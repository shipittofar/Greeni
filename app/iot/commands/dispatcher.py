# app/iot/commands/dispatcher.py
"""
Routes inbound MQTT command payloads to the correct executor
based on the 'type' field in the payload.
"""
from loguru import logger


# Map of command type string → executor class (lazy imports to avoid circular deps)
_EXECUTOR_MAP = {
    "ACTUATOR": "app.iot.commands.executors.actuator.ActuatorCommandExecutor",
    "SYSTEM":   "app.iot.commands.executors.system.SystemCommandExecutor",
}


def _load_executor_class(dotted_path: str):
    module_path, class_name = dotted_path.rsplit(".", 1)
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


async def dispatch_command(command: dict) -> None:
    """
    Receive a parsed command dict (from MQTT or internal scheduler) and
    delegate execution to the appropriate executor.

    Expected keys:
        type      (str)  – command category, e.g. "ACTUATOR", "SYSTEM"
        device    (str)  – target device_id
        ...              – executor-specific fields
    """
    cmd_type = command.get("type", "").upper()

    executor_path = _EXECUTOR_MAP.get(cmd_type)
    if not executor_path:
        logger.warning(f"[Dispatcher] Unknown command type '{cmd_type}' — ignored")
        return

    try:
        ExecutorClass = _load_executor_class(executor_path)
        executor = ExecutorClass(command)
        await executor.execute()
        logger.info(f"[Dispatcher] Executed {cmd_type} command for device={command.get('device')}")
    except Exception as e:
        logger.exception(
            f"[Dispatcher] Error executing {cmd_type} command "
            f"for device={command.get('device')}: {e}"
        )
