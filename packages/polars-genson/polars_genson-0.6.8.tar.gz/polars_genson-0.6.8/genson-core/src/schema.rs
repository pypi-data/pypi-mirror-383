use crate::genson_rs::{build_json_schema, get_builder, BuildConfig};
use crate::{debug, profile, profile_verbose};
use rayon::prelude::*;
use serde::de::Error as DeError;
use serde::Deserialize;
use serde_json::{json, Value};
use std::borrow::Cow;
use std::collections::HashSet;
use std::panic::{self, AssertUnwindSafe};
use std::time::{SystemTime, UNIX_EPOCH};
use xxhash_rust::xxh64::xxh64;

use crate::genson_rs::SchemaBuilder;

pub(crate) mod core;
pub use core::*;
mod map_inference;
use map_inference::*;

/// Maximum length of JSON string to include in error messages before truncating
const MAX_JSON_ERROR_LENGTH: usize = 100;
/// Threshold for switching to parallel processing. Below this, use sequential.
const PARALLEL_THRESHOLD: usize = 10;

/// Get current RSS memory usage in bytes
pub(crate) fn get_rss_bytes() -> Option<usize> {
    let status = std::fs::read_to_string("/proc/self/status").ok()?;
    for line in status.lines() {
        if line.starts_with("VmRSS:") {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() >= 2 {
                let kb: usize = parts[1].parse().ok()?;
                return Some(kb * 1024); // Convert KB to bytes
            }
        }
    }
    None
}

/// Format bytes to human-readable string
pub(crate) fn format_bytes(bytes: usize) -> String {
    const MB: usize = 1024 * 1024;
    const GB: usize = 1024 * 1024 * 1024;

    if bytes >= GB {
        format!("{:.2} GB", bytes as f64 / GB as f64)
    } else if bytes >= MB {
        format!("{:.2} MB", bytes as f64 / MB as f64)
    } else {
        format!("{:.2} KB", bytes as f64 / 1024.0)
    }
}

fn current_time_hms() -> String {
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();

    let total_seconds = now.as_secs() % 86_400; // seconds in a day
    let hours = total_seconds / 3600;
    let minutes = (total_seconds % 3600) / 60;
    let seconds = (total_seconds % 60) as f64 + now.subsec_millis() as f64 / 1000.0; // add fractional part

    format!("{:02}:{:02}:{:04.1}", hours, minutes, seconds)
}

fn validate_json(s: &str) -> Result<(), serde_json::Error> {
    let mut de = serde_json::Deserializer::from_str(s);
    serde::de::IgnoredAny::deserialize(&mut de)?; // lightweight: ignores the parsed value
    de.end()
}

fn validate_ndjson(s: &str) -> Result<(), serde_json::Error> {
    for line in s.lines() {
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }
        validate_json(trimmed)?; // propagate serde_json::Error
    }
    Ok(())
}

/// Recursively reorder union type arrays in a JSON Schema by canonical precedence.
///
/// Special case: preserves the common `["null", T]` pattern without reordering.
pub fn reorder_unions(schema: &mut Value) {
    match schema {
        Value::Object(obj) => {
            if let Some(Value::Array(types)) = obj.get_mut("type") {
                // sort by canonical precedence, but keep ["null", T] pattern intact
                if !(types.len() == 2 && types.iter().any(|t| t == "null")) {
                    types.sort_by_key(type_rank);
                }
            }
            // recurse into properties/items/etc.
            for v in obj.values_mut() {
                reorder_unions(v);
            }
        }
        Value::Array(arr) => {
            // Parallelize across array elements (if large enough)
            if arr.len() >= PARALLEL_THRESHOLD {
                arr.par_iter_mut().for_each(reorder_unions);
            } else {
                for v in arr {
                    reorder_unions(v);
                }
            }
        }
        _ => {}
    }
}

/// Assign a numeric precedence rank to a JSON Schema type.
///
/// Used by `reorder_unions` to sort union members deterministically.
/// - Null always first
/// - Containers before scalars (to enforce widening)
/// - Scalars ordered by narrowness
/// - Unknown types last
pub fn type_rank(val: &Value) -> usize {
    match val {
        Value::String(s) => type_string_rank(s),
        Value::Object(obj) => {
            if let Some(Value::String(t)) = obj.get("type") {
                type_string_rank(t)
            } else {
                100 // object with no "type" field
            }
        }
        _ => 100, // non-string/non-object
    }
}

/// Internal helper: rank by type string
fn type_string_rank(s: &str) -> usize {
    match s {
        // Null always first
        "null" => 0,

        // Containers before scalars: widening takes precedence
        "map" => 1,
        "array" => 2,
        "object" | "record" => 3,

        // Scalars (ordered by 'narrowness')
        "boolean" => 10,
        "integer" | "int" | "long" => 11,
        "number" | "float" | "double" => 12,
        "enum" => 13,
        "string" => 14,
        "fixed" => 15,
        "bytes" => 16,

        // Fallback
        _ => 99,
    }
}

