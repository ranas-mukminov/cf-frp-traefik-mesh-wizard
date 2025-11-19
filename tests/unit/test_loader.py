import yaml

from mesh_wizard.loader import load_raw, load_topology


def test_load_single_file(tmp_path):
    mesh_file = tmp_path / "mesh.yaml"
    mesh_file.write_text(
        yaml.safe_dump(
            {
                "mesh": {"name": "demo"},
                "nodes": [{"id": "vps", "role": "public_vps"}],
                "services": [{"id": "svc", "type": "http", "node": "vps"}],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    raw = load_raw(mesh_file)
    assert raw["mesh"]["name"] == "demo"


def test_load_directory_merges(tmp_path):
    part1 = {
        "mesh": {"name": "demo"},
        "nodes": [{"id": "vps", "role": "public_vps"}],
    }
    part2 = {
        "services": [{"id": "svc", "type": "http", "node": "vps"}],
    }
    (tmp_path / "part1.yaml").write_text(yaml.safe_dump(part1, sort_keys=False), encoding="utf-8")
    (tmp_path / "part2.yaml").write_text(yaml.safe_dump(part2, sort_keys=False), encoding="utf-8")
    topology = load_topology(tmp_path)
    assert "svc" in topology.services
