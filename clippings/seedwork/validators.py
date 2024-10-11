def truncate_string(value: str, max_length: int) -> str:
    if len(value) > max_length:
        return f"{value[:max_length-3]}..."
    return value


def validate_hashed_id(value: str) -> bool:
    if not isinstance(value, str) or len(value) != 13:
        return False
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return all(c in chars for c in value)
