import asyncio
import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.types import CallToolResult

# โหลดค่า Config
load_dotenv()
API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL")
MODEL_NAME = os.getenv("LLM_MODEL", "gpt-4o-mini")
SERVER_URL = "http://localhost:8000/sse"

client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)

async def run_complete_agent():
    print(f"🔌 เชื่อมต่อ MCP Server: {SERVER_URL}...")
    
    async with sse_client(SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # ==========================================
            # 1. จัดการ PROMPTS (จำลอง User เลือกเมนู)
            # ==========================================
            print("\n--- 1. Loading Prompts ---")
            # ขอดูว่า Server มี Prompt อะไรบ้าง
            prompts = await session.list_prompts()
            target_prompt_name = "debug_assistant"
            
            # ดึงข้อความ Prompt มาใช้งาน (ใส่ argument ตามที่ Server กำหนด)
            prompt_result = await session.get_prompt(
                target_prompt_name, 
                arguments={"log_type": "error"}
            )
            
            # ข้อความเริ่มต้นที่ได้จาก Server
            initial_instruction = prompt_result.messages[0].content.text
            print(f"📝 Prompt Selected: {target_prompt_name}")
            print(f"📜 Instruction: {initial_instruction}")

            # ==========================================
            # 2. จัดการ RESOURCES (อ่านข้อมูลดิบ)
            # ==========================================
            print("\n--- 2. Loading Resources ---")
            # ในสถานการณ์จริง AI หรือ User อาจเป็นคนเลือก Resource เอง
            # แต่ในที่นี้เราจะดึงมาใส่ Context ให้เลย
            resource_uri = "system://logs"
            resource_content = await session.read_resource(resource_uri)
            log_data = resource_content.contents[0].text
            
            print(f"📦 Resource Loaded: {resource_uri}")
            print(f"📄 Content Preview: {log_data.replace(chr(10), ' | ')}")

            # ==========================================
            # 3. เตรียม TOOLS และ CONTEXT ให้ AI
            # ==========================================
            print("\n--- 3. AI Processing ---")
            
            # ดึงรายการ Tools
            mcp_tools = await session.list_tools()
            openai_tools = [{
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema
                }
            } for t in mcp_tools.tools]

            # สร้างประวัติการคุย (รวม Prompt + Resource + Instruction)
            messages = [
                {"role": "system", "content": "คุณเป็นผู้ดูแลระบบที่เชี่ยวชาญ (System Admin)"},
                # ใส่ Instruction จาก Prompt
                {"role": "user", "content": initial_instruction}, 
                # แนบข้อมูลจาก Resource ไปด้วย เพื่อให้ AI มีข้อมูลวิเคราะห์
                {"role": "user", "content": f"นี่คือข้อมูล Log ล่าสุดจาก {resource_uri}:\n\n{log_data}"}
            ]

            # ==========================================
            # 4. ลูปการทำงานของ AI (Think -> Act)
            # ==========================================
            # ส่งให้ OpenAI
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=openai_tools,
                tool_choice="auto"
            )
            
            ai_msg = response.choices[0].message
            
            # ถ้า AI อยากใช้ Tool (เช่น อยาก Restart Service)
            if ai_msg.tool_calls:
                print(f"🤔 AI วิเคราะห์แล้วตัดสินใจใช้เครื่องมือ...")
                messages.append(ai_msg) # เก็บประวัติ

                for tool_call in ai_msg.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)
                    
                    print(f"🚀 Executing Tool: {func_name} with {func_args}")
                    
                    # เรียกใช้ Tool จริงที่ Server
                    result: CallToolResult = await session.call_tool(func_name, arguments=func_args)
                    tool_output = result.content[0].text
                    
                    print(f"✅ Tool Output: {tool_output}")
                    
                    # ส่งผลลัพธ์กลับไปให้ AI
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": tool_output
                    })

                # ให้ AI สรุปผลครั้งสุดท้าย
                final_res = await client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages
                )
                print(f"\n📢 AI Final Response:\n{final_res.choices[0].message.content}")
            else:
                print(f"\n📢 AI Response:\n{ai_msg.content}")

if __name__ == "__main__":
    asyncio.run(run_complete_agent())