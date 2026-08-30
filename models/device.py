import uuid

class Device:
    def __init__(self, name: str, host: str, port: int = 80, description: str = "", status_endpoint: str = "", id: str = None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.host = host.strip()
        self.port = int(port) if str(port).isdigit() else 80
        self.description = description
        self.status_endpoint = status_endpoint.strip()

    @property
    def base_url(self) -> str:
        host_str = self.host
        if host_str.startswith("http://") or host_str.startswith("https://"):
            url = host_str
        else:
            url = f"http://{host_str}"

        # If port is specified and not standard 80, add it if not present in host
        if self.port and self.port != 80 and f":{self.port}" not in url:
            # Strip trailing slash if present
            url = url.rstrip("/")
            url = f"{url}:{self.port}"
        return url.rstrip("/")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "description": self.description,
            "status_endpoint": self.status_endpoint
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Device":
        return cls(
            id=data.get("id"),
            name=data.get("name", "Unnamed Device"),
            host=data.get("host", ""),
            port=data.get("port", 80),
            description=data.get("description", ""),
            status_endpoint=data.get("status_endpoint", "")
        )
