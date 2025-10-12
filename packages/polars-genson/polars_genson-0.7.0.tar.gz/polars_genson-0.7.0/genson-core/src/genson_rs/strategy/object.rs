use ordermap::OrderMap;
use regex::Regex;
use std::collections::hash_set::HashSet;

use rayon::prelude::*;
use serde_json::{json, Map, Value};
use simd_json;
use simd_json::prelude::TypedObjectValue;

use crate::genson_rs::node::{DataType, SchemaNode};
use crate::genson_rs::strategy::base::SchemaStrategy;

#[derive(Debug, PartialEq)]
pub struct ObjectStrategy {
    // TODO: this is redeclared everywhere, how to avoid this?
    extra_keywords: Value,
    properties: OrderMap<String, SchemaNode>,
    pattern_properties: OrderMap<String, SchemaNode>,
    required_properties: Option<HashSet<String>>,
    include_empty_required: bool,
}

impl ObjectStrategy {
    pub fn new() -> Self {
        ObjectStrategy {
            extra_keywords: json!({}),
            properties: OrderMap::new(),
            pattern_properties: OrderMap::new(),
            required_properties: None,
            include_empty_required: false,
        }
    }
}

impl SchemaStrategy for ObjectStrategy {
    fn get_extra_keywords_mut(&mut self) -> &mut Value {
        &mut self.extra_keywords
    }

    fn get_extra_keywords(&self) -> &Value {
        &self.extra_keywords
    }

    fn match_schema(schema: &Value) -> bool {
        schema["type"] == "object"
    }

    fn match_object(object: &simd_json::BorrowedValue) -> bool {
        object.is_object()
    }

    fn add_object(&mut self, object: &simd_json::BorrowedValue) {
        let mut properties = HashSet::new();
        if let simd_json::BorrowedValue::Object(object) = object {
            object.iter().for_each(|(prop, subobj)| {
                let mut pattern: Option<&str> = None;
                if !self.properties.contains_key(prop.as_ref()) {
                    let pattern_matcher = |p: &str| Regex::new(p).unwrap().is_match(prop);
                    if let Some((p, node)) = self
                        .pattern_properties
                        .iter_mut()
                        .find(|(p, _)| pattern_matcher(p))
                    {
                        pattern = Some(p);
                        node.add_object(DataType::Object(subobj));
                    }
                }

                if pattern.is_none() {
                    properties.insert(prop.to_string());
                    if !self.properties.contains_key(prop.as_ref()) {
                        self.properties.insert(prop.to_string(), SchemaNode::new());
                    }
                    self.properties
                        .get_mut(prop.as_ref())
                        .unwrap()
                        .add_object(DataType::Object(subobj));
                }
            });
        }

        if self.required_properties.is_none() {
            self.required_properties = Some(properties);
        } else {
            // take the intersection
            self.required_properties
                .as_mut()
                .unwrap()
                .retain(|p| properties.contains(p));
        }
    }

    fn add_schema(&mut self, schema: &Value) {
        if let Value::Object(schema_object) = schema {
            self.add_extra_keywords(schema);

            // properties updater updates the internal properties and pattern_properties with the schema_object,
            // creating schema node as needed for each property
            let properties_updater = |properties: &mut OrderMap<String, SchemaNode>,
                                      schema_object: &Map<String, Value>,
                                      prop_key: &str| {
                if let Some(schema_properties) = schema_object[prop_key].as_object() {
                    schema_properties.iter().for_each(|(prop, sub_schema)| {
                        let sub_node = properties.entry(prop.to_string()).or_default();
                        sub_node.add_schema(DataType::Schema(sub_schema));
                    });
                }
            };

            if schema_object.contains_key("properties") {
                properties_updater(&mut self.properties, schema_object, "properties");
            }
            if schema_object.contains_key("patternProperties") {
                properties_updater(
                    &mut self.pattern_properties,
                    schema_object,
                    "patternProperties",
                );
            }
            if schema_object.contains_key("required") {
                if let Value::Array(required_fields) = &schema_object["required"] {
                    if required_fields.is_empty() {
                        // if the input schema object has required fields being empty, that means
                        // including empty required fields in the schema is the desired behavior
                        // and should be followed
                        self.include_empty_required = true;
                    }
                    if self.required_properties.is_none() {
                        let required_fields_set: HashSet<String> = required_fields
                            .iter()
                            .map(|v| v.as_str().unwrap().to_string())
                            .collect();
                        self.required_properties = Some(required_fields_set);
                    } else {
                        // take the intersection
                        self.required_properties
                            .as_mut()
                            .unwrap()
                            .retain(|p| required_fields.contains(&Value::String(p.to_string())));
                    }
                }
            }
        } else {
            panic!("Invalid schema type - must be a valid JSON object")
        }
    }

