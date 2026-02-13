from typing import Optional, Union, List, Dict
from app.cache.redis import redis_client

class BaseCache:
    def __init__(self, namespace: str, expire_seconds: int = 300):
        self.namespace = namespace
        self.expire_seconds = expire_seconds

    def _format_key(self, key: str) -> str:
        return f"{self.namespace}:{key}"

    def _convert_dict_numeric_keys_to_list(self, data):
        if isinstance(data, dict) and all(k.isdigit() for k in data.keys()):
            return [data[k] for k in sorted(data.keys(), key=int)]
        return data

    async def set(self, key: str, value: Union[List[Dict], Dict]):
        """
        Stores value as JSON in Redis.
        Converts dict with numeric keys to list for better RedisInsight display.
        """
        formatted_key = self._format_key(key)

        if isinstance(value, dict):
            keys_are_numbers = all(isinstance(k, str) and k.isdigit() for k in value.keys())
            if keys_are_numbers:
                print(f"[BaseCache Warning] Value for key '{formatted_key}' looks like dict with numeric keys. "
                      f"RedisInsight may not display it nicely. Converting to list.")
                value = self._convert_dict_numeric_keys_to_list(value)

        await redis_client.json().set(formatted_key, "$", value)
        await redis_client.expire(formatted_key, self.expire_seconds)

    async def get(self, key: str) -> Optional[Union[List[Dict], Dict]]:
        return await redis_client.json().get(self._format_key(key))

    async def invalidate(self, key: str):
        await redis_client.delete(self._format_key(key))

    async def invalidate_all(self):
        keys = await redis_client.keys(f"{self.namespace}:*")
        if keys:
            await redis_client.delete(*keys)
