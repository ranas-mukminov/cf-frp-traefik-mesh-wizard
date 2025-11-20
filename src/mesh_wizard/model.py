"""Domain model for mesh topology."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MeshMetadata:
    name: str
    description: str | None = None


@dataclass
class DNSMapping:
    hostname: str
    entrypoint: str
    target: str


@dataclass
class CloudflareConfig:
    tunnel_name: str
    account_id: str | None = None
    zone: str | None = None
    credentials_file: str | None = None
    dns: List[DNSMapping] = field(default_factory=list)


@dataclass
class FRPProxy:
    name: str
    type: str
    local_ip: str
    local_port: int
    remote_port: int | None = None
    custom_domains: List[str] | None = None
    subdomain: str | None = None


@dataclass
class FRPConfig:
    server: bool = False
    client: bool = False
    bind_port: int | None = None
    vhost_http_port: int | None = None
    vhost_https_port: int | None = None
    server_addr: str | None = None
    server_port: int | None = None
    token: str | None = None
    proxies: List[FRPProxy] = field(default_factory=list)


@dataclass
class TraefikEntrypoint:
    name: str
    port: int


@dataclass
class TraefikConfig:
    enabled: bool = False
    entrypoints: List[TraefikEntrypoint] = field(default_factory=list)
    log_level: str | None = None
    provider_directory: str | None = None


@dataclass
class Node:
    id: str
    role: str
    location: str | None = None
    public_ip: str | None = None
    lan_ip: str | None = None
    labels: List[str] = field(default_factory=list)
    frp: FRPConfig | None = None
    traefik: TraefikConfig | None = None


@dataclass
class ServiceRouter:
    rule: str | None = None
    entrypoints: List[str] = field(default_factory=list)
    service: str | None = None
    tls: bool | None = None


@dataclass
class ServiceBackend:
    type: str
    proxy_name: str | None = None
    url: str | None = None


@dataclass
class ServiceTarget:
    node: str | None = None
    ip: str | None = None
    port: int | None = None


@dataclass
class Service:
    id: str
    type: str
    node: str
    via: str
    router: ServiceRouter | None = None
    backend: ServiceBackend | None = None
    target: ServiceTarget | None = None
    description: str | None = None


@dataclass
class MeshTopology:
    mesh: MeshMetadata
    nodes: Dict[str, Node]
    services: Dict[str, Service]
    cloudflare: CloudflareConfig | None = None

    @staticmethod
    def _build_frp_proxy(data: dict) -> FRPProxy:
        return FRPProxy(
            name=data["name"],
            type=data["type"],
            local_ip=data["local_ip"],
            local_port=int(data["local_port"]),
            remote_port=data.get("remote_port"),
            custom_domains=data.get("custom_domains"),
            subdomain=data.get("subdomain"),
        )

    @staticmethod
    def _build_frp_config(data: dict | None) -> FRPConfig | None:
        if not data:
            return None
        proxies = [MeshTopology._build_frp_proxy(item) for item in data.get("proxies", [])]
        return FRPConfig(
            server=data.get("server", False),
            client=data.get("client", False),
            bind_port=data.get("bind_port"),
            vhost_http_port=data.get("vhost_http_port"),
            vhost_https_port=data.get("vhost_https_port"),
            server_addr=data.get("server_addr"),
            server_port=data.get("server_port"),
            token=data.get("token"),
            proxies=proxies,
        )

    @staticmethod
    def _build_traefik_config(data: dict | None) -> TraefikConfig | None:
        if not data:
            return None
        entrypoints = [
            TraefikEntrypoint(name=item["name"], port=int(item["port"]))
            for item in data.get("entrypoints", [])
        ]
        return TraefikConfig(
            enabled=data.get("enabled", False),
            entrypoints=entrypoints,
            log_level=data.get("log_level"),
            provider_directory=data.get("provider_directory"),
        )

    @staticmethod
    def _build_node(raw: dict) -> Node:
        frp = MeshTopology._build_frp_config(raw.get("frp"))
        traefik = MeshTopology._build_traefik_config(raw.get("traefik"))
        return Node(
            id=raw["id"],
            role=raw["role"],
            location=raw.get("location"),
            public_ip=raw.get("public_ip"),
            lan_ip=raw.get("lan_ip"),
            labels=raw.get("labels", []),
            frp=frp,
            traefik=traefik,
        )

    @staticmethod
    def _build_router(data: dict | None) -> ServiceRouter | None:
        if not data:
            return None
        return ServiceRouter(
            rule=data.get("rule"),
            entrypoints=data.get("entrypoints", []),
            service=data.get("service"),
            tls=data.get("tls"),
        )

    @staticmethod
    def _build_backend(data: dict | None) -> ServiceBackend | None:
        if not data:
            return None
        return ServiceBackend(
            type=data["type"],
            proxy_name=data.get("proxy_name"),
            url=data.get("url"),
        )

    @staticmethod
    def _build_target(data: dict | None) -> ServiceTarget | None:
        if not data:
            return None
        return ServiceTarget(node=data.get("node"), ip=data.get("ip"), port=data.get("port"))

    @staticmethod
    def _build_service(raw: dict) -> Service:
        return Service(
            id=raw["id"],
            type=raw["type"],
            node=raw["node"],
            via=raw.get("via", "traefik"),
            router=MeshTopology._build_router(raw.get("router")),
            backend=MeshTopology._build_backend(raw.get("backend")),
            target=MeshTopology._build_target(raw.get("target")),
            description=raw.get("description"),
        )

    @staticmethod
    def from_dict(data: dict) -> "MeshTopology":
        mesh_meta = data.get("mesh", {})
        mesh = MeshMetadata(name=mesh_meta["name"], description=mesh_meta.get("description"))

        cloudflare_cfg = data.get("cloudflare")
        cloudflare = None
        if cloudflare_cfg:
            dns_entries = [
                DNSMapping(
                    hostname=item["hostname"],
                    entrypoint=item["entrypoint"],
                    target=item["target"],
                )
                for item in cloudflare_cfg.get("dns", [])
            ]
            cloudflare = CloudflareConfig(
                tunnel_name=cloudflare_cfg["tunnel_name"],
                account_id=cloudflare_cfg.get("account_id"),
                zone=cloudflare_cfg.get("zone"),
                credentials_file=cloudflare_cfg.get("credentials_file"),
                dns=dns_entries,
            )

        nodes = {item["id"]: MeshTopology._build_node(item) for item in data.get("nodes", [])}
        services = {
            item["id"]: MeshTopology._build_service(item) for item in data.get("services", [])
        }

        return MeshTopology(mesh=mesh, nodes=nodes, services=services, cloudflare=cloudflare)

    def get_node(self, node_id: str) -> Node:
        try:
            return self.nodes[node_id]
        except KeyError as exc:  # pragma: no cover - defensive
            raise KeyError(f"Unknown node '{node_id}'") from exc

    def require_service(self, service_id: str) -> Service:
        try:
            return self.services[service_id]
        except KeyError as exc:  # pragma: no cover - defensive
            raise KeyError(f"Unknown service '{service_id}'") from exc
