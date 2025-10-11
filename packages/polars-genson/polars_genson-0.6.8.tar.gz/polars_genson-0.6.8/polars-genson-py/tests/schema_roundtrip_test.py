# tests/schema_roundtrip_test.py
"""Round-trip tests for schema_to_json / json_to_schema."""

import polars as pl
import polars_genson  # noqa: F401
import pytest


def test_round_trip_basic_from_df_schema():
    """Basic: DF.schema -> JSON -> Schema equals original."""
    df = pl.DataFrame({"a": [1, 2, 3], "b": [True, False, True]})

    original_schema = pl.Schema(df.schema)  # normalize to Schema object

    jsonified = polars_genson.schema_to_json(original_schema)
    assert isinstance(jsonified, str)

    recovered = polars_genson.json_to_schema(jsonified)
    assert isinstance(recovered, pl.Schema)

    assert recovered == original_schema


def test_round_trip_complex_types():
    """Complex dtypes survive round-trip intact."""
    complex_schema = pl.Schema(
        {
            "id": pl.Int64,
            "name": pl.String,
            "active": pl.Boolean,
            "scores": pl.List(pl.Float64),
            "price": pl.Decimal(10, 2),
            "arr3": pl.Array(pl.Int32, 3),
            "meta": pl.Struct(
                {"source": pl.String, "ts": pl.Datetime(time_unit="us", time_zone=None)}
            ),
            "tags": pl.List(pl.String),
        }
    )

    jsonified = polars_genson.schema_to_json(complex_schema)
    recovered = polars_genson.json_to_schema(jsonified)

    assert recovered == complex_schema


def test_round_trip_preserves_field_order():
    """Field insertion order is preserved by the round-trip."""
    original = pl.Schema({"z": pl.String, "b": pl.Int64, "a": pl.Boolean})

    jsonified = polars_genson.schema_to_json(original)
    recovered = polars_genson.json_to_schema(jsonified)

    # Ensure equality and order
    assert recovered == original
    assert list(recovered.keys()) == ["z", "b", "a"]


def test_round_trip_empty_schema():
    """An empty schema round-trips cleanly."""
    empty = pl.Schema({})
    jsonified = polars_genson.schema_to_json(empty)
    recovered = polars_genson.json_to_schema(jsonified)
    assert recovered == empty


def test_json_to_schema_invalid_json_raises():
    """Invalid JSON should raise a helpful error."""
    bad_json = "{not valid json"
    with pytest.raises(Exception):
        _ = polars_genson.json_to_schema(bad_json)


def test_schema_to_dict_nested_structs_lists():
    """schema_to_dict flattens nested types into comparable dicts."""
    schema = pl.Schema(
        {
            "id": pl.Int64,
            "meta": pl.Struct(
                {
                    "tags": pl.List(pl.List(pl.String)),
                    "scores": pl.Array(pl.Float32, 3),
                }
            ),
        }
    )

    # Expect correct deep structure for equality comparisons
    assert polars_genson.schema_to_dict(schema) == {
        "id": "Int64",
        "meta": {
            "tags": {"list": {"list": "String"}},
            "scores": {"array": {"inner": "Float32", "size": 3}},
        },
    }

    schema2 = pl.Schema(
        {
            "meta": pl.Struct(
                {
                    "scores": pl.Array(pl.Float32, 3),
                    "tags": pl.List(pl.List(pl.String)),
                }
            ),
            "id": pl.Int64,
        }
    )
    # Reordered schemas should not be directly equivalent
    assert schema != schema2
    # Reordered schemas should be equivalent after recursive conversion to dicts
    assert polars_genson.schema_to_dict(schema) == polars_genson.schema_to_dict(schema2)
