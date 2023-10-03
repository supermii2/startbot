class Entrant:
    def __init__(self, name: str, userid: int = None):
        self.name, self.id = name, userid

    def __str__(self) -> str:
        return self.name
