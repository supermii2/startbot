def list_to_str(lst: list) -> str:
    s = ""
    for x in lst:
        s += x + ", "
    return s[:-2] if s != "" else s
