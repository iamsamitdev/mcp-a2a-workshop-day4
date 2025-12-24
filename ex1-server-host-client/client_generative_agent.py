import asyncio
import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp import ClientSession
from mcp.client.sse import sse_client


# 1. โหลด Config จาก .env
load_dotenv()
API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL")
MODEL_NAME = os.getenv("LLM_MODEL", "gpt-4o-mini")
SERVER_URL = "http://localhost:8000/sse"

# สร้าง OpenAI Client
openai_client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)

async def run_agent(user_query: str):
    print(f"🔌 เชื่อมต่อ MCP Server: {SERVER_URL}...")
    
    # เชื่อมต่อกับ MCP Server
    async with sse_client(SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 2. ดึงรายการ Tools จาก MCP Server
            mcp_tools = await session.list_tools()
            
            # 3. แปลง Tools ของ MCP ให้เป็น Format ที่ OpenAI เข้าใจ
            openai_tools = []
            for tool in mcp_tools.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema # MCP ใช้ JSON Schema อยู่แล้ว โยนใส่ได้เลย!
                    }
                })
            
            print(f"🛠️  AI รู้จักเครื่องมือ: {[t['function']['name'] for t in openai_tools]}")

            # 4. เริ่มคุยกับ AI (ส่ง System prompt + User query)
            messages = [
                {"role": "system", "content": "คุณเป็นผู้ช่วยที่มีความสามารถในการใช้เครื่องมือภายนอกได้"},
                {"role": "user", "content": user_query}
            ]

            print(f"🤖 User: {user_query}")
            
            # ส่งให้ OpenAI ตัดสินใจ (รอบแรก)
            response = await openai_client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=openai_tools,
                tool_choice="auto" # ให้ AI เลือกเองว่าจะใช้ Tool ไหม
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # 5. ตรวจสอบว่า AI ต้องการเรียกใช้ Tool หรือไม่?
            if tool_calls:
                print(f"🤔 AI ตัดสินใจเรียกใช้ Tool: {len(tool_calls)} รายการ")
                
                # เพิ่มข้อความตอบกลับของ AI (ที่มี tool_calls) ลงในประวัติ เพื่อให้ Context ต่อเนื่อง
                messages.append(response_message)

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"🚀 กำลังรัน: {function_name} ด้วยค่า {function_args}")
                    
                    # --- เรียกใช้ MCP Tool ของจริงที่ Server ---
                    result = await session.call_tool(function_name, arguments=function_args)
                    tool_output = result.content[0].text
                    print(f"✅ ผลลัพธ์จาก Server: {tool_output}")

                    # เพิ่มผลลัพธ์กลับเข้าไปในประวัติการคุย (Role: tool)
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_output,
                    })

                # 6. ส่งข้อมูลทั้งหมดกลับให้ OpenAI สรุปผลครั้งสุดท้าย
                final_response = await openai_client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages
                )
                print(f"\n📢 AI ตอบสรุป:\n{final_response.choices[0].message.content}")
            
            else:
                # ถ้า AI ไม่เรียก Tool ก็ตอบข้อความธรรมดา
                print(f"\n📢 AI ตอบ:\n{response_message.content}")

if __name__ == "__main__":
    # ลองเปลี่ยนคำถามตรงนี้ได้เลยครับ
    # เช่น "บวกเลข 50 กับ 25 ให้หน่อย" หรือ "ช่วยทักทายคุณสมชายหน่อย"
    query = "ช่วยบวกเลข 1234 กับ 5678 ให้หน่อย แล้วก็ทักทายคุณสมหญิงด้วย"
    asyncio.run(run_agent(query))