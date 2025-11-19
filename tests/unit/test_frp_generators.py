from mesh_wizard.generators import frp_client_generator, frp_server_generator
from mesh_wizard.loader import load_topology


def test_frp_server_generator_uses_token():
    topology = load_topology("examples/simple-single-vps.yaml")
    configs = frp_server_generator.generate(topology)
    content = next(iter(configs.values()))
    assert "auth.token" in content
    assert "CHANGE_ME_SECURE_TOKEN" in content


def test_frp_client_generator_links_to_server():
    topology = load_topology("examples/multi-vps-k3s-lan.yaml")
    configs = frp_client_generator.generate(topology)
    # k3s-lan client should exist
    assert "k3s-lan-frpc.toml" in configs
    assert "serverAddr" in configs["k3s-lan-frpc.toml"]
