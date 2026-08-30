import uuid

class Category:
    def __init__(self, name: str, icon: str = "folder", order: int = 0, id: str = None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.icon = icon
        self.order = order

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "order": self.order
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Category":
        return cls(
            id=data.get("id"),
            name=data.get("name", "General"),
            icon=data.get("icon", "folder"),
            order=data.get("order", 0)
        )
