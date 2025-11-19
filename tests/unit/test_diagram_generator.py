from mesh_wizard.generators import diagram_generator
from mesh_wizard.loader import load_topology


def test_diagram_contains_nodes():
    topology = load_topology("examples/simple-single-vps.yaml")
    art = diagram_generator.build_ascii(topology)
    assert "vps-hetzner" in art
    assert "apps-router" in art
