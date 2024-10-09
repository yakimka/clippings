def truncate_string(value: str, max_length: int) -> str:
    if len(value) > max_length:
        return f"{value[:max_length-3]}..."
    return value
