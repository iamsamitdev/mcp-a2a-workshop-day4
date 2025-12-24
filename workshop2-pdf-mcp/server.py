import os
from pathlib import Path
from typing import Optional
import requests
import fitz  # PyMuPDF
import tempfile
from fastmcp import FastMCP
from typhoon_ocr import ocr_document  # ใช้ Typhoon OCR 1.5
from dotenv import load_dotenv

# -----------------------------
# 1. Load Environment Variables
# -----------------------------
# server.py อยู่ที่ Root ดังนั้น .env ก็อยู่ข้างๆ กันเลย
load_dotenv(Path(__file__).parent / ".env")

# -----------------------------
# 2. ตั้งค่า FastMCP
# -----------------------------
mcp = FastMCP("pdf-ocr-llm-tools")

# -----------------------------
# 3. กำหนด Path ของโฟลเดอร์เก็บ PDF
# -----------------------------
# ชี้ไปที่โฟลเดอร์ data ที่อยู่ข้างๆ server.py เลย
PDF_DIR = Path(__file__).parent / "data"


# -----------------------------
# ENV สำหรับ Typhoon OCR และ LLM
# -----------------------------
TYPHOON_OCR_API_KEY = os.getenv("TYPHOON_OCR_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.0-mini")  # หรือ gpt-3.5-turbo / typhoon-v2


# -----------------------------
# ฟังก์ชันช่วยเรียก LLM (LLM & Image Conversion)
# -----------------------------
def call_llm_for_summary(
    content: str,
    extra_instruction: Optional[str] = None,
    max_tokens: int = 1024,
) -> str:
    """
    เรียก LLM ผ่าน API รูปแบบ OpenAI-compatible เพื่อสรุป/วิเคราะห์เอกสาร
    """
    if not LLM_API_KEY:
        raise RuntimeError("กรุณาตั้งค่า LLM_API_KEY ใน environment ก่อนใช้งาน")

    system_prompt = (
        "คุณคือผู้ช่วยวิเคราะห์เอกสารระดับมืออาชีพ "
        "ทำงานกับเอกสารภาษาไทยและอังกฤษได้ดี "
        "ให้สรุปอย่างชัดเจน เข้าใจง่าย และดึง insight ที่สำคัญออกมา"
    )

    if extra_instruction:
        user_prompt = (
            f"{extra_instruction}\n\n" "----- เนื้อหาจาก OCR -----\n" f"{content}\n"
        )
    else:
        user_prompt = (
            "กรุณาสรุปเนื้อหา วิเคราะห์ประเด็นสำคัญ "
            "และดึง insight ที่น่าสนใจจากข้อมูลด้านล่าง:\n\n"
            "----- เนื้อหาจาก OCR -----\n"
            f"{content}\n"
        )

    url = f"{LLM_BASE_URL.rstrip('/')}/chat/completions"

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    # ตรวจสอบว่าเป็น Model ตระกูล o1/o3 หรือไม่ (ที่บังคับใช้ max_completion_tokens)
    # หรือถ้า API แจ้ง error นี้มา ก็ควรเปลี่ยนไปใช้ max_completion_tokens
    # เพื่อความง่าย เราจะเช็คจากชื่อ Model หรือใช้ try-except ก็ได้
    # แต่ในที่นี้ขอปรับให้รองรับทั้งคู่โดยดูจากชื่อ Model คร่าวๆ หรือ default เป็น max_tokens

    is_reasoning_model = any(
        x in LLM_MODEL.lower() for x in ["o1", "o3", "gpt-5"]
    )  # เดาว่า gpt-5 อาจจะเป็น reasoning

    messages = []
    if is_reasoning_model:
        # Reasoning models (like o1) might not support 'system' role or behave better with single user message
        # Combine system prompt into user prompt
        messages = [
            {
                "role": "user",
                "content": f"Instruction: {system_prompt}\n\nTask: {user_prompt}",
            }
        ]
    else:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    payload = {
        "model": LLM_MODEL,
        "messages": messages,
    }

    if is_reasoning_model:
        payload["max_completion_tokens"] = max_tokens
        payload["temperature"] = 1  # Reasoning models require temperature 1
    else:
        payload["max_tokens"] = max_tokens
        payload["temperature"] = 0.3

    resp = requests.post(url, json=payload, headers=headers, timeout=60)

    if resp.status_code == 400:
        # Handle 400 Bad Request specifically to give more info
        try:
            error_detail = resp.json()
        except:
            error_detail = resp.text
        raise ValueError(
            f"LLM API Error (400 Bad Request): {error_detail}. Please check your LLM_MODEL or API Key."
        )

    resp.raise_for_status()
    data = resp.json()

    if "choices" in data and len(data["choices"]) > 0:
        return data["choices"][0]["message"]["content"]
    return ""


# -----------------------------
# Helper Function: แปลง PDF หน้าที่ระบุเป็นรูปภาพ (เพื่อเลี่ยง Poppler)
# -----------------------------
def convert_pdf_page_to_image(pdf_path: Path, page_num: int) -> str:
    """
    Convert a specific page of a PDF to a temporary image file using PyMuPDF.
    Returns the path to the temporary image file.
    """
    doc = fitz.open(pdf_path)
    try:
        # page_num is 1-based from user, fitz is 0-based
        if page_num < 1 or page_num > len(doc):
            raise ValueError(f"Page number {page_num} is out of range (1-{len(doc)})")

        page = doc.load_page(page_num - 1)
        pix = page.get_pixmap(dpi=300)  # 300 DPI for good OCR

        # Create a temp file
        fd, temp_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)

        pix.save(temp_path)
        return temp_path
    finally:
        doc.close()


