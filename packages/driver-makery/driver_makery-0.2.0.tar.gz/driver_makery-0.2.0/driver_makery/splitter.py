import re
from typing import List, Tuple
from .utils import compile_page_marker, find_register_names

def analyze_text_via_regex(text: str, split_unit: int, reg_name_pattern: str) -> List[Tuple[str,str,int,int]]:
    text = text.replace('\xa0', ' ')
    all_registers = []
    current_page = None
    sections = re.split(r'(\n--- PAGE \d+ START \(Source Page\) ---\n)', text)

    for section in sections:
        match = re.search(r'PAGE (\d+)', section)
        if match:
            current_page = int(match.group(1))
            continue
        if current_page:
            reg_names = find_register_names(section, reg_name_pattern)
            for name in reg_names:
                if not all_registers or all_registers[-1][0] != name:
                    all_registers.append((name, current_page))

    split_ranges = []
    for i in range(0, len(all_registers), split_unit):
        group = all_registers[i:i + split_unit]
        split_ranges.append((group[0][0], group[-1][0], group[0][1], group[-1][1]))
    print(f"✅ 총 {len(all_registers)}개 레지스터를 {len(split_ranges)}개로 분할")
    return split_ranges

def write_split_files(full_text: str, split_ranges: List[Tuple[str,str,int,int]]):
    for i, (start_reg, end_reg, start_page, end_page) in enumerate(split_ranges):
        next_page = end_page + 1
        pattern_start = re.escape(compile_page_marker(start_page))
        pattern_end = re.escape(compile_page_marker(next_page))

        start_match = re.search(pattern_start, full_text)
        end_match = re.search(pattern_end, full_text[start_match.start():]) if start_match else None
        if not start_match:
            continue

        chunk = full_text[start_match.start(): (start_match.start() + end_match.start()) if end_match else len(full_text)]
        filename = f"Part_{i + 1:02d}_{start_reg}-{end_reg}_{start_page}-{end_page}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(chunk)
        print(f"   - {filename} 저장 완료")
