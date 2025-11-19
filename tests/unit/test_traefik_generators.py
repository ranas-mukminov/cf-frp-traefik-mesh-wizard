from mesh_wizard.generators import traefik_dynamic_generator, traefik_static_generator
from mesh_wizard.loader import load_topology


def test_traefik_static_contains_entrypoints():
    topology = load_topology("examples/simple-single-vps.yaml")
    configs = traefik_static_generator.generate(topology)
    assert any("entryPoints" in cfg for cfg in configs.values())


def test_traefik_dynamic_router_rules():
    topology = load_topology("examples/multi-vps-k3s-lan.yaml")
    configs = traefik_dynamic_generator.generate(topology)
    dyn = configs[[key for key in configs if key.endswith("dynamic.yaml")][0]]
    assert "http" in dyn
    assert dyn["http"]["routers"], "should have routers"
