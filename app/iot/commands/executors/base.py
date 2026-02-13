class BaseCommandExecutor:
    def __init__(self, command: dict):
        self.command = command

    async def execute(self):
        raise NotImplementedError("Executor must implement 'execute' method.")
