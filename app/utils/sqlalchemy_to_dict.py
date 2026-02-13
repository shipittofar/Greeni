from sqlalchemy.inspection import inspect
from uuid import UUID
from datetime import datetime

def sqlalchemy_to_dict(obj):
    result = {}
    for c in inspect(obj).mapper.column_attrs:
        value = getattr(obj, c.key)
        if isinstance(value, UUID):
            value = str(value)
        elif isinstance(value, datetime):
            value = value.isoformat()
        result[c.key] = value
    return result
