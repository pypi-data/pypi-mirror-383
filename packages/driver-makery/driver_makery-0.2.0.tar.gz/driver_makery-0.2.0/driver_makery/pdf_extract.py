import os
import fitz

def extract_pdf_text_to_file(pdf_path: str, start_page: int, end_page: int, output_file: str):
    if not os.path.exists(pdf_path):
        print(f"[오류] PDF 파일을 찾을 수 없습니다: {pdf_path}")
        return False, None
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for i in range(start_page - 1, end_page):
            page = doc.load_page(i)
            text += f"\n--- PAGE {i + 1} START (Source Page) ---\n" + page.get_text("text")
        doc.close()
        text = text.replace('\xa0', ' ')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"✅ 텍스트 추출 완료 → {output_file}")
        return True, text
    except Exception as e:
        print(f"[오류] 텍스트 추출 중 오류: {e}")
        return False, None
