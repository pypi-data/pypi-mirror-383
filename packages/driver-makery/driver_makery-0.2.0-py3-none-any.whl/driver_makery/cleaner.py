import os
import glob

def remove_generated_files(output_text_filename: str):
    files = [output_text_filename] + glob.glob("Part_*.txt") + glob.glob("Register_Definitions_Part_*.h")
    deleted = 0
    for fpath in files:
        if os.path.exists(fpath):
            os.remove(fpath)
            print(f"   - 삭제됨: {fpath}")
            deleted += 1
    print(f"✅ 총 {deleted}개 파일 삭제 완료")