# -----------------------------
# Helper Function: Logic สำหรับ OCR (แยกออกมาเพื่อให้เรียกใช้ภายในได้)
# -----------------------------
def _ocr_logic(file_name: str, page_num: int) -> str:
    if not TYPHOON_OCR_API_KEY:
        raise RuntimeError(
            "กรุณาตั้งค่า TYPHOON_OCR_API_KEY ใน environment ก่อนใช้งาน Typhoon OCR"
        )

    file_path = PDF_DIR / file_name

    # ใช้ PyMuPDF แปลงเป็นรูปภาพก่อน เพื่อหลีกเลี่ยงปัญหา Poppler missing บน Windows
    temp_image_path = convert_pdf_page_to_image(file_path, page_num)

    try:
        # ส่งรูปภาพไปให้ Typhoon OCR แทนไฟล์ PDF
        markdown = ocr_document(
            pdf_or_image_path=temp_image_path,
            # page_num ไม่จำเป็นต้องระบุเมื่อส่งเป็นรูปภาพเดี่ยว
            api_key=TYPHOON_OCR_API_KEY,
        )
    finally:
        # ลบไฟล์รูปภาพชั่วคราว
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)

    return markdown


# -----------------------------
# Tools ฝั่ง MCP
# -----------------------------
@mcp.tool()
def list_pdf_files() -> list[str]:
    """
    แสดงรายชื่อไฟล์ PDF ที่มีในโฟลเดอร์ data/pdf
    """
    if not PDF_DIR.exists():
        return []
    return [p.name for p in PDF_DIR.glob("*.pdf")]


@mcp.tool()
def ocr_pdf_to_markdown(
    file_name: str,
    page_num: int = 1,
) -> str:
    """
    ใช้ Typhoon OCR 1.5 แปลง PDF 1 หน้าให้เป็น Markdown/ข้อความ
    - file_name: ชื่อไฟล์ PDF ใน data/pdf
    - page_num: เลขหน้าที่ต้องการ OCR (เริ่มจาก 1)
    """
    return _ocr_logic(file_name, page_num)


@mcp.tool()
def summarize_pdf_with_llm(
    file_name: str,
    page_num: int = 1,
    extra_instruction: Optional[str] = None,
) -> str:
    """
    Workflow เต็ม: OCR PDF → ส่งเข้า LLM → ได้สรุป/วิเคราะห์กลับมา
    - file_name: ชื่อไฟล์ PDF ใน data/pdf
    - page_num: เลขหน้าที่ต้องการ OCR (เริ่มจาก 1)
    - extra_instruction: ถ้าอยากกำหนดรูปแบบสรุป เช่น
        "ช่วยสรุปเป็น bullet 5 ข้อและวิเคราะห์แนวโน้มยอดขาย"
    """
    # 1) OCR ด้วย Typhoon OCR
    markdown = _ocr_logic(file_name=file_name, page_num=page_num)

    # ถ้าข้อความยาวมาก อาจตัดความยาวก่อนส่งเข้า LLM
    if len(markdown) > 16000:
        markdown_to_use = markdown[:16000]
    else:
        markdown_to_use = markdown

    # 2) ส่งเข้า LLM ให้สรุป / วิเคราะห์
    summary = call_llm_for_summary(
        content=markdown_to_use,
        extra_instruction=extra_instruction,
        max_tokens=1024,
    )

    return summary


@mcp.tool()
def ocr_pdf_multi_page_and_summarize(
    file_name: str,
    start_page: int = 1,
    end_page: int = 3,
    extra_instruction: Optional[str] = None,
) -> str:
    """
    OCR PDF หลายหน้า (ช่วง start_page ถึง end_page) แล้วให้ LLM สรุป/วิเคราะห์รวม
    ใช้กรณีรายงานหลายหน้า เช่น Report ทั้งเดือน/ทั้งไตรมาส
    """
    if start_page < 1:
        raise ValueError("start_page ต้องมากกว่าหรือเท่ากับ 1")
    if end_page < start_page:
        raise ValueError("end_page ต้องมากกว่าหรือเท่ากับ start_page")

    # OCR ทีละหน้าแล้วต่อเป็นข้อความเดียว
    combined_markdown_parts: list[str] = []
    for page in range(start_page, end_page + 1):
        try:
            page_md = _ocr_logic(file_name=file_name, page_num=page)
            combined_markdown_parts.append(f"# หน้า {page}\n\n{page_md}")
        except Exception as e:
            combined_markdown_parts.append(f"# หน้า {page}\n\n(OCR ผิดพลาด: {e})")

    combined_markdown = "\n\n---\n\n".join(combined_markdown_parts)

    # ป้องกันยาวเกินไป
    if len(combined_markdown) > 20000:
        combined_markdown = combined_markdown[:20000]

    # เรียก LLM
    summary = call_llm_for_summary(
        content=combined_markdown,
        extra_instruction=extra_instruction,
        max_tokens=1500,
    )

    return summary


# -----------------------------
# main entry สำหรับรัน MCP Server
# -----------------------------
if __name__ == "__main__":
    # Run the MCP server with SSE transport on port 8000
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
