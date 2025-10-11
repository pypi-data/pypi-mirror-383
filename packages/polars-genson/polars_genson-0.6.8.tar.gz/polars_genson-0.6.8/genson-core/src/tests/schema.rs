// genson-core/src/tests/schema.rs
use super::*;
use predicates::prelude::*;
use serde_json::json;

#[test]
fn test_reorder_unions_string_float_null() {
    // Unordered union: string, float, null
    let mut schema = json!({
        "type": ["string", "float", "null"]
    });

    reorder_unions(&mut schema);

    // After reordering, null should come first, then float/number, then string
    assert_eq!(
        schema,
        json!({
            "type": ["null", "float", "string"]
        })
    );
}

#[test]
fn test_basic_schema_inference() {
    let json_strings = vec![
        r#"{"name": "Alice", "age": 30}"#.to_string(),
        r#"{"name": "Bob", "age": 25, "city": "NYC"}"#.to_string(),
    ];

    let result = infer_json_schema_from_strings(&json_strings, SchemaInferenceConfig::default())
        .expect("Schema inference should succeed");

    // Test processed count
    assert_eq!(result.processed_count, 2);

    // Use predicates to test schema structure
    let schema_str = result.schema.to_string();

    predicate::str::contains("\"type\"")
        .and(predicate::str::contains("object"))
        .eval(&schema_str);

    predicate::str::contains("\"properties\"").eval(&schema_str);

    // Check that both name and age properties are present
    predicate::str::contains("\"name\"")
        .and(predicate::str::contains("\"age\""))
        .eval(&schema_str);

    println!(
        "✅ Generated schema: {}",
        serde_json::to_string_pretty(&result.schema).unwrap()
    );
}

#[test]
fn test_empty_input() {
    let json_strings = vec![];
    let result = infer_json_schema_from_strings(&json_strings, SchemaInferenceConfig::default());

    assert!(result.is_err());

    let error_msg = result.unwrap_err();
    predicate::str::contains("No JSON strings provided").eval(&error_msg);

    println!("✅ Empty input correctly rejected with: {}", error_msg);
}

