from datetime import datetime
import json

def orm_to_dict(obj):
    """Convert ORM object to dict, serializing datetime to ISO string.
    Use this before model_validate to avoid Pydantic datetime->string errors."""
    d = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if val is None:
            d[col.name] = None  # keep None, let caller or schema handle it
        elif isinstance(val, datetime):
            d[col.name] = val.isoformat()
        elif isinstance(val, (dict, list)):
            d[col.name] = json.dumps(val, ensure_ascii=False)
        else:
            d[col.name] = val
    return d


def sanitize_for_model(d, defaults=None):
    """Replace None values with sensible defaults for Pydantic model_validate."""
    if defaults is None:
        defaults = {}
    out = {}
    for k, v in d.items():
        if v is None:
            out[k] = defaults.get(k, v)
        else:
            out[k] = v
    return out