if hasattr(__import__("sys").stdout, "reconfigure"):
    __import__("sys").stdout.reconfigure(encoding="utf-8")

class BaseTool:
    name: str = ""
    description: str = ""
    parameters: dict = {}

    def execute(self, args: dict, kb, client, scope=None):
        raise NotImplementedError
