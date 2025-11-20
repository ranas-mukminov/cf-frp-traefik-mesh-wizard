from mesh_wizard.generators import cloudflare_generator
from mesh_wizard.loader import load_topology


def _load_example(name: str):
    return load_topology(f"examples/{name}")


def test_cloudflare_generator_has_catch_all():
    topology = _load_example("simple-single-vps.yaml")
    config = cloudflare_generator.generate(topology)
    assert config["tunnel"] == topology.cloudflare.tunnel_name
    assert config["ingress"][-1]["service"] == "http_status:404"
    hostnames = [item["hostname"] for item in config["ingress"] if "hostname" in item]
    assert "apps.example.com" in hostnames
