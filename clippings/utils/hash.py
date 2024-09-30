import mmh3


def hasher(text: str) -> str:
    num_hash = mmh3.hash64(text, 0xFFFFFFFF, signed=False)[0]
    if short_hash := base36_encode(num_hash):
        return short_hash
    raise ValueError("Hash is empty")


def base36_encode(n: int) -> str:
    if n <= 0:
        raise ValueError("Positive non-zero number is required")

    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = []
    while n > 0:
        n, i = divmod(n, len(chars))
        result.append(chars[i])
    return "".join(reversed(result))
