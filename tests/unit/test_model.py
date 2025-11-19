from mesh_wizard.model import MeshTopology


def test_model_builds_nodes_and_services(tmp_path):
    mesh = {
        "mesh": {"name": "demo"},
        "nodes": [
            {"id": "vps", "role": "public_vps", "frp": {"server": True, "token": "x"}},
            {"id": "lan", "role": "lan_cluster"},
        ],
        "services": [
            {
                "id": "app",
                "type": "http",
                "node": "vps",
                "via": "traefik",
                "router": {"rule": "Host(`app.example.com`)"},
            }
        ],
    }
    topology = MeshTopology.from_dict(mesh)
    assert topology.mesh.name == "demo"
    assert topology.get_node("vps").frp is not None
    assert topology.require_service("app").router.rule.startswith("Host")
