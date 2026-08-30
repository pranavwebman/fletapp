import uuid

class Control:
    TYPE_ACTION = "action"
    TYPE_TOGGLE = "toggle"
    TYPE_MOMENTARY = "momentary"

    def __init__(
        self,
        name: str,
        icon: str = "power_settings_new",
        color: str = "#2196F3",
        control_type: str = TYPE_ACTION,
        device_id: str = "",
        custom_url: str = "",
        on_endpoint: str = "/on",
        off_endpoint: str = "/off",
        http_method: str = "GET",
        request_body: str = "",
        custom_headers: dict = None,
        timeout: int = 5,
        requires_confirmation: bool = False,
        enabled: bool = True,
        category_id: str = "all",
        order: int = 0,
        state: bool = False,  # True = ON, False = OFF
        id: str = None
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.icon = icon
        self.color = color
        self.control_type = control_type
        self.device_id = device_id
        self.custom_url = custom_url.strip()
        self.on_endpoint = on_endpoint.strip()
        self.off_endpoint = off_endpoint.strip()
        self.http_method = http_method.upper()
        self.request_body = request_body
        self.custom_headers = custom_headers if custom_headers is not None else {}
        self.timeout = int(timeout) if str(timeout).isdigit() else 5
        self.requires_confirmation = bool(requires_confirmation)
        self.enabled = bool(enabled)
        self.category_id = category_id
        self.order = order
        self.state = bool(state)

    def get_full_url(self, device=None, is_off: bool = False) -> str:
        endpoint = self.off_endpoint if is_off else self.on_endpoint

        if self.custom_url:
            base = self.custom_url.rstrip("/")
            if endpoint:
                if not endpoint.startswith("/"):
                    endpoint = "/" + endpoint
                return f"{base}{endpoint}"
            return base

        if device:
            base = device.base_url
            if endpoint:
                if not endpoint.startswith("/"):
                    endpoint = "/" + endpoint
                return f"{base}{endpoint}"
            return base

        return endpoint

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "color": self.color,
            "control_type": self.control_type,
            "device_id": self.device_id,
            "custom_url": self.custom_url,
            "on_endpoint": self.on_endpoint,
            "off_endpoint": self.off_endpoint,
            "http_method": self.http_method,
            "request_body": self.request_body,
            "custom_headers": self.custom_headers,
            "timeout": self.timeout,
            "requires_confirmation": self.requires_confirmation,
            "enabled": self.enabled,
            "category_id": self.category_id,
            "order": self.order,
            "state": self.state
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Control":
        return cls(
            id=data.get("id"),
            name=data.get("name", "Unnamed Control"),
            icon=data.get("icon", "power_settings_new"),
            color=data.get("color", "#2196F3"),
            control_type=data.get("control_type", cls.TYPE_ACTION),
            device_id=data.get("device_id", ""),
            custom_url=data.get("custom_url", ""),
            on_endpoint=data.get("on_endpoint", "/on"),
            off_endpoint=data.get("off_endpoint", "/off"),
            http_method=data.get("http_method", "GET"),
            request_body=data.get("request_body", ""),
            custom_headers=data.get("custom_headers", {}),
            timeout=data.get("timeout", 5),
            requires_confirmation=data.get("requires_confirmation", False),
            enabled=data.get("enabled", True),
            category_id=data.get("category_id", "all"),
            order=data.get("order", 0),
            state=data.get("state", False)
        )