/// Prepare JSON bytes for schema building (validation + wrap_root transformation)
fn prepare_json_bytes<'a>(
    json_bytes: &'a [u8],
    index: usize,
    config: &SchemaInferenceConfig,
) -> Result<Cow<'a, [u8]>, String> {
    // Early return for empty input
    let json_str = std::str::from_utf8(json_bytes)
        .map_err(|e| format!("Invalid UTF-8 at index {}: {}", index + 1, e))?;

    if json_str.trim().is_empty() {
        return Ok(Cow::Borrowed(&[]));
    }

    // Choose validation strategy based on delimiter
    let validation_result = if let Some(delim) = config.delimiter {
        if delim == b'\n' {
            validate_ndjson(json_str)
        } else {
            Err(serde_json::Error::custom(format!(
                "Unsupported delimiter: {:?}",
                delim
            )))
        }
    } else {
        validate_json(json_str)
    };

    if let Err(parse_error) = validation_result {
        let truncated_json = if json_str.len() > MAX_JSON_ERROR_LENGTH {
            format!(
                "{}... [truncated {} chars]",
                &json_str[..MAX_JSON_ERROR_LENGTH],
                json_str.len() - MAX_JSON_ERROR_LENGTH
            )
        } else {
            json_str.to_string()
        };

        return Err(format!(
            "Invalid JSON input at index {}: {} - JSON: {}",
            index + 1,
            parse_error,
            truncated_json
        ));
    }

    // Safe: JSON is valid, now hand off to genson-rs
    if let Some(ref field) = config.wrap_root {
        if config.delimiter == Some(b'\n') {
            // NDJSON: wrap each line separately
            let mut wrapped_bytes = Vec::new();
            for line in json_str.lines() {
                let trimmed = line.trim();
                if trimmed.is_empty() {
                    continue;
                }
                let inner_val: Value = serde_json::from_str(trimmed)
                    .map_err(|e| format!("Failed to parse NDJSON line before wrap_root: {}", e))?;

                if !wrapped_bytes.is_empty() {
                    wrapped_bytes.push(b'\n');
                }
                serde_json::to_writer(&mut wrapped_bytes, &json!({ field: inner_val }))
                    .map_err(|e| format!("Failed to serialize wrapped NDJSON: {}", e))?;
            }
            Ok(Cow::Owned(wrapped_bytes))
        } else {
            // Single JSON doc
            let inner_val: Value = serde_json::from_str(json_str)
                .map_err(|e| format!("Failed to parse JSON before wrap_root: {}", e))?;
            let wrapped_bytes = serde_json::to_vec(&json!({ field: inner_val }))
                .map_err(|e| format!("Failed to serialize wrapped JSON: {}", e))?;
            Ok(Cow::Owned(wrapped_bytes))
        }
    } else {
        // No wrapping needed - just borrow the original bytes
        Ok(Cow::Borrowed(json_bytes))
    }
}

/// Process all JSON strings sequentially and build schemas
fn process_json_strings_sequential(
    json_strings: &[String],
    config: &SchemaInferenceConfig,
    builder: &mut crate::genson_rs::SchemaBuilder,
) -> Result<usize, String> {
    let build_config = BuildConfig {
        delimiter: config.delimiter,
        ignore_outer_array: config.ignore_outer_array,
    };

    let mut processed_count = 0;

    // Process each JSON string
    for (i, json_str) in json_strings.iter().enumerate() {
        profile_verbose!(config, "PROCESSING JSON STRING {}", i);

        let prep_start = std::time::Instant::now();
        let prepared_json = prepare_json_bytes(json_str.as_bytes(), i, config)?;
        let prep_elapsed = prep_start.elapsed();
        profile_verbose!(config, "  Preparation took: {:?}", prep_elapsed);

        if prepared_json.is_empty() {
            continue;
        }

        let mut bytes = prepared_json.into_owned(); // Only allocate if Cow::Owned

        // Build schema incrementally - this is where panics happen
        let build_start = std::time::Instant::now();
        let _schema = build_json_schema(builder, &mut bytes, &build_config);
        let build_elapsed = build_start.elapsed();
        profile_verbose!(config, "  Schema building took: {:?}", build_elapsed);

        processed_count += 1;
    }

    Ok(processed_count)
}

