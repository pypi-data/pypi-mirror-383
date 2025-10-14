import re
from typing import List

def parse_build_selection(arg: str, total_parts: int) -> List[int]:
    parts = set()
    for token in arg.split(","):
        t = token.strip()
        if not t:
            continue
        if "-" in t:
            a, b = t.split("-", 1)
            a = int(a); b = int(b)
            if a > b:
                a, b = b, a
            for x in range(a, b + 1):
                if 1 <= x <= total_parts:
                    parts.add(x)
        else:
            x = int(t)
            if 1 <= x <= total_parts:
                parts.add(x)
    return sorted(parts)

def find_register_names(section: str, pattern: str):
    return re.findall(pattern, section)

def compile_page_marker(page_num: int) -> str:
    return f"\n--- PAGE {page_num} START (Source Page) ---\n"
