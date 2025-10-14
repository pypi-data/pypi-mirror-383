import re
import glob
from .gemini_client import call_gemini
from .codegen import build_c_code_from_json
from .utils import parse_build_selection

def rebuild_ranges_from_filenames(part_files):
    ranges = []
    for filename in part_files:
        match = re.search(r"Part_(\d{2})_([A-Z0-9_]+)-([A-Z0-9_]+)_(\d+)-(\d+)\.txt$", filename)
        if match:
            _, start_reg, end_reg, start_page, end_page = match.groups()
            ranges.append((start_reg, end_reg, int(start_page), int(end_page)))
    return ranges

def process_code_generation(part_number, ranges, api_url, api_key, code_output_fmt):
    start_reg, end_reg, start_page, end_page = ranges[part_number - 1]
    input_file = f"Part_{part_number:02d}_{start_reg}-{end_reg}_{start_page}-{end_page}.txt"
    output_file = code_output_fmt.format(part_number=part_number)

    with open(input_file, 'r', encoding='utf-8') as f:
        doc_text = f.read()

    print(f"\n[Gemini 변환] {input_file} → {output_file}")
    json_data = call_gemini(doc_text, api_url=api_url, api_key=api_key)
    c_code = build_c_code_from_json(json_data)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(c_code)
    print(f"✅ 코드 생성 완료 → {output_file}")

def run_build(selection_arg: str, code_output_fmt: str, api_url: str, api_key: str):
    part_files = sorted(glob.glob("Part_*.txt"))
    if not part_files:
        print("[오류] 'prepare' 또는 'split'을 먼저 실행하세요.")
        raise SystemExit(1)

    ranges = rebuild_ranges_from_filenames(part_files)
    total = len(ranges)

    if selection_arg:
        targets = parse_build_selection(selection_arg, total)
        if not targets:
            print(f"[오류] 유효한 파트가 없습니다. 1~{total} 범위를 확인하세요.")
            raise SystemExit(1)
    else:
        targets = list(range(1, total + 1))

    print(f"\n[Build 시작] 총 {len(targets)}개 파트 처리: {targets}")
    for i in targets:
        process_code_generation(i, ranges, api_url, api_key, code_output_fmt)
    print("\n✅ 선택한 파트 코드 생성이 완료되었습니다.")