    /// Optimized batch schema merging for objects
    /// Collects all properties from all schemas first, then merges each property once
    fn add_schemas(&mut self, schemas: &[&Value]) {
        // Phase 1: Collect all properties and required sets from all schemas
        let mut property_groups: OrderMap<String, Vec<&Value>> = OrderMap::new();
        let mut pattern_property_groups: OrderMap<String, Vec<&Value>> = OrderMap::new();
        let mut all_required_sets: Vec<HashSet<String>> = Vec::new();

        for schema in schemas {
            if let Value::Object(schema_obj) = schema {
                self.add_extra_keywords(schema);

                // Collect regular properties
                if let Some(Value::Object(props)) = schema_obj.get("properties") {
                    for (prop_name, sub_schema) in props {
                        property_groups
                            .entry(prop_name.clone())
                            .or_default()
                            .push(sub_schema);
                    }
                }

                // Collect pattern properties
                if let Some(Value::Object(patterns)) = schema_obj.get("patternProperties") {
                    for (pattern, sub_schema) in patterns {
                        pattern_property_groups
                            .entry(pattern.clone())
                            .or_default()
                            .push(sub_schema);
                    }
                }

                // Collect required fields
                if let Some(Value::Array(required)) = schema_obj.get("required") {
                    if required.is_empty() {
                        self.include_empty_required = true;
                    }
                    let required_set: HashSet<String> = required
                        .iter()
                        .filter_map(|v| v.as_str().map(String::from))
                        .collect();
                    all_required_sets.push(required_set);
                }
            }
        }

        // Phase 2: Merge properties in parallel if there are enough properties
        if property_groups.len() > 3 {
            let merged_properties: Vec<(String, SchemaNode)> = property_groups
                .into_par_iter()
                .map(|(prop_name, sub_schemas)| {
                    let mut node = SchemaNode::new();
                    // Batch add all schemas for this property
                    let schema_values: Vec<Value> =
                        sub_schemas.iter().map(|&s| s.clone()).collect();
                    node.add_schemas(&schema_values);
                    (prop_name, node)
                })
                .collect();

            // Insert merged properties back
            for (prop_name, node) in merged_properties {
                self.properties.insert(prop_name, node);
            }
        } else {
            // Sequential for small property counts
            for (prop_name, sub_schemas) in property_groups {
                let node = self.properties.entry(prop_name).or_default();

                let schema_values: Vec<Value> = sub_schemas.iter().map(|&s| s.clone()).collect();
                node.add_schemas(&schema_values);
            }
        }

        // Phase 3: Merge pattern properties (usually few, so sequential is fine)
        for (pattern, sub_schemas) in pattern_property_groups {
            let node = self.pattern_properties.entry(pattern).or_default();

            let schema_values: Vec<Value> = sub_schemas.iter().map(|&s| s.clone()).collect();
            node.add_schemas(&schema_values);
        }

        // Phase 4: Merge required fields (intersection of all sets)
        if !all_required_sets.is_empty() {
            let final_required = all_required_sets
                .into_iter()
                .reduce(|acc, set| acc.intersection(&set).cloned().collect())
                .unwrap_or_default();

            if self.required_properties.is_none() {
                self.required_properties = Some(final_required);
            } else {
                self.required_properties
                    .as_mut()
                    .unwrap()
                    .retain(|p| final_required.contains(p));
            }
        }
    }

    fn to_schema(&self) -> Value {
        let mut schema = self.extra_keywords.clone();
        schema["type"] = "object".into();
        if !self.properties.is_empty() {
            schema["properties"] = self.properties_to_schema(&self.properties);
        }
        if !self.pattern_properties.is_empty() {
            schema["patternProperties"] = self.properties_to_schema(&self.pattern_properties);
        }
        if self.required_properties.is_some() || self.include_empty_required {
            let mut required_props: Vec<String>;
            if let Some(required_properties) = &self.required_properties {
                required_props = required_properties.iter().map(|p| p.to_string()).collect();
            } else {
                required_props = vec![];
            }
            required_props.sort();

            if !required_props.is_empty() || self.include_empty_required {
                schema["required"] = required_props.into();
            } else {
                // this is done in case there's a conflict with the required properties
                // from extra keywords
                schema.as_object_mut().unwrap().shift_remove("required");
            }
        } else {
            schema.as_object_mut().unwrap().shift_remove("required");
        }
        schema
    }
}

impl ObjectStrategy {
    fn properties_to_schema(&self, properties: &OrderMap<String, SchemaNode>) -> Value {
        let mut schema_properties = json!({});
        properties.iter().for_each(|(prop, node)| {
            schema_properties[prop] = node.to_schema();
        });
        schema_properties
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ordermap_equality_differs_from_indexmap() {
        // Two ObjectStrategies with same keys/values in different order
        let mut strat1 = ObjectStrategy::new();
        strat1.properties.insert("a".to_string(), SchemaNode::new());
        strat1.properties.insert("b".to_string(), SchemaNode::new());

        let mut strat2 = ObjectStrategy::new();
        strat2.properties.insert("b".to_string(), SchemaNode::new());
        strat2.properties.insert("a".to_string(), SchemaNode::new());

        let keys1: Vec<_> = strat1.properties.keys().collect();
        let keys2: Vec<_> = strat2.properties.keys().collect();
        anstream::println!("keys1 = {:?}", keys1);
        anstream::println!("keys2 = {:?}", keys2);

        // The keys are the same set, but in different order.
        // With OrderMap, properties != properties because order matters.
        // With IndexMap, they would compare equal.
        assert_ne!(
            strat1.properties, strat2.properties,
            "OrderMap should treat maps with different insertion order as unequal"
        );
    }
}
