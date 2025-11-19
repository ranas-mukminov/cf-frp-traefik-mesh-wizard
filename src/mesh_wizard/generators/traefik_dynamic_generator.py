"""Traefik dynamic configuration generator."""
from __future__ import annotations

from typing import Dict, List

from ..model import MeshTopology, Node, Service

DEFAULT_HTTP_BACKEND_PORT = 8000
DEFAULT_TCP_BACKEND_PORT = 9000


def _router_name(service: Service) -> str:
    return f"{service.id}-router"


def _service_name(service: Service) -> str:
    return f"{service.id}-service"


def _http_backend_url(node: Node, service: Service) -> str:
    if service.backend:
        if service.backend.type == "static_url" and service.backend.url:
            return service.backend.url
        if service.backend.type == "frp_http" and node.frp:
            port = node.frp.vhost_http_port or 19080
            return f"http://127.0.0.1:{port}"
    if service.target and service.target.ip and service.target.port:
        return f"http://{service.target.ip}:{service.target.port}"
    return f"http://127.0.0.1:{DEFAULT_HTTP_BACKEND_PORT}"


def _tcp_backend_address(node: Node, service: Service) -> str:
    if service.backend and service.backend.type == "frp_tcp" and node.frp:
        port = node.frp.vhost_https_port or 19443
        return f"127.0.0.1:{port}"
    if service.target and service.target.ip and service.target.port:
        return f"{service.target.ip}:{service.target.port}"
    return f"127.0.0.1:{DEFAULT_TCP_BACKEND_PORT}"


def _router_entrypoints(service: Service) -> List[str]:
    if service.router and service.router.entrypoints:
        return service.router.entrypoints
    return ["websecure"] if service.type == "http" else ["tcp"]


def _router_rule(service: Service) -> str:
    if service.router and service.router.rule:
        return service.router.rule
    if service.type == "http":
        return "PathPrefix(`/`)"
    return "HostSNI(`*`)"


def _tls_block(service: Service) -> Dict[str, object] | None:
    if service.router and service.router.tls:
        return {}
    return None


def _generate_http_section(node: Node, services: List[Service]) -> Dict[str, object]:
    routers: Dict[str, Dict[str, object]] = {}
    svcs: Dict[str, Dict[str, object]] = {}
    for service in services:
        router_name = _router_name(service)
        service_name = _service_name(service)
        routers[router_name] = {
            "rule": _router_rule(service),
            "entryPoints": _router_entrypoints(service),
            "service": service_name,
        }
        tls_block = _tls_block(service)
        if tls_block is not None:
            routers[router_name]["tls"] = tls_block
        svcs[service_name] = {
            "loadBalancer": {
                "servers": [
                    {"url": _http_backend_url(node, service)}
                ]
            }
        }
    return {"routers": routers, "services": svcs}


def _generate_tcp_section(node: Node, services: List[Service]) -> Dict[str, object]:
    routers: Dict[str, Dict[str, object]] = {}
    svcs: Dict[str, Dict[str, object]] = {}
    for service in services:
        router_name = _router_name(service)
        service_name = _service_name(service)
        routers[router_name] = {
            "rule": _router_rule(service),
            "entryPoints": _router_entrypoints(service),
            "service": service_name,
        }
        tls_block = _tls_block(service)
        if tls_block is not None:
            routers[router_name]["tls"] = tls_block
        svcs[service_name] = {
            "loadBalancer": {
                "servers": [
                    {"address": _tcp_backend_address(node, service)}
                ]
            }
        }
    return {"routers": routers, "services": svcs}


def generate(topology: MeshTopology) -> Dict[str, Dict[str, object]]:
    configs: Dict[str, Dict[str, object]] = {}
    for node in topology.nodes.values():
        if not node.traefik or not node.traefik.enabled:
            continue
        http_services = [svc for svc in topology.services.values() if svc.node == node.id and svc.type == "http" and svc.via == "traefik"]
        tcp_services = [svc for svc in topology.services.values() if svc.node == node.id and svc.type == "tcp" and svc.via == "traefik"]
        dynamic: Dict[str, object] = {}
        if http_services:
            dynamic["http"] = _generate_http_section(node, http_services)
        if tcp_services:
            dynamic["tcp"] = _generate_tcp_section(node, tcp_services)
        configs[f"{node.id}-traefik-dynamic.yaml"] = dynamic if dynamic else {"http": {}, "tcp": {}}
    return configs
