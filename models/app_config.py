class AppConfig:
    THEME_LIGHT = "light"
    THEME_DARK = "dark"
    THEME_SYSTEM = "system"

    def __init__(
        self,
        theme_mode: str = THEME_LIGHT,
        default_timeout: int = 5,
        default_control_type: str = "action",
        global_requires_confirmation: bool = False,
        user_name: str = "Pranav"
    ):
        self.theme_mode = theme_mode
        self.default_timeout = default_timeout
        self.default_control_type = default_control_type
        self.global_requires_confirmation = global_requires_confirmation
        self.user_name = user_name

    def to_dict(self) -> dict:
        return {
            "theme_mode": self.theme_mode,
            "default_timeout": self.default_timeout,
            "default_control_type": self.default_control_type,
            "global_requires_confirmation": self.global_requires_confirmation,
            "user_name": self.user_name
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        if not data:
            return cls()
        return cls(
            theme_mode=data.get("theme_mode", cls.THEME_LIGHT),
            default_timeout=data.get("default_timeout", 5),
            default_control_type=data.get("default_control_type", "action"),
            global_requires_confirmation=data.get("global_requires_confirmation", False),
            user_name=data.get("user_name", "Pranav")
        )
