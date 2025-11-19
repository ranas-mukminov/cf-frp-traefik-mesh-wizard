from mesh_wizard.schema_validator import validate_dict


def test_valid_yaml_passes_schema(tmp_path):
    sample = {
        "mesh": {"name": "demo"},
        "nodes": [{"id": "vps", "role": "public_vps"}],
        "services": [{"id": "svc", "type": "http", "node": "vps"}],
    }
    validate_dict(sample)


def test_invalid_yaml_raises_value_error():
    broken = {"mesh": {"name": "demo"}}
    try:
        validate_dict(broken)
    except ValueError as exc:
        assert "nodes" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("validation did not fail")