#[test]
fn test_invalid_json_variants() {
    let test_cases = vec![
        (
            r#"{"name": "Alice"}"#,
            r#"{"invalid": json}"#,
            "unquoted value",
        ),
        (
            r#"{"valid": "json"}"#,
            r#"{"incomplete":"#,
            "incomplete string",
        ),
        (r#"{"good": "data"}"#, r#"{"trailing":,"#, "trailing comma"),
        (
            r#"{"working": true}"#,
            r#"{invalid: "json"}"#,
            "unquoted key",
        ),
        (
            r#"{"normal": "object"}"#,
            r#"{"nested": {"broken": json}}"#,
            "nested broken JSON",
        ),
    ];

    for (valid_json, invalid_json, description) in test_cases {
        println!("🧪 Testing: {}", description);
        println!("   Valid JSON: {}", valid_json);
        println!("   Invalid JSON: {}", invalid_json);

        let json_strings = vec![valid_json.to_string(), invalid_json.to_string()];

        let result =
            infer_json_schema_from_strings(&json_strings, SchemaInferenceConfig::default());

        // Should return an error instead of panicking
        assert!(result.is_err(), "Expected error for case: {}", description);

        let error_msg = result.unwrap_err();

        // Use predicates to verify error message content
        predicate::str::contains("Invalid JSON input at position").eval(&error_msg);

        // For short JSON strings, verify the content is included
        if invalid_json.len() <= MAX_JSON_ERROR_LENGTH {
            predicate::str::contains(invalid_json).eval(&error_msg);
        } else {
            // For long JSON, just check that truncation happened
            predicate::str::contains("truncated").eval(&error_msg);
        }

        // Ensure we don't have panic-related messages
        predicate::str::contains("panicked").not().eval(&error_msg);

        predicate::str::contains("SIGABRT").not().eval(&error_msg);

        println!("   ❌ Correctly failed with: {}", error_msg);
        println!();
    }
}

#[test]
fn test_mixed_valid_and_empty_strings() {
    let json_strings = vec![
        r#"{"name": "Alice", "age": 30}"#.to_string(),
        "".to_string(),    // Empty string should be skipped
        "   ".to_string(), // Whitespace-only should be skipped
        r#"{"name": "Bob", "age": 25}"#.to_string(),
    ];

    let result = infer_json_schema_from_strings(&json_strings, SchemaInferenceConfig::default())
        .expect("Should succeed with valid JSON, skipping empty strings");

    // Should process only the 2 valid JSON strings
    assert_eq!(result.processed_count, 2);

    let schema_str = result.schema.to_string();
    predicate::str::contains("\"name\"")
        .and(predicate::str::contains("\"age\""))
        .eval(&schema_str);

    println!(
        "✅ Processed {} valid strings, skipped empty ones",
        result.processed_count
    );
}

#[test]
fn test_schema_config_variations() {
    let json_strings = vec![r#"[{"item": "first"}, {"item": "second"}]"#.to_string()];

    // Test with ignore_outer_array = false
    let config_array = SchemaInferenceConfig {
        ignore_outer_array: false,
        ..Default::default()
    };

    let result = infer_json_schema_from_strings(&json_strings, config_array)
        .expect("Should handle array schema");

    let schema_str = result.schema.to_string();
    predicate::str::contains("\"type\"")
        .and(predicate::str::contains("array"))
        .eval(&schema_str);

    println!(
        "✅ Array schema: {}",
        serde_json::to_string_pretty(&result.schema).unwrap()
    );

    // Test with ignore_outer_array = true (default)
    let config_object = SchemaInferenceConfig {
        ignore_outer_array: true,
        ..Default::default()
    };

    let result = infer_json_schema_from_strings(&json_strings, config_object)
        .expect("Should handle object schema from array items");

    let schema_str = result.schema.to_string();
    predicate::str::contains("\"type\"")
        .and(predicate::str::contains("object"))
        .eval(&schema_str);

    predicate::str::contains("\"item\"").eval(&schema_str);

    println!(
        "✅ Object schema from array items: {}",
        serde_json::to_string_pretty(&result.schema).unwrap()
    );
}

#[test]
fn test_very_long_invalid_json() {
    // Create a very long invalid JSON string
    let long_value = "x".repeat(500); // 500 char string
    let long_invalid_json = format!(
        r#"{{"field1": "{}", "field2": "{}", "field3": "{}", "field4": "{}", "invalid_syntax": }}"#,
        long_value, long_value, long_value, long_value
    );

    let json_strings = vec![
        r#"{"valid": "json"}"#.to_string(),
        long_invalid_json.clone(),
    ];

    println!(
        "🧪 Testing very long invalid JSON ({} chars)",
        long_invalid_json.len()
    );

    let result = infer_json_schema_from_strings(&json_strings, SchemaInferenceConfig::default());

    assert!(result.is_err(), "Expected error for very long invalid JSON");

    let error_msg = result.unwrap_err();

    println!("The error message was: {}", error_msg);

    // Should contain truncation indicator
    predicate::str::contains("truncated").eval(&error_msg);

    // Should contain position information
    predicate::str::contains("Invalid JSON input at position 2").eval(&error_msg);

    // Error message should be reasonable length (much shorter than original JSON)
    assert!(
        error_msg.len() < long_invalid_json.len() / 2,
        "Error message should be much shorter than original JSON"
    );

    println!(
        "   ❌ Correctly truncated long JSON in error: {}",
        error_msg
    );

    // Verify the error message doesn't exceed a reasonable length
    assert!(
        error_msg.len() < 500,
        "Error message should be under 500 chars, got: {}",
        error_msg.len()
    );
}

#[test]
fn test_complex_nested_schema() {
    let json_strings = vec![
        json!({
            "user": {
                "id": 123,
                "profile": {
                    "name": "Alice",
                    "preferences": ["dark_mode", "notifications"]
                }
            },
            "metadata": {
                "created_at": "2024-01-01",
                "version": 1
            }
        })
        .to_string(),
        json!({
            "user": {
                "id": 456,
                "profile": {
                    "name": "Bob",
                    "preferences": ["light_mode"]
                }
            },
            "metadata": {
                "created_at": "2024-01-02",
                "version": 2
            }
        })
        .to_string(),
    ];

    let result = infer_json_schema_from_strings(&json_strings, SchemaInferenceConfig::default())
        .expect("Should handle complex nested schema");

    assert_eq!(result.processed_count, 2);

    let schema_str = result.schema.to_string();

    // Check for nested structure
    predicate::str::contains("\"user\"")
        .and(predicate::str::contains("\"metadata\""))
        .and(predicate::str::contains("\"profile\""))
        .and(predicate::str::contains("\"preferences\""))
        .eval(&schema_str);

    println!("✅ Complex nested schema generated successfully");
    println!(
        "Schema: {}",
        serde_json::to_string_pretty(&result.schema).unwrap()
    );
}

#[test]
fn test_ndjson_parsing() {
    // Two valid JSON objects separated by newlines (NDJSON format)
    let ndjson_input = r#"
{"name": "Alice", "age": 30}
{"name": "Bob", "age": 25, "city": "NYC"}
{"name": "Charlie"}
"#;

    let json_strings = vec![ndjson_input.to_string()];

    let config = SchemaInferenceConfig {
        delimiter: Some(b'\n'),
        ..Default::default()
    };

    let result = infer_json_schema_from_strings(&json_strings, config)
        .expect("NDJSON schema inference should succeed");

    // All 3 objects should be processed
    assert_eq!(result.processed_count, 1,
    "NDJSON should be counted as a single input string but parsed into multiple rows internally"
);

    let schema_str = result.schema.to_string();

    // The schema should include properties from all lines
    assert!(!schema_str.contains("Alice")); // values are not in schema
    assert!(schema_str.contains("\"name\""));
    assert!(schema_str.contains("\"age\""));
    assert!(schema_str.contains("\"city\""));

    println!(
        "✅ NDJSON schema generated: {}",
        serde_json::to_string_pretty(&result.schema).unwrap()
    );
}

#[test]
fn test_invalid_ndjson_line() {
    // Second line is malformed
    let ndjson_input = r#"
{"valid": true}
{"invalid": json}
{"also_valid": 123}
"#;

    let json_strings = vec![ndjson_input.to_string()];

    let config = SchemaInferenceConfig {
        delimiter: Some(b'\n'),
        ..Default::default()
    };

    let result = infer_json_schema_from_strings(&json_strings, config.clone());

    assert!(result.is_err(), "Expected error for malformed NDJSON line");

    let err_msg = result.unwrap_err();
    eprintln!("Got error: {}", err_msg);
    assert!(
        err_msg.contains("Invalid JSON input at index 1: expected value at line 1 column 13"),
        "Error message should report the failing line"
    );
    println!("✅ Correctly rejected malformed NDJSON: {}", err_msg);
}

/// Two objects with varying keys and homogeneous string values (low map threshold)
#[test]
fn test_map_threshold_rewrite() {
    let json_strings = vec![
        r#"{"labels": {"en": "Hello", "fr": "Bonjour"}}"#.to_string(),
        r#"{"labels": {"de": "Hallo", "es": "Hola"}}"#.to_string(),
    ];

    let config = SchemaInferenceConfig {
        map_threshold: 2,
        ..Default::default()
    };
    let result = infer_json_schema_from_strings(&json_strings, config).unwrap();

    let labels = &result.schema["properties"]["labels"];
    assert_eq!(labels["type"], "object");
    assert!(labels.get("additionalProperties").is_some());
    assert!(labels.get("properties").is_none());
}

/// Two objects with varying keys and homogeneous string values (default map threshold)
#[test]
fn test_map_threshold_as_record() {
    let json_strings = vec![
        r#"{"labels": {"en": "Hello", "fr": "Bonjour"}}"#.to_string(),
        r#"{"labels": {"de": "Hallo", "es": "Hola"}}"#.to_string(),
    ];

    let result =
        infer_json_schema_from_strings(&json_strings, SchemaInferenceConfig::default()).unwrap();

    let labels = &result.schema["properties"]["labels"];
    assert!(labels.get("properties").is_some());
    assert!(labels.get("additionalProperties").is_none());
}

#[test]
fn test_wrap_root_inserts_single_required_field() {
    let json_strings = vec![
        r#"{"en":{"language":"en","value":"Hello"},"fr":{"language":"fr","value":"Bonjour"}}"#
            .to_string(),
    ];

    let cfg = SchemaInferenceConfig {
        wrap_root: Some("labels".to_string()),
        ..Default::default()
    };

    let out = infer_json_schema_from_strings(&json_strings, cfg).unwrap();
    let sch = out.schema;

    assert_eq!(sch["type"], "object");
    assert_eq!(sch["required"], serde_json::json!(["labels"]));
    assert!(sch["properties"]["labels"].is_object());
}

#[test]
fn test_rewrite_objects_map_of_records() {
    use serde_json::json;

    // Schema that genson-rs would roughly emit for {"en": {...}, "fr": {...}}
    let mut schema = json!({
        "type": "object",
        "properties": {
            "en": {
                "type": "object",
                "properties": {
                    "language": { "type": "string" },
                    "value": { "type": "string" }
                },
                "required": ["language", "value"]
            },
            "fr": {
                "type": "object",
                "properties": {
                    "language": { "type": "string" },
                    "value": { "type": "string" }
                },
                "required": ["language", "value"]
            }
        },
        "required": ["en","fr"]
    });

    let cfg = SchemaInferenceConfig {
        map_threshold: 2, // force detection at 2 keys
        ..Default::default()
    };

    rewrite_objects(&mut schema, None, &cfg, true);

    println!("Generated schema:\n{}", schema);

    // After rewrite, we should have additionalProperties instead of fixed properties
    assert_eq!(schema["type"], "object");
    assert!(schema.get("properties").is_none());
    assert!(schema.get("required").is_none());

    // additionalProperties should carry the inner record shape
    let ap = schema
        .get("additionalProperties")
        .expect("should insert additionalProperties");

    assert_eq!(ap["type"], "object");
    assert_eq!(ap["properties"]["language"], json!({ "type": "string" }));
    assert_eq!(ap["properties"]["value"], json!({ "type": "string" }));
}

#[test]
fn test_map_of_strings_not_promoted_to_records() {
    let schema = json!({
        "type": "object",
        "properties": {
            "labels": {
                "type": "object",
                "properties": {
                    "en": { "type": "string" },
                    "fr": { "type": "string" }
                },
                "required": ["en", "fr"]
            }
        },
        "required": ["labels"]
    });

    let mut sch = schema.clone();
    let cfg = SchemaInferenceConfig {
        map_threshold: 2,
        ..Default::default()
    };
    rewrite_objects(&mut sch, None, &cfg, true);

    assert_eq!(
        sch["properties"]["labels"]["additionalProperties"]["type"],
        "string"
    );
}

#[test]
fn test_rewrite_objects_respects_map_max_required_keys() {
    let mut schema = json!({
        "type": "object",
        "properties": {
            "field1": {"type": "string"},
            "field2": {"type": "string"}
        },
        "required": ["field1", "field2"]
    });

    let config = SchemaInferenceConfig {
        map_threshold: 2,
        map_max_required_keys: Some(1), // Max 1 required key for maps
        ..Default::default()
    };

    rewrite_objects(&mut schema, None, &config, true);

    // Should remain as record because 2 required keys > 1
    assert_eq!(schema["type"], "object");
    assert!(schema.get("properties").is_some());
    assert!(schema.get("additionalProperties").is_none());
}

#[test]
fn test_rewrite_objects_allows_map_with_few_required_keys() {
    let mut schema = json!({
        "type": "object",
        "properties": {
            "field1": {"type": "string"},
            "field2": {"type": "string"}
        },
        "required": ["field1"] // Only 1 required key
    });

    let config = SchemaInferenceConfig {
        map_threshold: 2,
        no_root_map: false,
        map_max_required_keys: Some(1), // Max 1 required key for maps
        ..Default::default()
    };

    rewrite_objects(&mut schema, None, &config, true);

    // Should become map because 1 required key ≤ 1
    assert_eq!(schema["type"], "object");
    assert!(schema.get("additionalProperties").is_some());
    assert!(schema.get("properties").is_none());
}

#[test]
fn test_rewrite_objects_none_max_required_keys_preserves_behavior() {
    let mut schema = json!({
        "type": "object",
        "properties": {
            "field1": {"type": "string"},
            "field2": {"type": "string"},
            "field3": {"type": "string"}
        },
        "required": ["field1", "field2", "field3"]
    });

    let config = SchemaInferenceConfig {
        map_threshold: 2,
        map_max_required_keys: None, // No gating
        no_root_map: false,
        ..Default::default()
    };

    rewrite_objects(&mut schema, None, &config, true);

    // Should become map because None means no gating (old behavior)
    assert_eq!(schema["type"], "object");
    assert!(schema.get("additionalProperties").is_some());
    assert!(schema.get("properties").is_none());
}

#[test]
fn test_rewrite_objects_zero_max_required_keys() {
    let mut schema = json!({
        "type": "object",
        "properties": {
            "field1": {"type": "string"},
            "field2": {"type": "string"}
        },
        "required": ["field1"]
    });

    let config = SchemaInferenceConfig {
        map_threshold: 2,
        map_max_required_keys: Some(0), // Only allow maps with 0 required keys
        ..Default::default()
    };

    rewrite_objects(&mut schema, None, &config, true);

    // Should remain as record because 1 required key > 0
    assert_eq!(schema["type"], "object");
    assert!(schema.get("properties").is_some());
    assert!(schema.get("additionalProperties").is_none());
}

#[test]
fn test_rewrite_objects_zero_required_keys_allowed() {
    let mut schema = json!({
        "type": "object",
        "properties": {
            "field1": {"type": "string"},
            "field2": {"type": "string"}
        }
        // No required array = 0 required keys
    });

    let config = SchemaInferenceConfig {
        map_threshold: 2,
        map_max_required_keys: Some(0), // Only allow maps with 0 required keys
        no_root_map: false,
        ..Default::default()
    };

    rewrite_objects(&mut schema, None, &config, true);

    // Should become map because 0 required keys ≤ 0
    assert_eq!(schema["type"], "object");
    assert!(schema.get("additionalProperties").is_some());
    assert!(schema.get("properties").is_none());
}

#[test]
fn test_force_scalar_promotion() {
    let json_strings = vec![
        r#"{"precision": 11}"#.to_string(),
        r#"{"precision": 12}"#.to_string(),
    ];

    let mut force_promo = std::collections::HashSet::new();
    force_promo.insert("precision".to_string());

    let config = SchemaInferenceConfig {
        force_scalar_promotion: force_promo,
        ..Default::default()
    };

    let result = infer_json_schema_from_strings(&json_strings, config)
        .expect("Schema inference should succeed");

    let schema = &result.schema;
    let precision_schema = &schema["properties"]["precision"];

    eprintln!("Got the schema: {}", precision_schema);

    // Should be an object with promoted scalar keys, not just a scalar type
    assert_eq!(precision_schema["type"], "object");
    assert!(precision_schema["properties"].is_object());
    
    // Should have both integer and number wrapped forms
    let props = precision_schema["properties"].as_object().unwrap();
    assert!(props.contains_key("precision__integer"));
    
    println!("✅ Force scalar promotion created wrapped fields: {:?}", props.keys());
}

#[test]
fn test_force_scalar_promotion_with_unify_maps() {
    // Reproduces bug where precision field loses scalar promotion when:
    // 1. Multiple fields are promoted (datavalue, precision)
    // 2. unify_maps is enabled
    // 3. map_threshold is low (causing properties to become maps)
    let json_strings = vec![
        r#"{"P646":[{"references":[{"P577":[{"datavalue":{"time":"+2013-10-28T00:00:00Z","precision":11}}]}]}]}"#.to_string(),
        r#"{"P646":[{"references":[{"P577":[{"datavalue":{"time":"+2013-10-28T00:00:00Z","precision":11}}]}]}]}"#.to_string(),
    ];

    let mut force_promo = std::collections::HashSet::new();
    force_promo.insert("datavalue".to_string());
    force_promo.insert("precision".to_string());

    let config = SchemaInferenceConfig {
        force_scalar_promotion: force_promo,
        unify_maps: true,
        map_threshold: 0,
        wrap_root: Some("claims".to_string()),
        ..Default::default()
    };

    let result = infer_json_schema_from_strings(&json_strings, config)
        .expect("Schema inference should succeed");

    let schema_str = serde_json::to_string_pretty(&result.schema).unwrap();
    eprintln!("Full schema:\n{}", schema_str);

    // Bug: precision should reference the promoted type "precision__integer"
    // but instead shows plain "int"
    assert!(
        schema_str.contains("precision__integer"),
        "Schema should contain precision__integer type reference. \
         Bug: precision field shows 'int' instead of 'precision__integer' when \
         force_scalar_promotion is combined with unify_maps.\n\
         Schema: {}",
        schema_str
    );

    println!("✅ Force scalar promotion correctly applied with unify_maps");
}

#[test]
fn test_force_scalar_promotion_nested_in_maps() {
    // Reproduces bug where precision field in deeply nested maps doesn't get promoted
    // Even though it's in force_scalar_promotion, it remains as plain int
    let json_strings = vec![
        r#"{"P646":[{"references":[{"P577":[{"datavalue":{"precision":11}}]}]}],"P937":[{"references":[{"P143":[{"datavalue":{"labels":{"en":"German Wikipedia"}}}]}]}]}"#.to_string(),
        r#"{"P646":[{"references":[{"P577":[{"datavalue":{"precision":11}}]}]}]}"#.to_string(),
    ];

    let mut force_promo = std::collections::HashSet::new();
    force_promo.insert("datavalue".to_string());
    force_promo.insert("precision".to_string());

    let config = SchemaInferenceConfig {
        force_scalar_promotion: force_promo,
        unify_maps: true,
        map_threshold: 0,
        wrap_root: Some("claims".to_string()),
        ..Default::default()
    };

    let result = infer_json_schema_from_strings(&json_strings, config)
        .expect("Schema inference should succeed");

    let schema_str = serde_json::to_string_pretty(&result.schema).unwrap();
    eprintln!("Full schema:\n{}", schema_str);

    // Bug: precision should be promoted to precision__integer even in deeply nested maps
    assert!(
        schema_str.contains("precision__integer"),
        "Schema should contain precision__integer type reference. \
         Bug: precision field in nested maps is not promoted despite being in force_scalar_promotion.\n\
         Schema: {}",
        schema_str
    );

    println!("✅ Force scalar promotion applied to fields nested in maps");
}

#[test]
fn test_rewrite_objects_force_override_wins() {
    let mut schema = json!({
        "type": "object",
        "properties": {
            "field1": {"type": "string"},
            "field2": {"type": "string"}
        },
        "required": ["field1", "field2"]
    });

    let mut force_types = std::collections::HashMap::new();
    force_types.insert("test_field".to_string(), "map".to_string());

    let config = SchemaInferenceConfig {
        map_threshold: 2,
        map_max_required_keys: Some(0), // Would normally block this
        force_field_types: force_types,
        ..Default::default()
    };

    // Apply with field name that matches force override
    rewrite_objects(&mut schema, Some("test_field"), &config, true);

    // Should become map despite having required keys due to force override
    assert_eq!(schema["type"], "object");
    assert!(schema.get("additionalProperties").is_some());
    assert!(schema.get("properties").is_none());
}

#[test]
fn test_rewrite_objects_non_homogeneous_values_not_rewritten() {
    let mut schema = json!({
        "type": "object",
        "properties": {
            "field1": {"type": "string"},
            "field2": {"type": "integer"} // Non-homogeneous
        },
        "required": []
    });

    let config = SchemaInferenceConfig {
        map_threshold: 2,
        map_max_required_keys: Some(5), // Would allow this
        ..Default::default()
    };

    rewrite_objects(&mut schema, None, &config, true);

    // Should remain as record because values are not homogeneous
    assert_eq!(schema["type"], "object");
    assert!(schema.get("properties").is_some());
    assert!(schema.get("additionalProperties").is_none());
}

#[test]
fn test_rewrite_objects_below_threshold_not_rewritten() {
    let mut schema = json!({
        "type": "object",
        "properties": {
            "field1": {"type": "string"}
        },
        "required": []
    });

    let config = SchemaInferenceConfig {
        map_threshold: 5,               // Above the key count
        map_max_required_keys: Some(5), // Would allow this
        ..Default::default()
    };

    rewrite_objects(&mut schema, None, &config, true);

    // Should remain as record because below threshold
    assert_eq!(schema["type"], "object");
    assert!(schema.get("properties").is_some());
    assert!(schema.get("additionalProperties").is_none());
}

#[test]
fn test_map_max_required_keys_with_wrap_root() {
    let json_strings = vec![
        r#"{"en":{"language":"en","value":"Hello"},"fr":{"language":"fr","value":"Bonjour"}}"#
            .to_string(),
    ];

    let cfg = SchemaInferenceConfig {
        wrap_root: Some("labels".to_string()),
        map_threshold: 2,
        map_max_required_keys: Some(1), // Should allow the wrapped content
        ..Default::default()
    };

    let out = infer_json_schema_from_strings(&json_strings, cfg).unwrap();
    let sch = out.schema;

    assert_eq!(sch["type"], "object");
    assert_eq!(sch["required"], serde_json::json!(["labels"]));

    // The wrapped labels should have the map logic applied
    let labels_content = &sch["properties"]["labels"];
    assert!(labels_content.is_object());

    println!("✅ map_max_required_keys works with wrap_root");
}

#[test]
fn test_wrap_scalars_in_map_of_records() {
    let json_strings = vec![
        // "root" field is a map, all map keys have a record{id,value},
        // for map keys A/B value is a record{hello} and for map key C value is a string
        // Row 1: value is an object
        r#"{"root": {"A": {"id": 1, "value": {"hello": "world"}}}}"#.to_string(),
        // Row 2: value is an object, again
        r#"{"root": {"B": {"id": 2, "value": {"hello": "foo"}}}}"#.to_string(),
        // Row 3: value is just a string
        r#"{"root": {"C": {"id": 3, "value": "bar"}}}"#.to_string(),
    ];

    let cfg = SchemaInferenceConfig {
        map_threshold: 3,
        map_max_required_keys: Some(0),
        unify_maps: true,
        wrap_scalars: true,
        ..Default::default()
    };

    let result = infer_json_schema_from_strings(&json_strings, cfg)
        .expect("Schema inference should succeed with wrap_scalars");

    let sch = result.schema;

    // Navigate to root map’s value type
    let root_additional = &sch["properties"]["root"]["additionalProperties"];
    assert_eq!(root_additional["type"], "object");

    // The "value" field should be promoted and contain both object and scalar string form
    let value_schema = &root_additional["properties"]["value"];
    assert!(value_schema.is_object());

    // Should contain the synthetic key for the wrapped scalar
    assert!(
        value_schema["properties"]
            .as_object()
            .unwrap()
            .keys()
            .any(|k| k.contains("__string")),
        "Expected synthetic scalar wrapper key inside value schema, got: {}",
        serde_json::to_string_pretty(value_schema).unwrap()
    );

    println!(
        "✅ wrap_scalars promoted scalar inside map-of-records: {}",
        serde_json::to_string_pretty(value_schema).unwrap()
    );
}

#[test]
fn test_no_root_map_prevents_root_becoming_map() {
    let mut schema = json!({
        "type": "object",
        "properties": {
            "field1": {"type": "string"},
            "field2": {"type": "string"},
            "field3": {"type": "string"}
        },
        "required": []
    });

    let config = SchemaInferenceConfig {
        map_threshold: 2,           // Would normally trigger map inference
        no_root_map: true,         // But this should prevent it
        ..Default::default()
    };

    rewrite_objects(&mut schema, None, &config, true);

    // Should remain as record despite meeting map criteria
    assert_eq!(schema["type"], "object");
    assert!(schema.get("properties").is_some());
    assert!(schema.get("additionalProperties").is_none());

    println!("✅ no_root_map=true prevented root from becoming map");
}

#[test]
fn test_no_root_map_false_allows_root_becoming_map() {
    let mut schema = json!({
        "type": "object",
        "properties": {
            "field1": {"type": "string"},
            "field2": {"type": "string"},
            "field3": {"type": "string"}
        },
        "required": []
    });

    let config = SchemaInferenceConfig {
        map_threshold: 2,           // Should trigger map inference
        no_root_map: false,        // Explicitly allow root maps
        ..Default::default()
    };

    rewrite_objects(&mut schema, None, &config, true);

    // Should become map because no_root_map=false allows it
    assert_eq!(schema["type"], "object");
    assert!(schema.get("additionalProperties").is_some());
    assert!(schema.get("properties").is_none());

    println!("✅ no_root_map=false allowed root to become map");
}

#[test]
#[ignore]
fn test_schema_field_order_determinism() {
    // Use actual data similar to your claims fixture
    let json_string = r#"{"P31":[{"mainsnak":{"property":"P31","datavalue":{"id":"Q15632617"},"datatype":"wikibase-item"},"rank":"normal"}],"P40":[{"mainsnak":{"property":"P40","datavalue":{"id":"Q1049347"},"datatype":"wikibase-item"},"rank":"normal"}],"P27":[{"mainsnak":{"property":"P27","datavalue":{"id":"Q30"},"datatype":"wikibase-item"},"rank":"normal"}],"P345":[{"mainsnak":{"property":"P345","datavalue":"ch0009881","datatype":"external-id"},"rank":"deprecated"}],"P108":[{"mainsnak":{"property":"P108","datavalue":{"id":"Q2944031"},"datatype":"wikibase-item"},"rank":"normal"}],"P463":[{"mainsnak":{"property":"P463","datavalue":{"id":"Q209114"},"datatype":"wikibase-item"},"rank":"normal"}],"P569":[{"mainsnak":{"property":"P569","datavalue":{"time":"+1966-02-18T00:00:00Z","timezone":0,"before":0,"after":0,"precision":11,"calendarmodel":"http://www.wikidata.org/entity/Q1985727"},"datatype":"time"},"rank":"normal"}],"P451":[{"mainsnak":{"property":"P451","datavalue":{"id":"Q284262"},"datatype":"wikibase-item"},"rank":"normal"}],"P19":[{"mainsnak":{"property":"P19","datavalue":{"id":"Q47164"},"datatype":"wikibase-item"},"rank":"normal"}],"P22":[{"mainsnak":{"property":"P22","datavalue":{"id":"Q3322144"},"datatype":"wikibase-item"},"rank":"normal"}],"P166":[{"mainsnak":{"property":"P166","datavalue":{"id":"Q852071"},"datatype":"wikibase-item"},"rank":"normal"}],"P410":[{"mainsnak":{"property":"P410","datavalue":{"id":"Q19100"},"datatype":"wikibase-item"},"rank":"normal"}],"P26":[{"mainsnak":{"property":"P26","datavalue":{"id":"Q1095612"},"datatype":"wikibase-item"},"rank":"normal"}],"P512":[{"mainsnak":{"property":"P512","datavalue":{"id":"Q1765120"},"datatype":"wikibase-item"},"rank":"normal"}],"P106":[{"mainsnak":{"property":"P106","datavalue":{"id":"Q5446967"},"datatype":"wikibase-item"},"rank":"normal"}],"P21":[{"mainsnak":{"property":"P21","datavalue":{"id":"Q6581097"},"datatype":"wikibase-item"},"rank":"normal"}],"P646":[{"mainsnak":{"property":"P646","datavalue":"/m/022jzf","datatype":"external-id"},"rank":"normal"}],"P18":[{"mainsnak":{"property":"P18","datavalue":"Kiefer Sutherland at 24 Redemption premiere 1 (headshot).jpg","datatype":"commonsMedia"},"rank":"normal"}],"P1441":[{"mainsnak":{"property":"P1441","datavalue":{"id":"Q56194"},"datatype":"wikibase-item"},"rank":"normal"}],"P1448":[{"mainsnak":{"property":"P1448","datavalue":{"text":"Jack Bauer","language":"en"},"datatype":"monolingualtext"},"rank":"normal"}],"P3373":[{"mainsnak":{"property":"P3373","datavalue":{"id":"Q10290844"},"datatype":"wikibase-item"},"rank":"normal"}],"P3417":[{"mainsnak":{"property":"P3417","datavalue":"Jack-Bauer","datatype":"external-id"},"rank":"normal"}],"P4839":[{"mainsnak":{"property":"P4839","datavalue":"Entity[\"FictionalCharacter\", \"JackBauer\"]","datatype":"external-id"},"rank":"normal"}],"P175":[{"mainsnak":{"property":"P175","datavalue":{"id":"Q103946"},"datatype":"wikibase-item"},"rank":"normal"}],"P1412":[{"mainsnak":{"property":"P1412","datavalue":{"id":"Q1860"},"datatype":"wikibase-item"},"rank":"normal"}],"P1417":[{"mainsnak":{"property":"P1417","datavalue":"topic/Jack-Bauer","datatype":"external-id"},"rank":"normal"}],"P5800":[{"mainsnak":{"property":"P5800","datavalue":{"id":"Q215972"},"datatype":"wikibase-item"},"rank":"normal"}],"P6262":[{"mainsnak":{"property":"P6262","datavalue":"24:Jack_Bauer","datatype":"external-id"},"rank":"normal"}],"P570":[{"mainsnak":{"property":"P570","datatype":"time"},"rank":"normal"}],"P2581":[{"mainsnak":{"property":"P2581","datavalue":"03111055n","datatype":"external-id"},"rank":"normal"}],"P10291":[{"mainsnak":{"property":"P10291","datavalue":"12819","datatype":"external-id"},"rank":"normal"}],"P10757":[{"mainsnak":{"property":"P10757","datavalue":"170","datatype":"external-id"},"rank":"normal"}],"P3553":[{"mainsnak":{"property":"P3553","datavalue":"19959170","datatype":"external-id"},"rank":"normal"}]}"#;

    let config = SchemaInferenceConfig {
        map_threshold: 0,
        unify_maps: true,
        wrap_root: Some("claims".to_string()),
        delimiter: Some(b'\n'),
        ..Default::default()
    };

    // Run inference multiple times
    let mut all_keys = Vec::new();
    let result = infer_json_schema_from_strings(&[json_string.to_string()], config.clone())
        .expect("Schema inference should succeed");

    // Navigate to datavalue.properties, handling both Avro and non-Avro schema shapes
    let datavalue_props = &result.schema["properties"]["claims"]["additionalProperties"]
        ["items"]["properties"]["mainsnak"]["properties"]["datavalue"]["properties"];

    if let Some(props) = datavalue_props.as_object() {
        let keys: Vec<String> = props.keys().cloned().collect();
        eprintln!("Run keys: {:?}", keys);
        all_keys.push(keys);
    } else {
        panic!(
            "datavalue_props was not an object: {:?}",
            datavalue_props
        );
    }

    assert!(
        !all_keys.is_empty(),
        "No key vectors collected — datavalue_props was not an object in any run"
    );

    let first = &all_keys[0];
    let first_key = &first[0];
    assert_eq!(first_key, "id");
}

// #[test]
// #[ignore]
// fn test_builder_to_schema_determinism() {
//     let json_string = r#"{"P31":[{"mainsnak":{"property":"P31","datavalue":{"id":"Q15632617"},"datatype":"wikibase-item"},"rank":"normal"}],"P40":[{"mainsnak":{"property":"P40","datavalue":{"id":"Q1049347"},"datatype":"wikibase-item"},"rank":"normal"}],"P27":[{"mainsnak":{"property":"P27","datavalue":{"id":"Q30"},"datatype":"wikibase-item"},"rank":"normal"}],"P345":[{"mainsnak":{"property":"P345","datavalue":"ch0009881","datatype":"external-id"},"rank":"deprecated"}],"P108":[{"mainsnak":{"property":"P108","datavalue":{"id":"Q2944031"},"datatype":"wikibase-item"},"rank":"normal"}],"P463":[{"mainsnak":{"property":"P463","datavalue":{"id":"Q209114"},"datatype":"wikibase-item"},"rank":"normal"}],"P569":[{"mainsnak":{"property":"P569","datavalue":{"time":"+1966-02-18T00:00:00Z","timezone":0,"before":0,"after":0,"precision":11,"calendarmodel":"http://www.wikidata.org/entity/Q1985727"},"datatype":"time"},"rank":"normal"}],"P451":[{"mainsnak":{"property":"P451","datavalue":{"id":"Q284262"},"datatype":"wikibase-item"},"rank":"normal"}],"P19":[{"mainsnak":{"property":"P19","datavalue":{"id":"Q47164"},"datatype":"wikibase-item"},"rank":"normal"}],"P22":[{"mainsnak":{"property":"P22","datavalue":{"id":"Q3322144"},"datatype":"wikibase-item"},"rank":"normal"}],"P166":[{"mainsnak":{"property":"P166","datavalue":{"id":"Q852071"},"datatype":"wikibase-item"},"rank":"normal"}],"P410":[{"mainsnak":{"property":"P410","datavalue":{"id":"Q19100"},"datatype":"wikibase-item"},"rank":"normal"}],"P26":[{"mainsnak":{"property":"P26","datavalue":{"id":"Q1095612"},"datatype":"wikibase-item"},"rank":"normal"}],"P512":[{"mainsnak":{"property":"P512","datavalue":{"id":"Q1765120"},"datatype":"wikibase-item"},"rank":"normal"}],"P106":[{"mainsnak":{"property":"P106","datavalue":{"id":"Q5446967"},"datatype":"wikibase-item"},"rank":"normal"}],"P21":[{"mainsnak":{"property":"P21","datavalue":{"id":"Q6581097"},"datatype":"wikibase-item"},"rank":"normal"}],"P646":[{"mainsnak":{"property":"P646","datavalue":"/m/022jzf","datatype":"external-id"},"rank":"normal"}],"P18":[{"mainsnak":{"property":"P18","datavalue":"Kiefer Sutherland at 24 Redemption premiere 1 (headshot).jpg","datatype":"commonsMedia"},"rank":"normal"}],"P1441":[{"mainsnak":{"property":"P1441","datavalue":{"id":"Q56194"},"datatype":"wikibase-item"},"rank":"normal"}],"P1448":[{"mainsnak":{"property":"P1448","datavalue":{"text":"Jack Bauer","language":"en"},"datatype":"monolingualtext"},"rank":"normal"}],"P3373":[{"mainsnak":{"property":"P3373","datavalue":{"id":"Q10290844"},"datatype":"wikibase-item"},"rank":"normal"}],"P3417":[{"mainsnak":{"property":"P3417","datavalue":"Jack-Bauer","datatype":"external-id"},"rank":"normal"}],"P4839":[{"mainsnak":{"property":"P4839","datavalue":"Entity[\"FictionalCharacter\", \"JackBauer\"]","datatype":"external-id"},"rank":"normal"}],"P175":[{"mainsnak":{"property":"P175","datavalue":{"id":"Q103946"},"datatype":"wikibase-item"},"rank":"normal"}],"P1412":[{"mainsnak":{"property":"P1412","datavalue":{"id":"Q1860"},"datatype":"wikibase-item"},"rank":"normal"}],"P1417":[{"mainsnak":{"property":"P1417","datavalue":"topic/Jack-Bauer","datatype":"external-id"},"rank":"normal"}],"P5800":[{"mainsnak":{"property":"P5800","datavalue":{"id":"Q215972"},"datatype":"wikibase-item"},"rank":"normal"}],"P6262":[{"mainsnak":{"property":"P6262","datavalue":"24:Jack_Bauer","datatype":"external-id"},"rank":"normal"}],"P570":[{"mainsnak":{"property":"P570","datatype":"time"},"rank":"normal"}],"P2581":[{"mainsnak":{"property":"P2581","datavalue":"03111055n","datatype":"external-id"},"rank":"normal"}],"P10291":[{"mainsnak":{"property":"P10291","datavalue":"12819","datatype":"external-id"},"rank":"normal"}],"P10757":[{"mainsnak":{"property":"P10757","datavalue":"170","datatype":"external-id"},"rank":"normal"}],"P3553":[{"mainsnak":{"property":"P3553","datavalue":"19959170","datatype":"external-id"},"rank":"normal"}]}"#;
// 
//     let config = SchemaInferenceConfig {
//         delimiter: Some(b'\n'),
//         ..Default::default()
//     };
// 
//     let mut builder = get_builder(config.schema_uri.as_deref());
//     
//     process_json_strings_sequential(&[json_string.to_string()], &config, &mut builder)
//         .expect("Processing should succeed");
//     
//     let schema = builder.to_schema();
//     
//     let schema_props = &schema["properties"];
//     
//     if let Some(props) = schema_props.as_object() {
//         let keys: Vec<String> = props.keys().cloned().collect();
//         eprintln!("properties keys (count={}): {:?}", keys.len(), keys);
//         eprintln!("First key: {}", keys[0]);
//         assert_eq!(keys[0], "P31", "Expected first key to be P31");
//     } else {
//         eprintln!("properties: {:?}", schema_props);
//         panic!("properties was not an object");
//     }
// }

// #[test]
// #[ignore]
// fn test_build_json_schema_determinism() {
//     let json_string = r#"{"P31":[{"mainsnak":{"property":"P31","datavalue":{"id":"Q15632617"},"datatype":"wikibase-item"},"rank":"normal"}],"P40":[{"mainsnak":{"property":"P40","datavalue":{"id":"Q1049347"},"datatype":"wikibase-item"},"rank":"normal"}],"P27":[{"mainsnak":{"property":"P27","datavalue":{"id":"Q30"},"datatype":"wikibase-item"},"rank":"normal"}],"P345":[{"mainsnak":{"property":"P345","datavalue":"ch0009881","datatype":"external-id"},"rank":"deprecated"}],"P108":[{"mainsnak":{"property":"P108","datavalue":{"id":"Q2944031"},"datatype":"wikibase-item"},"rank":"normal"}],"P463":[{"mainsnak":{"property":"P463","datavalue":{"id":"Q209114"},"datatype":"wikibase-item"},"rank":"normal"}],"P569":[{"mainsnak":{"property":"P569","datavalue":{"time":"+1966-02-18T00:00:00Z","timezone":0,"before":0,"after":0,"precision":11,"calendarmodel":"http://www.wikidata.org/entity/Q1985727"},"datatype":"time"},"rank":"normal"}],"P451":[{"mainsnak":{"property":"P451","datavalue":{"id":"Q284262"},"datatype":"wikibase-item"},"rank":"normal"}],"P19":[{"mainsnak":{"property":"P19","datavalue":{"id":"Q47164"},"datatype":"wikibase-item"},"rank":"normal"}],"P22":[{"mainsnak":{"property":"P22","datavalue":{"id":"Q3322144"},"datatype":"wikibase-item"},"rank":"normal"}],"P166":[{"mainsnak":{"property":"P166","datavalue":{"id":"Q852071"},"datatype":"wikibase-item"},"rank":"normal"}],"P410":[{"mainsnak":{"property":"P410","datavalue":{"id":"Q19100"},"datatype":"wikibase-item"},"rank":"normal"}],"P26":[{"mainsnak":{"property":"P26","datavalue":{"id":"Q1095612"},"datatype":"wikibase-item"},"rank":"normal"}],"P512":[{"mainsnak":{"property":"P512","datavalue":{"id":"Q1765120"},"datatype":"wikibase-item"},"rank":"normal"}],"P106":[{"mainsnak":{"property":"P106","datavalue":{"id":"Q5446967"},"datatype":"wikibase-item"},"rank":"normal"}],"P21":[{"mainsnak":{"property":"P21","datavalue":{"id":"Q6581097"},"datatype":"wikibase-item"},"rank":"normal"}],"P646":[{"mainsnak":{"property":"P646","datavalue":"/m/022jzf","datatype":"external-id"},"rank":"normal"}],"P18":[{"mainsnak":{"property":"P18","datavalue":"Kiefer Sutherland at 24 Redemption premiere 1 (headshot).jpg","datatype":"commonsMedia"},"rank":"normal"}],"P1441":[{"mainsnak":{"property":"P1441","datavalue":{"id":"Q56194"},"datatype":"wikibase-item"},"rank":"normal"}],"P1448":[{"mainsnak":{"property":"P1448","datavalue":{"text":"Jack Bauer","language":"en"},"datatype":"monolingualtext"},"rank":"normal"}],"P3373":[{"mainsnak":{"property":"P3373","datavalue":{"id":"Q10290844"},"datatype":"wikibase-item"},"rank":"normal"}],"P3417":[{"mainsnak":{"property":"P3417","datavalue":"Jack-Bauer","datatype":"external-id"},"rank":"normal"}],"P4839":[{"mainsnak":{"property":"P4839","datavalue":"Entity[\"FictionalCharacter\", \"JackBauer\"]","datatype":"external-id"},"rank":"normal"}],"P175":[{"mainsnak":{"property":"P175","datavalue":{"id":"Q103946"},"datatype":"wikibase-item"},"rank":"normal"}],"P1412":[{"mainsnak":{"property":"P1412","datavalue":{"id":"Q1860"},"datatype":"wikibase-item"},"rank":"normal"}],"P1417":[{"mainsnak":{"property":"P1417","datavalue":"topic/Jack-Bauer","datatype":"external-id"},"rank":"normal"}],"P5800":[{"mainsnak":{"property":"P5800","datavalue":{"id":"Q215972"},"datatype":"wikibase-item"},"rank":"normal"}],"P6262":[{"mainsnak":{"property":"P6262","datavalue":"24:Jack_Bauer","datatype":"external-id"},"rank":"normal"}],"P570":[{"mainsnak":{"property":"P570","datatype":"time"},"rank":"normal"}],"P2581":[{"mainsnak":{"property":"P2581","datavalue":"03111055n","datatype":"external-id"},"rank":"normal"}],"P10291":[{"mainsnak":{"property":"P10291","datavalue":"12819","datatype":"external-id"},"rank":"normal"}],"P10757":[{"mainsnak":{"property":"P10757","datavalue":"170","datatype":"external-id"},"rank":"normal"}],"P3553":[{"mainsnak":{"property":"P3553","datavalue":"19959170","datatype":"external-id"},"rank":"normal"}]}"#;
// 
//     let config = SchemaInferenceConfig {
//         delimiter: Some(b'\n'),
//         ..Default::default()
//     };
// 
//     let build_config = BuildConfig {
//         delimiter: config.delimiter,
//         ignore_outer_array: config.ignore_outer_array,
//     };
// 
//     let mut builder = get_builder(None);
// 
//     let prepared_json = prepare_json_bytes(json_string.as_bytes(), 0, &config)
//         .expect("Preparation should succeed");
// 
//     let mut bytes = prepared_json.into_owned();
// 
//     build_json_schema(&mut builder, &mut bytes, &build_config);
// 
//     let schema = builder.to_schema();
// 
//     let schema_props = &schema["properties"];
// 
//     if let Some(props) = schema_props.as_object() {
//         let keys: Vec<String> = props.keys().cloned().collect();
//         eprintln!("properties keys (count={}): {:?}", keys.len(), keys);
//         eprintln!("First key: {}", keys[0]);
//         assert_eq!(keys[0], "P31", "Expected first key to be P31");
//     } else {
//         panic!("properties was not an object");
//     }
// }

// #[test]
// #[ignore]
// fn test_build_genson_rs_builder_determinism() {
//     let json_string = r#"{"P31":[{"mainsnak":{"property":"P31","datavalue":{"id":"Q15632617"},"datatype":"wikibase-item"},"rank":"normal"}],"P40":[{"mainsnak":{"property":"P40","datavalue":{"id":"Q1049347"},"datatype":"wikibase-item"},"rank":"normal"}],"P27":[{"mainsnak":{"property":"P27","datavalue":{"id":"Q30"},"datatype":"wikibase-item"},"rank":"normal"}],"P345":[{"mainsnak":{"property":"P345","datavalue":"ch0009881","datatype":"external-id"},"rank":"deprecated"}],"P108":[{"mainsnak":{"property":"P108","datavalue":{"id":"Q2944031"},"datatype":"wikibase-item"},"rank":"normal"}],"P463":[{"mainsnak":{"property":"P463","datavalue":{"id":"Q209114"},"datatype":"wikibase-item"},"rank":"normal"}],"P569":[{"mainsnak":{"property":"P569","datavalue":{"time":"+1966-02-18T00:00:00Z","timezone":0,"before":0,"after":0,"precision":11,"calendarmodel":"http://www.wikidata.org/entity/Q1985727"},"datatype":"time"},"rank":"normal"}],"P451":[{"mainsnak":{"property":"P451","datavalue":{"id":"Q284262"},"datatype":"wikibase-item"},"rank":"normal"}],"P19":[{"mainsnak":{"property":"P19","datavalue":{"id":"Q47164"},"datatype":"wikibase-item"},"rank":"normal"}],"P22":[{"mainsnak":{"property":"P22","datavalue":{"id":"Q3322144"},"datatype":"wikibase-item"},"rank":"normal"}],"P166":[{"mainsnak":{"property":"P166","datavalue":{"id":"Q852071"},"datatype":"wikibase-item"},"rank":"normal"}],"P410":[{"mainsnak":{"property":"P410","datavalue":{"id":"Q19100"},"datatype":"wikibase-item"},"rank":"normal"}],"P26":[{"mainsnak":{"property":"P26","datavalue":{"id":"Q1095612"},"datatype":"wikibase-item"},"rank":"normal"}],"P512":[{"mainsnak":{"property":"P512","datavalue":{"id":"Q1765120"},"datatype":"wikibase-item"},"rank":"normal"}],"P106":[{"mainsnak":{"property":"P106","datavalue":{"id":"Q5446967"},"datatype":"wikibase-item"},"rank":"normal"}],"P21":[{"mainsnak":{"property":"P21","datavalue":{"id":"Q6581097"},"datatype":"wikibase-item"},"rank":"normal"}],"P646":[{"mainsnak":{"property":"P646","datavalue":"/m/022jzf","datatype":"external-id"},"rank":"normal"}],"P18":[{"mainsnak":{"property":"P18","datavalue":"Kiefer Sutherland at 24 Redemption premiere 1 (headshot).jpg","datatype":"commonsMedia"},"rank":"normal"}],"P1441":[{"mainsnak":{"property":"P1441","datavalue":{"id":"Q56194"},"datatype":"wikibase-item"},"rank":"normal"}],"P1448":[{"mainsnak":{"property":"P1448","datavalue":{"text":"Jack Bauer","language":"en"},"datatype":"monolingualtext"},"rank":"normal"}],"P3373":[{"mainsnak":{"property":"P3373","datavalue":{"id":"Q10290844"},"datatype":"wikibase-item"},"rank":"normal"}],"P3417":[{"mainsnak":{"property":"P3417","datavalue":"Jack-Bauer","datatype":"external-id"},"rank":"normal"}],"P4839":[{"mainsnak":{"property":"P4839","datavalue":"Entity[\"FictionalCharacter\", \"JackBauer\"]","datatype":"external-id"},"rank":"normal"}],"P175":[{"mainsnak":{"property":"P175","datavalue":{"id":"Q103946"},"datatype":"wikibase-item"},"rank":"normal"}],"P1412":[{"mainsnak":{"property":"P1412","datavalue":{"id":"Q1860"},"datatype":"wikibase-item"},"rank":"normal"}],"P1417":[{"mainsnak":{"property":"P1417","datavalue":"topic/Jack-Bauer","datatype":"external-id"},"rank":"normal"}],"P5800":[{"mainsnak":{"property":"P5800","datavalue":{"id":"Q215972"},"datatype":"wikibase-item"},"rank":"normal"}],"P6262":[{"mainsnak":{"property":"P6262","datavalue":"24:Jack_Bauer","datatype":"external-id"},"rank":"normal"}],"P570":[{"mainsnak":{"property":"P570","datatype":"time"},"rank":"normal"}],"P2581":[{"mainsnak":{"property":"P2581","datavalue":"03111055n","datatype":"external-id"},"rank":"normal"}],"P10291":[{"mainsnak":{"property":"P10291","datavalue":"12819","datatype":"external-id"},"rank":"normal"}],"P10757":[{"mainsnak":{"property":"P10757","datavalue":"170","datatype":"external-id"},"rank":"normal"}],"P3553":[{"mainsnak":{"property":"P3553","datavalue":"19959170","datatype":"external-id"},"rank":"normal"}]}"#;
// 
//     let mut builder = get_builder(None);
//     
//     // Parse and add the object directly
//     let mut bytes = json_string.as_bytes().to_vec();
//     let object = simd_json::to_borrowed_value(&mut bytes).unwrap();
//     builder.add_object(&object);
// 
//     let schema = builder.to_schema();
// 
//     let schema_props = &schema["properties"];
// 
//     if let Some(props) = schema_props.as_object() {
//         let keys: Vec<String> = props.keys().cloned().collect();
//         eprintln!("properties keys (count={}): {:?}", keys.len(), keys);
//         eprintln!("First key: {}", keys[0]);
//         assert_eq!(keys[0], "P31", "Expected first key to be P31");
//     } else {
//         panic!("properties was not an object");
//     }
// }

// #[test]
// #[ignore]
// fn test_add_object_determinism() {
//     let json_string = r#"{"P31":[{"mainsnak":{"property":"P31","datavalue":{"id":"Q15632617"},"datatype":"wikibase-item"},"rank":"normal"}],"P40":[{"mainsnak":{"property":"P40","datavalue":{"id":"Q1049347"},"datatype":"wikibase-item"},"rank":"normal"}],"P27":[{"mainsnak":{"property":"P27","datavalue":{"id":"Q30"},"datatype":"wikibase-item"},"rank":"normal"}],"P345":[{"mainsnak":{"property":"P345","datavalue":"ch0009881","datatype":"external-id"},"rank":"deprecated"}],"P108":[{"mainsnak":{"property":"P108","datavalue":{"id":"Q2944031"},"datatype":"wikibase-item"},"rank":"normal"}],"P463":[{"mainsnak":{"property":"P463","datavalue":{"id":"Q209114"},"datatype":"wikibase-item"},"rank":"normal"}],"P569":[{"mainsnak":{"property":"P569","datavalue":{"time":"+1966-02-18T00:00:00Z","timezone":0,"before":0,"after":0,"precision":11,"calendarmodel":"http://www.wikidata.org/entity/Q1985727"},"datatype":"time"},"rank":"normal"}],"P451":[{"mainsnak":{"property":"P451","datavalue":{"id":"Q284262"},"datatype":"wikibase-item"},"rank":"normal"}],"P19":[{"mainsnak":{"property":"P19","datavalue":{"id":"Q47164"},"datatype":"wikibase-item"},"rank":"normal"}],"P22":[{"mainsnak":{"property":"P22","datavalue":{"id":"Q3322144"},"datatype":"wikibase-item"},"rank":"normal"}],"P166":[{"mainsnak":{"property":"P166","datavalue":{"id":"Q852071"},"datatype":"wikibase-item"},"rank":"normal"}],"P410":[{"mainsnak":{"property":"P410","datavalue":{"id":"Q19100"},"datatype":"wikibase-item"},"rank":"normal"}],"P26":[{"mainsnak":{"property":"P26","datavalue":{"id":"Q1095612"},"datatype":"wikibase-item"},"rank":"normal"}],"P512":[{"mainsnak":{"property":"P512","datavalue":{"id":"Q1765120"},"datatype":"wikibase-item"},"rank":"normal"}],"P106":[{"mainsnak":{"property":"P106","datavalue":{"id":"Q5446967"},"datatype":"wikibase-item"},"rank":"normal"}],"P21":[{"mainsnak":{"property":"P21","datavalue":{"id":"Q6581097"},"datatype":"wikibase-item"},"rank":"normal"}],"P646":[{"mainsnak":{"property":"P646","datavalue":"/m/022jzf","datatype":"external-id"},"rank":"normal"}],"P18":[{"mainsnak":{"property":"P18","datavalue":"Kiefer Sutherland at 24 Redemption premiere 1 (headshot).jpg","datatype":"commonsMedia"},"rank":"normal"}],"P1441":[{"mainsnak":{"property":"P1441","datavalue":{"id":"Q56194"},"datatype":"wikibase-item"},"rank":"normal"}],"P1448":[{"mainsnak":{"property":"P1448","datavalue":{"text":"Jack Bauer","language":"en"},"datatype":"monolingualtext"},"rank":"normal"}],"P3373":[{"mainsnak":{"property":"P3373","datavalue":{"id":"Q10290844"},"datatype":"wikibase-item"},"rank":"normal"}],"P3417":[{"mainsnak":{"property":"P3417","datavalue":"Jack-Bauer","datatype":"external-id"},"rank":"normal"}],"P4839":[{"mainsnak":{"property":"P4839","datavalue":"Entity[\"FictionalCharacter\", \"JackBauer\"]","datatype":"external-id"},"rank":"normal"}],"P175":[{"mainsnak":{"property":"P175","datavalue":{"id":"Q103946"},"datatype":"wikibase-item"},"rank":"normal"}],"P1412":[{"mainsnak":{"property":"P1412","datavalue":{"id":"Q1860"},"datatype":"wikibase-item"},"rank":"normal"}],"P1417":[{"mainsnak":{"property":"P1417","datavalue":"topic/Jack-Bauer","datatype":"external-id"},"rank":"normal"}],"P5800":[{"mainsnak":{"property":"P5800","datavalue":{"id":"Q215972"},"datatype":"wikibase-item"},"rank":"normal"}],"P6262":[{"mainsnak":{"property":"P6262","datavalue":"24:Jack_Bauer","datatype":"external-id"},"rank":"normal"}],"P570":[{"mainsnak":{"property":"P570","datatype":"time"},"rank":"normal"}],"P2581":[{"mainsnak":{"property":"P2581","datavalue":"03111055n","datatype":"external-id"},"rank":"normal"}],"P10291":[{"mainsnak":{"property":"P10291","datavalue":"12819","datatype":"external-id"},"rank":"normal"}],"P10757":[{"mainsnak":{"property":"P10757","datavalue":"170","datatype":"external-id"},"rank":"normal"}],"P3553":[{"mainsnak":{"property":"P3553","datavalue":"19959170","datatype":"external-id"},"rank":"normal"}]}"#;
//     
//     let mut builder = get_builder(None);
// 
//     let mut bytes = json_string.as_bytes().to_vec();
//     let object = simd_json::to_borrowed_value(&mut bytes).unwrap();
//     builder.add_object(&object);
// 
//     // Introspect BEFORE calling to_schema
//     // Access the root_node's active_strategies
//     let root_node = &builder.root_node;
//     eprintln!("Number of strategies: {}", root_node.active_strategies.len());
// 
//     if let Some(crate::genson_rs::strategy::BasicSchemaStrategy::Object(obj_strategy)) = root_node.active_strategies.first() {
//         let keys: Vec<String> = obj_strategy.properties.keys().cloned().collect();
//         eprintln!("properties keys after add_object (count={}): {:?}", keys.len(), keys);
//         eprintln!("First key: {}", keys[0]);
//         assert_eq!(keys[0], "P31", "Expected first key to be P31");
//     } else {
//         panic!("No object strategy found");
//     }
// }

#[test]
#[ignore]
fn test_simd_json_iteration_determinism() {
    let json_string = r#"{"P31":[{"mainsnak":{"property":"P31","datavalue":{"id":"Q15632617"},"datatype":"wikibase-item"},"rank":"normal"}],"P40":[{"mainsnak":{"property":"P40","datavalue":{"id":"Q1049347"},"datatype":"wikibase-item"},"rank":"normal"}],"P27":[{"mainsnak":{"property":"P27","datavalue":{"id":"Q30"},"datatype":"wikibase-item"},"rank":"normal"}],"P345":[{"mainsnak":{"property":"P345","datavalue":"ch0009881","datatype":"external-id"},"rank":"deprecated"}],"P108":[{"mainsnak":{"property":"P108","datavalue":{"id":"Q2944031"},"datatype":"wikibase-item"},"rank":"normal"}],"P463":[{"mainsnak":{"property":"P463","datavalue":{"id":"Q209114"},"datatype":"wikibase-item"},"rank":"normal"}],"P569":[{"mainsnak":{"property":"P569","datavalue":{"time":"+1966-02-18T00:00:00Z","timezone":0,"before":0,"after":0,"precision":11,"calendarmodel":"http://www.wikidata.org/entity/Q1985727"},"datatype":"time"},"rank":"normal"}],"P451":[{"mainsnak":{"property":"P451","datavalue":{"id":"Q284262"},"datatype":"wikibase-item"},"rank":"normal"}],"P19":[{"mainsnak":{"property":"P19","datavalue":{"id":"Q47164"},"datatype":"wikibase-item"},"rank":"normal"}],"P22":[{"mainsnak":{"property":"P22","datavalue":{"id":"Q3322144"},"datatype":"wikibase-item"},"rank":"normal"}],"P166":[{"mainsnak":{"property":"P166","datavalue":{"id":"Q852071"},"datatype":"wikibase-item"},"rank":"normal"}],"P410":[{"mainsnak":{"property":"P410","datavalue":{"id":"Q19100"},"datatype":"wikibase-item"},"rank":"normal"}],"P26":[{"mainsnak":{"property":"P26","datavalue":{"id":"Q1095612"},"datatype":"wikibase-item"},"rank":"normal"}],"P512":[{"mainsnak":{"property":"P512","datavalue":{"id":"Q1765120"},"datatype":"wikibase-item"},"rank":"normal"}],"P106":[{"mainsnak":{"property":"P106","datavalue":{"id":"Q5446967"},"datatype":"wikibase-item"},"rank":"normal"}],"P21":[{"mainsnak":{"property":"P21","datavalue":{"id":"Q6581097"},"datatype":"wikibase-item"},"rank":"normal"}],"P646":[{"mainsnak":{"property":"P646","datavalue":"/m/022jzf","datatype":"external-id"},"rank":"normal"}],"P18":[{"mainsnak":{"property":"P18","datavalue":"Kiefer Sutherland at 24 Redemption premiere 1 (headshot).jpg","datatype":"commonsMedia"},"rank":"normal"}],"P1441":[{"mainsnak":{"property":"P1441","datavalue":{"id":"Q56194"},"datatype":"wikibase-item"},"rank":"normal"}],"P1448":[{"mainsnak":{"property":"P1448","datavalue":{"text":"Jack Bauer","language":"en"},"datatype":"monolingualtext"},"rank":"normal"}],"P3373":[{"mainsnak":{"property":"P3373","datavalue":{"id":"Q10290844"},"datatype":"wikibase-item"},"rank":"normal"}],"P3417":[{"mainsnak":{"property":"P3417","datavalue":"Jack-Bauer","datatype":"external-id"},"rank":"normal"}],"P4839":[{"mainsnak":{"property":"P4839","datavalue":"Entity[\"FictionalCharacter\", \"JackBauer\"]","datatype":"external-id"},"rank":"normal"}],"P175":[{"mainsnak":{"property":"P175","datavalue":{"id":"Q103946"},"datatype":"wikibase-item"},"rank":"normal"}],"P1412":[{"mainsnak":{"property":"P1412","datavalue":{"id":"Q1860"},"datatype":"wikibase-item"},"rank":"normal"}],"P1417":[{"mainsnak":{"property":"P1417","datavalue":"topic/Jack-Bauer","datatype":"external-id"},"rank":"normal"}],"P5800":[{"mainsnak":{"property":"P5800","datavalue":{"id":"Q215972"},"datatype":"wikibase-item"},"rank":"normal"}],"P6262":[{"mainsnak":{"property":"P6262","datavalue":"24:Jack_Bauer","datatype":"external-id"},"rank":"normal"}],"P570":[{"mainsnak":{"property":"P570","datatype":"time"},"rank":"normal"}],"P2581":[{"mainsnak":{"property":"P2581","datavalue":"03111055n","datatype":"external-id"},"rank":"normal"}],"P10291":[{"mainsnak":{"property":"P10291","datavalue":"12819","datatype":"external-id"},"rank":"normal"}],"P10757":[{"mainsnak":{"property":"P10757","datavalue":"170","datatype":"external-id"},"rank":"normal"}],"P3553":[{"mainsnak":{"property":"P3553","datavalue":"19959170","datatype":"external-id"},"rank":"normal"}]}"#;

    let mut bytes = json_string.as_bytes().to_vec();
    let object = simd_json::to_borrowed_value(&mut bytes).unwrap();

    if let simd_json::BorrowedValue::Object(obj) = object {
        let keys: Vec<String> = obj.iter().map(|(k, _)| k.to_string()).collect();
        eprintln!("simd_json object keys (count={}): {:?}", keys.len(), keys);
        eprintln!("First key: {}", keys[0]);
        assert_eq!(keys[0], "P31", "Expected first key to be P31");
    } else {
        panic!("Not an object");
    }
}
