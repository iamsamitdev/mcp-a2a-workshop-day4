import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_host():
    # 1. กำหนดค่า Server ที่เราจะเชื่อมต่อ (บอก Host ว่า Server อยู่ไหน)
    server_params = StdioServerParameters(
        command=sys.executable, # ใช้ Python ตัวปัจจุบัน
        args=["server.py"],     # รันไฟล์ server.py
        env=None                # กำหนด Environment variables ถ้าจำเป็น
    )

    print("🔌 กำลังเชื่อมต่อกับ Server...")

    # 2. เริ่มต้น Client (เชื่อมต่อแบบ Stdio)
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            # 3. Initialize (จับมือทักทายกับ Server)
            await session.initialize()
            print("✅ เชื่อมต่อสำเร็จ!")

            # 4. List Tools (ถาม Server ว่า "นายทำอะไรได้บ้าง?")
            tools = await session.list_tools()
            print(f"\n 🛠️ พบเครื่องมือทั้งหมด {len(tools.tools)} รายการ:")
            for tool in tools.tools:
                print(f" - {tool.name}: {tool.description}")

            # 5. Call Tool (ลองสั่งงาน Server)
            print("\n🤖 Host: กำลังสั่งให้บวกเลข 10 + 20...")
            result_add = await session.call_tool("add_numbers", arguments={"a": 10, "b": 20})
            print(f"📨 Server ตอบกลับ: {result_add.content[0].text}")

            print("\n🤖 Host: กำลังสั่งให้ทักทาย...")
            result_greet = await session.call_tool("say_hello", arguments={"name": "Somchai"})
            print(f"📨 Server ตอบกลับ: {result_greet.content[0].text}")

if __name__ == "__main__":
    asyncio.run(run_host())