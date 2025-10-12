use serde_json::Value;
use simd_json;

/// base schema strategy trait
pub trait SchemaStrategy {
    fn match_schema(schema: &Value) -> bool;
    fn match_object(object: &simd_json::BorrowedValue) -> bool;

    fn add_schema(&mut self, schema: &Value) {
        self.add_extra_keywords(schema)
    }

    /// Add multiple schemas at once
    /// Default implementation: sequential fallback for backward compatibility
    fn add_schemas(&mut self, schemas: &[&Value]) {
        for schema in schemas {
            self.add_schema(schema);
        }
    }

    fn add_object(&mut self, _object: &simd_json::BorrowedValue);

    fn to_schema(&self) -> Value {
        self.get_extra_keywords().clone()
    }

    fn add_extra_keywords(&mut self, schema: &Value) {
        if let Value::Object(schema) = schema {
            schema.iter().for_each(|(key, value)| {
                let keywords = self.get_extra_keywords_mut();
                if let Value::Object(keywords) = keywords {
                    if key == "type" {
                    } else if !keywords.contains_key(key) {
                        // add the property from the input schema if it doesn't already exist
                        keywords.insert(key.to_string(), value.clone());
                    }
                }
            });
        }
    }

    fn get_extra_keywords_mut(&mut self) -> &mut Value;

    fn get_extra_keywords(&self) -> &Value;
}

/// base schema strategy trait for scalar types
pub trait ScalarSchemaStrategy: SchemaStrategy {
    fn js_type() -> &'static str;

    fn to_schema(&self) -> Value {
        let mut schema = SchemaStrategy::to_schema(self);
        schema["type"] = Value::String(Self::js_type().to_string());
        schema
    }
}
