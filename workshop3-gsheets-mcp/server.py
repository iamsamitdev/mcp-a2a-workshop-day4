from fastmcp import FastMCP
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials

# -----------------------------
# ตั้งค่า FastMCP
# -----------------------------
mcp = FastMCP("sheets-tools")

# -----------------------------
# ตั้งค่า Google Sheets API
# -----------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CRED_FILE = Path("service_account.json")

# -----------------------------
# ฟังก์ชันช่วยเหลือ: สร้าง gspread client
# -----------------------------
def get_client():
    if not CRED_FILE.exists():
        raise FileNotFoundError("ไม่พบ service_account.json")
    creds = Credentials.from_service_account_file(str(CRED_FILE), scopes=SCOPES)
    return gspread.authorize(creds)


# -----------------------------
# MCP Tools สำหรับจัดการ Google Sheets
# -----------------------------

# Tools สำหรับแสดงรายชื่อ Worksheets
@mcp.tool()
def list_worksheets(spreadsheet_id: str) -> list[str]:
    """
    แสดงรายชื่อ Worksheet (Tabs) ทั้งหมดที่มีใน Google Sheet นี้
    """
    client = get_client()
    sh = client.open_by_key(spreadsheet_id)
    # ดึงชื่อของทุก Worksheet ออกมาเป็น list
    return [ws.title for ws in sh.worksheets()]


# Tools สำหรับอ่านข้อมูลจาก Google Sheet
@mcp.tool()
def read_sheet(
    spreadsheet_id: str,
    worksheet_name: str,
    limit: int = 20,
) -> list[dict]:
    """
    อ่านข้อมูลจาก Google Sheet แล้วแปลงเป็น list ของ dict
    """
    client = get_client()
    sh = client.open_by_key(spreadsheet_id)

    try:
        ws = sh.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        raise ValueError(f"ไม่พบ worksheet ชื่อ '{worksheet_name}'")

    rows = ws.get_all_records()
    if limit > 0:
        rows = rows[:limit]

    return rows


# Tools สำหรับเพิ่มแถวข้อมูลใหม่ลงใน Google Sheet
@mcp.tool()
def append_row(
    spreadsheet_id: str,
    worksheet_name: str,
    row_data: dict,
) -> str:
    """
    เพิ่มข้อมูล 1 แถวลงใน Google Sheet (ใช้ header ของชีตเป็น key)
    """
    client = get_client()
    sh = client.open_by_key(spreadsheet_id)

    try:
        ws = sh.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        raise ValueError(f"ไม่พบ worksheet ชื่อ '{worksheet_name}'")

    header = ws.row_values(1)
    values: list[str] = [str(row_data.get(h, "")) for h in header]

    ws.append_row(values)

    return "เพิ่มข้อมูลเรียบร้อยแล้ว"


# -----------------------------
# main entry สำหรับรัน MCP Server
# -----------------------------
if __name__ == "__main__":
    # Run the MCP server with SSE transport on port 8000
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
