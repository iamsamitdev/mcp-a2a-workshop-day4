import logging
import sys
from fastmcp import FastMCP
import pandas as pd
from pathlib import Path

# ตั้งค่า Logging ให้แสดงผลที่ stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


# Initialize FastMCP instance
mcp = FastMCP("csv-tools")

# Define the data directory path
DATA_DIR = Path(__file__).parent / "data"


# --- Helper Function: แปลง NaN เป็น None เพื่อให้ JSON ไม่พัง ---
def clean_nans(data):
    """แปลงค่า NaN ใน DataFrame/Series ให้เป็น None เพื่อให้ส่ง JSON ได้ไม่ error"""
    if isinstance(data, (pd.DataFrame, pd.Series)):
        return data.where(pd.notnull(data), None)
    return data


# Tool to list all CSV files in the data directory
@mcp.tool()
def list_csv_files() -> list[str]:
    """แสดงรายชื่อไฟล์ CSV ที่พร้อมใช้งานในโฟลเดอร์ data"""
    logger.info(f"กำลังลิสต์ไฟล์ CSV ในโฟลเดอร์: {DATA_DIR}")
    # ตรวจสอบว่าโฟลเดอร์มีอยู่จริงก่อน glob
    if not DATA_DIR.exists():
        return []
    return [p.name for p in DATA_DIR.glob("*.csv")]


# Tool to summarize a specific CSV file
@mcp.tool()
def summarize_csv(file_name: str) -> dict:
    """
    สรุปข้อมูลไฟล์ CSV (จำนวนแถว, คอลัมน์, ตัวอย่างหัวตาราง, สถิติรวมของคอลัมน์ตัวเลข)
    """
    logger.info(f"กำลังสรุปข้อมูลจากไฟล์: {file_name}")
    file_path = DATA_DIR / file_name

    # เช็คว่ามีไฟล์จริงไหม
    if not file_path.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์ {file_name} ในโฟลเดอร์ data")

    df = pd.read_csv(file_path)

    return {
        "file": file_name,
        "shape": {"rows": int(df.shape[0]), "cols": int(df.shape[1])},
        "columns": list(df.columns),
        "head": clean_nans(df.head(5)).to_dict(orient="records"),
        "numeric_summary": clean_nans(df.describe(include="number")).to_dict(),
    }


# Tool to read rows with pagination
@mcp.tool()
def read_csv_rows(file_name: str, offset: int = 0, limit: int = 10) -> list[dict]:
    """อ่านข้อมูลจากไฟล์ CSV แบบระบุจำนวนแถว (Pagination)"""
    logger.info(f"กำลังอ่านข้อมูลจากไฟล์: {file_name}, offset={offset}, limit={limit}")
    file_path = DATA_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์ {file_name}")

    df = pd.read_csv(file_path)

    if offset >= len(df):
        return []

    # ตัดแถวที่ต้องการและ clean ค่าว่าง
    result_df = clean_nans(df.iloc[offset : offset + limit])
    return result_df.to_dict(orient="records")


# Tool to get unique values
@mcp.tool()
def get_unique_values(file_name: str, column_name: str) -> list:
    """ดึงค่าที่ไม่ซ้ำกัน (Unique values) จากคอลัมน์ที่ระบุ"""
    logger.info(f"กำลังดึงค่าที่ไม่ซ้ำกันจากไฟล์: {file_name}, คอลัมน์: {column_name}")
    file_path = DATA_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์ {file_name}")

    df = pd.read_csv(file_path)

    if column_name not in df.columns:
        raise ValueError(f"ไม่พบคอลัมน์ {column_name}")

    return df[column_name].dropna().unique().tolist()


# Tool to filter data using pandas query
@mcp.tool()
def filter_csv(file_name: str, query: str) -> list[dict]:
    """
    กรองข้อมูล CSV ด้วย query string (ใช้ syntax ของ pandas query)

    ตัวอย่างการใช้งาน:
    - "age > 25"
    - "department == 'Sales' and salary > 50000"
    - "product_name.str.contains('Pro', case=False)"
    """
    logger.info(f"กำลังกรองข้อมูลจากไฟล์: {file_name} ด้วย query: {query}")
    file_path = DATA_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์ {file_name}")

    df = pd.read_csv(file_path)

    try:
        result = df.query(query, engine="python")
        return clean_nans(result).to_dict(orient="records")
    except Exception as e:
        raise ValueError(f"Query Error: {str(e)}")


if __name__ == "__main__":
    # Run the MCP server with SSE transport on port 8000
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
