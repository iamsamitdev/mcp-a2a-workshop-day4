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

# สร้าง Server
mcp = FastMCP("Super Server")

# --- 1. RESOURCES (สำหรับให้ AI อ่านข้อมูล) ---
@mcp.resource("system://logs")
def get_recent_logs() -> str:
    """ดึง Log 3 บรรทัดล่าสุด (สมมติ)"""
    logger.info("ดึง Log 3 บรรทัดล่าสุด")
    return "[INFO] System started\n[WARN] High memory usage\n[ERROR] Database timeout"

# --- 2. PROMPTS (สำหรับช่วย User ตั้งคำถาม) ---
@mcp.prompt()
def debug_assistant(log_type: str = "error") -> str:
    """แม่แบบคำสั่งให้ AI ช่วย Debug ตามประเภท Log"""
    logger.info(f"สร้าง Prompt สำหรับตรวจสอบ Log ประเภท: {log_type}")
    return f"ฉันต้องการให้คุณตรวจสอบ System Log ประเภท '{log_type}' และช่วยวิเคราะห์หาสาเหตุของปัญหา พร้อมแนะนำวิธีแก้ปัญหาทีละขั้นตอน"

# --- 3. TOOLS (สำหรับให้ AI ลงมือทำ) ---
@mcp.tool()
def restart_service(service_name: str) -> str:
    """สั่งรีสตาร์ทบริการ (Action)"""
    logger.info(f"สั่งรีสตาร์ทบริการ: {service_name}")
    # ในความเป็นจริงตรงนี้คือโค้ดสั่ง restart docker หรือ service จริงๆ
    return f"✅ ทำการ Restart บริการ {service_name} เรียบร้อยแล้ว!"

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)