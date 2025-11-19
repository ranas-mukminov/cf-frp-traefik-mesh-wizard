from ai_providers.base import registry
from ai_providers.mock_provider import MockProvider
from mesh_wizard.ai import ha_suggestions, topology_nl_to_yaml
from mesh_wizard.loader import load_topology


def setup_module(module):  # noqa: D103
    registry.configure(MockProvider("apps.example.com"))


def test_topology_from_text_uses_ai_hint():
    data = topology_nl_to_yaml.generate_from_text("Expose apps.example.com")
    assert data["cloudflare"]["dns"][0]["hostname"] == "apps.example.com"


def test_ha_suggestions_returns_report():
    topology = load_topology("examples/simple-single-vps.yaml")
    plan = ha_suggestions.generate(topology)
    assert plan.suggestions
    assert plan.report.startswith("## HA")
