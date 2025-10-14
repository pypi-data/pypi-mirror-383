import os
import sys
from .config import load_config
from .pdf_extract import extract_pdf_text_to_file
from .splitter import analyze_text_via_regex, write_split_files
from .build import run_build
from .cleaner import remove_generated_files

def main():
    print("in the main")

    if len(sys.argv) < 2:
        print(f"\n사용법: drivermakery [prepare | split | build [선택] | clean]")
        print("  - build 선택 인자 예: 3 / 2-5 / 1,3,7 / 1,4-6,9 (미지정 시 전체)")
        raise SystemExit(1)

    cfg = load_config()
    mode = sys.argv[1].lower()

    if mode == "prepare":
        ok, text = extract_pdf_text_to_file(
            cfg["PDF_PATH"], cfg["REG_START_PAGE"], cfg["REG_END_PAGE"], cfg["OUTPUT_TEXT_FILENAME"]
        )
        if ok:
            ranges = analyze_text_via_regex(text, cfg["REG_SPLIT_UNIT"], cfg["REG_NAME_PATTERN"])
            write_split_files(text, ranges)

    elif mode == "split":
        if not os.path.exists(cfg["OUTPUT_TEXT_FILENAME"]):
            print("[오류] 먼저 'prepare' 실행 필요.")
            raise SystemExit(1)
        with open(cfg["OUTPUT_TEXT_FILENAME"], 'r', encoding='utf-8') as f:
            text = f.read()
        ranges = analyze_text_via_regex(text, cfg["REG_SPLIT_UNIT"], cfg["REG_NAME_PATTERN"])
        write_split_files(text, ranges)

    elif mode == "build":
        selection_arg = sys.argv[2] if len(sys.argv) >= 3 else ""
        api_key = cfg.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        api_url = cfg.get("GEMINI_API_URL")
        if not api_key:
            print("[오류] GEMINI_API_KEY가 설정되지 않았습니다. .env 또는 환경변수로 설정하세요.")
            raise SystemExit(1)
        run_build(selection_arg, cfg["CODE_OUTPUT_FILENAME_FORMAT"], api_url, api_key)

    elif mode == "clean":
        remove_generated_files(cfg["OUTPUT_TEXT_FILENAME"])

    else:
        print(f"[오류] 알 수 없는 명령: {mode}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()