import logging
import sys
from fastmcp import FastMCP

# ตั้งค่า Logging ให้แสดงผลที่ stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mcp-server")

# 1. สร้าง Server MCP instance
mcp = FastMCP("My Math Server")


# 2. สร้าง Tool (เครื่องมือ) สำหรับการบวกเลข
@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """บวกเลขจำนวนเต็มสองจำนวน"""
    logger.info(f"กำลังคำนวณ: {a} + {b}") # บันทึก Log ลงใน Console
    return a + b


@mcp.tool(name="say_hello", description="ใช้สำหรับทักทายลูกค้าอย่างเป็นทางการ")
def greet(name: str) -> str:
    logger.info(f"กำลังทักทายคุณ: {name}") # บันทึก Log ลงใน Console
    return f"สวัสดีครับ/ค่ะ, {name} ยินดีที่ได้รู้จัก!"


# 3. main entry สำหรับรัน MCP Server
if __name__ == "__main__":
    # รัน Server รอรับการเชื่อมต่อจาก Client
    # Run the MCP server with Standard IO (STDIO)
    mcp.run()