/// Process all JSON strings in parallel while maintaining order
fn process_json_strings_parallel(
    json_strings: &[String],
    config: &SchemaInferenceConfig,
    builder: &mut SchemaBuilder,
) -> Result<usize, String> {
    profile!(
        config,
        "Starting parallel preparation and building ({})",
        current_time_hms()
    );

    // Process in chunks to limit peak memory
    let chunk_size = config.max_builders.unwrap_or(json_strings.len());

    if config.profile {
        if let Some(rss) = get_rss_bytes() {
            anstream::eprintln!("📊 RSS before parallel processing: {}", format_bytes(rss));
        }
    }

    let mut processed_count = 0;
    let mut seen_hashes = HashSet::new();

    for (chunk_idx, chunk) in json_strings.chunks(chunk_size).enumerate() {
        profile!(
            config,
            "Processing chunk {} ({} strings)",
            chunk_idx,
            chunk.len()
        );

        if config.profile {
            if let Some(rss) = get_rss_bytes() {
                anstream::eprintln!("📊 RSS before chunk {}: {}", chunk_idx, format_bytes(rss));
            }
        }

        let chunk_builders: Vec<(usize, SchemaBuilder, bool)> = chunk
            .par_iter()
            .enumerate()
            .map(
                |(i, json_str)| -> Result<(usize, SchemaBuilder, bool), String> {
                    profile_verbose!(config, "Thread processing JSON STRING {}", i);

                    let prep_start = std::time::Instant::now();
                    let prepared = prepare_json_bytes(json_str.as_bytes(), i, config)?;
                    let prep_elapsed = prep_start.elapsed();
                    profile_verbose!(
                        config,
                        "  String {} preparation took: {:?}",
                        i,
                        prep_elapsed
                    );

                    if prepared.is_empty() {
                        return Ok((i, get_builder(config.schema_uri.as_deref()), false));
                    }

                    let mut chunk_builder = get_builder(config.schema_uri.as_deref());
                    let mut bytes = prepared.into_owned();
                    let chunk_build_config = BuildConfig {
                        delimiter: config.delimiter,
                        ignore_outer_array: config.ignore_outer_array,
                    };

                    let build_start = std::time::Instant::now();
                    build_json_schema(&mut chunk_builder, &mut bytes, &chunk_build_config);
                    let build_elapsed = build_start.elapsed();
                    profile_verbose!(
                        config,
                        "  String {} schema building took: {:?}",
                        i,
                        build_elapsed
                    );

                    Ok((i, chunk_builder, true))
                },
            )
            .collect::<Result<Vec<_>, String>>()?;

        if config.profile {
            if let Some(rss) = get_rss_bytes() {
                anstream::eprintln!("📊 RSS after collecting chunk: {}", format_bytes(rss));
            }
        }

        // Extract and merge schemas from this chunk
        for (_i, individual_builder, was_non_empty) in chunk_builders {
            if !was_non_empty {
                continue;
            }

            let schema = individual_builder.to_schema();
            let hash = xxh64(schema.to_string().as_bytes(), 0);

            if !seen_hashes.insert(hash) {
                continue;
            }

            processed_count += 1;
            builder.add_schema(schema);
        }

        if config.profile {
            if let Some(rss) = get_rss_bytes() {
                anstream::eprintln!("📊 RSS after merging chunk: {}", format_bytes(rss));
            }
        }
    }

    profile!(config, "All chunks processed ({})", current_time_hms());

    Ok(processed_count)
}

/// Infer JSON schema from a collection of JSON strings
pub fn infer_json_schema_from_strings(
    json_strings: &[String],
    config: SchemaInferenceConfig,
) -> Result<SchemaInferenceResult, String> {
    profile!(
        config,
        "Processing {} strings ({})",
        json_strings.len(),
        current_time_hms()
    );
    debug!(config, "Schema inference config: {:#?}", config);
    if json_strings.is_empty() {
        return Err("No JSON strings provided".to_string());
    }

    // Wrap the entire genson-rs interaction in panic handling
    let result = panic::catch_unwind(AssertUnwindSafe(
        || -> Result<SchemaInferenceResult, String> {
            // Create schema builder
            let mut builder = get_builder(config.schema_uri.as_deref());

            profile!(config, "Starting preparation loop ({})", current_time_hms());

            let use_parallel = std::env::var("GENSON_PARALLEL")
                .map(|v| v == "1" || v.to_lowercase() == "true")
                .unwrap_or_else(|_| json_strings.len() >= PARALLEL_THRESHOLD);

            let processed_count = if use_parallel {
                process_json_strings_parallel(json_strings, &config, &mut builder)?
            } else {
                process_json_strings_sequential(json_strings, &config, &mut builder)?
            };

            // Get final schema
            let mut final_schema = builder.to_schema();
            profile!(config, "Rewriting objects ({})", current_time_hms());
            rewrite_objects(&mut final_schema, None, &config, true);
            profile!(config, "Reordering unions ({})", current_time_hms());
            reorder_unions(&mut final_schema);

            #[cfg(feature = "avro")]
            if config.avro {
                let avro_schema = SchemaInferenceResult {
                    schema: final_schema.clone(),
                    processed_count,
                }
                .to_avro_schema(
                    "genson", // namespace
                    Some(""),
                    Some(""), // base_uri
                    false,    // don't split top-level
                );
                return Ok(SchemaInferenceResult {
                    schema: avro_schema,
                    processed_count,
                });
            }

            Ok(SchemaInferenceResult {
                schema: final_schema,
                processed_count,
            })
        },
    ));

    // Handle the result of panic::catch_unwind
    match result {
        Ok(Ok(schema_result)) => Ok(schema_result),
        Ok(Err(e)) => Err(e),
        Err(_panic) => Err("JSON schema inference failed due to invalid JSON input".to_string()),
    }
}

#[cfg(test)]
mod tests {
    include!("tests/schema.rs");
}
