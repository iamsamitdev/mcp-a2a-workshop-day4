## Agentic AI MCP and A2A with FastMCP - DAY 2

### Download Trainging Document

[Click here to download the training document](https://drive.google.com/drive/folders/1PgOFXacZ-tOM7auvrIPLtOwrh-MkWxay?usp=sharing)

### 📋 Content

1. [สร้าง MCP Server ตัวแรกด้วย FastMCP โดยใช้การสื่อสารแบบ STDIO](#1.-สร้าง-MCP-Server-ตัวแรกด้วย-FastMCP-โดยใช้การสื่อสารแบบ-STDIO)
2. [ทดสอบการเชื่อม Claude Desktop เข้ากับ MCP ของเรา](#2.-ทดสอบการเชื่อม-Claude-Desktop-เข้ากับ-MCP-ของเรา)
3. [FastMCP Server SSE and HTTP Transports](#3-FastMCP-Server-SSE-and-HTTP-Transports)
4. [MCP Client SSE and HTTP Example](#4-MCP-Client-SSE-and-HTTP-Example)
5. [FastMCP Server with RESOURCES+PROMPTS+TOOLS](#5-FastMCP-Server-with-RESOURCESPROMPTSTOOLS)
6. [MCP Client with Generative AI Agent](#6-MCP-Client-with-Generative-AI-Agent)
7. [MCP Client RESOURCES+PROMPTS+TOOLS and Generative AI Agent](#7-MCP-Client-RESOURCESPROMPTSTOOLS-and-Generative-AI-Agent)
8. [ทดสอบการเชื่อม VSCode กับ MCP Server ของเรา](#8-ทดสอบการเชื่อม-VSCode-กับ-MCP-Server-ของเรา)


### 1. สร้าง MCP Server ตัวแรกด้วย FastMCP โดยใช้การสื่อสารแบบ STDIO
#### 1.1 สร้างไฟล์ server.py
สร้างไฟล์ชื่อ `server.py` ในโฟลเดอร์โปรเจกต์ของคุณ และเพิ่มโค้ดต่อไปนี้ลงไป:
```python
from fastmcp import FastMCP

# 1. สร้าง Server MCP instance
mcp = FastMCP("My Math Server")

# 2. สร้าง Tool (เครื่องมือ)
@mcp.tool()
# @mcp.tool(name="calculator_plus", description="บวกเลขจำนวนเต็มสองจำนวน")
def add_numbers(a: int, b: int) -> int:
    """บวกเลขจำนวนเต็มสองจำนวน"""
    return a + b

# กำหนดชื่อเครื่องมือเป็น "say_hello" แทนที่จะเป็น "greet"
# กำหนดคำอธิบายเป็นภาษาไทย
@mcp.tool(name="say_hello", description="ใช้สำหรับทักทายลูกค้าอย่างเป็นทางการ")
def greet(name: str) -> str:
    # """กล่าวทักทายผู้ใช้งาน"""
    return f"สวัสดีครับคุณ {name} ยินดีที่ได้รู้จัก!"

# 3. main entry สำหรับรัน MCP Server
if __name__ == "__main__":
    # รัน Server รอรับการเชื่อมต่อจาก Client
    # Run the MCP server with Standard IO (STDIO)
    mcp.run()
```

#### 1.2 รัน MCP Server
เปิดเทอร์มินัลหรือคอมมานด์พรอมต์ในโฟลเดอร์โปรเจกต์ของคุณ และรันคำสั่งต่อไปนี้เพื่อเริ่ม MCP Server:
```bash
uv run python server.py
```

#### 1.3 MCP Server ทำงานอย่างไร
เมื่อรันคำสั่ง `uv run python server.py` โปรแกรมจะเริ่มต้น MCP Server ที่รอรับการเชื่อมต่อจาก MCP Client ผ่านทาง STDIO (Standard Input/Output) โดยมีเครื่องมือ (Tools) ที่เราสร้างไว้ ได้แก่ `add_numbers` และ `greet` ซึ่งสามารถเรียกใช้งานผ่าน MCP Client ได้

### 2. ทดสอบการเชื่อม Claude Desktop เข้ากับ MCP ของเรา
#### 2.1 ติดตั้ง Claude Desktop
ดาวน์โหลดและติดตั้ง Claude Desktop จากลิงก์นี้: [Claude Desktop Releases](https://claude.com/download)

#### 2.2 ตั้งค่าเชื่อมต่อกับ MCP Server แบบ STDIO
1. เปิด Claude Desktop
2. ไปที่ Settings > Developer > Local MCP servers
3. คลิก "Edit Config"
4. เพิ่มการเชื่อมต่อใหม่โดยตั้งค่าดังนี้:

    ##### Windows path example
    ```json
    {
        "mcpServers": {
            "My Math Server": {
                "command": "C:\\path\\to\\your\\agentic-mcp-workshop\\ex1_server_host_client\\.venv\\Scripts\\python.exe",
                "args": [
                    "C:\\path\\to\\your\\agentic-mcp-workshop\\ex1_server_host_client\\server.py"
                ]
            },
        }
    }
    ```
    ##### MacOS / Linux path example
    ```json
    {
        "mcpServers": {
            "My Math Server": {
                "command": "/path/to/your/agentic-mcp-workshop/ex1_server_host_client/.venv/bin/python",
                "args": [
                    "/path/to/your/agentic-mcp-workshop/ex1_server_host_client/server.py"
                ]
            },
        }
    }
    ```

   - Name: My Math Server
   - Command: `uv run python path/to/your/server.py` (เปลี่ยน `path/to/your/server.py` เป็นเส้นทางที่แท้จริงของไฟล์ server.py ของคุณ)
5. บันทึกการตั้งค่า

#### 2.3 ทดสอบการเชื่อมต่อ
1. สร้างแชทใหม่ใน Claude Desktop
2. เลือกการเชื่อมต่อที่สร้างขึ้น (My Math Server)
3. ส่งข้อความทดสอบ เช่น:
   - "ลองบวกเลข 3 กับ 5 และฝากทักทายคุณ สมชาย ด้วย"
4. ตรวจสอบผลลัพธ์ที่ได้รับจาก MCP Server

#### 2.4 ทดสอบสร้าง MCP Client ด้วยโค้ด Python
สร้างไฟล์ชื่อ `client.py` ในโฟลเดอร์โปรเจกต์ของคุณ และเพิ่มโค้ดต่อไปนี้ลงไป:
```python
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
            result_greet = await session.call_tool("greet", arguments={"name": "Somchai"})
            print(f"📨 Server ตอบกลับ: {result_greet.content[0].text}")

if __name__ == "__main__":
    asyncio.run(run_host())
```
> ต้องติดตั้งไลบรารี `mcp` เพิ่มเติมด้วยคำสั่ง:
```bash
uv add mcp
```

#### 2.5 รัน MCP Client
เปิดเทอร์มินัลหรือคอมมานด์พรอมต์ในโฟลเดอร์โปรเจกต์ของคุณ และรันคำสั่งต่อไปนี้เพื่อเริ่ม MCP Client:
```bash
uv run python client.py
```
#### 2.6 MCP Client ทำงานอย่างไร
เมื่อรันคำสั่ง `uv run python client.py` โปรแกรมจะเริ่มต้น MCP Client ที่เชื่อมต่อกับ MCP Server ผ่านทาง STDIO (Standard Input/Output) โดยมีขั้นตอนดังนี้:
1. กำหนดค่า Server ที่จะเชื่อมต่อ
2. เริ่มต้น Client และเชื่อมต่อกับ Server
3. ส่งคำสั่งให้ Server ทำงานผ่านเครื่องมือ (Tools) ที่มีอยู่

### 3. FastMCP Server SSE and HTTP Transports
#### 3.1 สร้างไฟล์ server_sse_http.py
สร้างไฟล์ชื่อ `server_sse_http.py` ในโฟลเดอร์โปรเจกต์ของคุณ และเพิ่มโค้ดต่อไปนี้ลงไป:
```python
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


# 2. สร้าง Tool (เครื่องมือ)
# กำหนดชื่อเครื่องมือเป็น "calculator_plus" แทนที่จะเป็น "add_numbers"
@mcp.tool(name="calculator_plus")
def add_numbers(a: int, b: int) -> int:
    """บวกเลขจำนวนเต็มสองจำนวน"""
    logger.info(f"กำลังคำนวณ: {a} + {b}") # บันทึก Log ลงใน Console
    return a + b


# กำหนดชื่อและคำอธิบายใหม่ (ไม่ใช้ Docstring)
@mcp.tool(name="say_hello", description="ใช้สำหรับทักทายลูกค้าอย่างเป็นทางการ")
def greet(name: str) -> str:
    # """กล่าวทักทายผู้ใช้งาน"""
    logger.info(f"กำลังทักทายคุณ: {name}") # บันทึก Log ลงใน Console
    return f"สวัสดีครับคุณ {name} ยินดีที่ได้รู้จัก!"


# 3. main entry สำหรับรัน MCP Server
if __name__ == "__main__":
    # รัน Server รอรับการเชื่อมต่อจาก Client
    # Run the MCP server with SSE transport on port 8000
    mcp.run(transport="sse", host="0.0.0.0", port=8000)

    # Run the MCP server with HTTP transport on port 8000
    # mcp.run(transport="http", host="127.0.0.1", port=8000)
```
#### 3.2 รัน MCP Server SSE
เปิดเทอร์มินัลหรือคอมมานด์พรอมต์ในโฟลเดอร์โปรเจกต์ของคุณ และรันคำสั่งต่อไปนี้เพื่อเริ่ม
MCP Server SSE:
```bash
uv run python server_sse_http.py
```

#### 3.4 ตั้งค่าเชื่อมต่อกับ MCP Server แบบ SSE ใน Claude Desktop
1. เปิด Claude Desktop
2. ไปที่ Settings > Developer > Local MCP servers
3. คลิก "Edit Config"
4. เพิ่มการเชื่อมต่อใหม่โดยตั้งค่าดังนี้:
    ```json
    {
        "mcpServers": {
            "My Math Server SSE HTTP": {
                "command": "npx",
                "args": [   
                    "-y",
                    "mcp-remote",
                    "http://127.0.0.1:8000/sse",
                    "--allow-http"
                ]
            }
        }
    }
    ```
   - Name: My Math Server SSE
   - URL: `http://localhost:8000/sse`
5. บันทึกการตั้งค่า

### 4. MCP Client SSE and HTTP Example
#### 4.1 สร้างไฟล์ client_sse_http.py
สร้างไฟล์ชื่อ `client_sse_http.py` ในโฟลเดอร์โปรเจกต์ของคุณ และเพิ่มโค้ดต่อไปนี้ลงไป:
```python
import asyncio
from mcp import ClientSession        # <-- นี่คือเครื่องมือของ Client
from mcp.client.sse import sse_client # <-- นี่คือเครื่องมือของ Client

async def run_host():
    
    # --- ส่วนที่เป็น HOST (สมอง) ---
    # Host ตัดสินใจว่า "ฉันจะไปคุยกับ Server ที่ URL นี้นะ"
    server_url = "http://localhost:8000/sse"
    print(f"🔌 Host: กำลังเชื่อมต่อ...")

    # --- ส่วนที่เป็น CLIENT (ปาก/ท่อส่งข้อมูล) ---
    # เรียกใช้กลไก Client เพื่อเชื่อมต่อ
    async with sse_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # --- กลับมาเป็นส่วนของ HOST (สมอง) ---
            # Host สั่ง: "ขอดูเมนูหน่อย (List tools)"
            tools = await session.list_tools()
            print(f"🛠️ Host: เจอเครื่องมือแล้ว -> {[t.name for t in tools.tools]}")

            # Host สั่ง: "ฉันอยากบวกเลข 50+50 จัดการให้หน่อย"
            print("\n🤖 Host: สั่งให้บวกเลข...")
            
            # --- ส่วนที่เป็น CLIENT (ปาก) ---
            # Client รับคำสั่งจาก Host แล้ววิ่งไปคุยกับ Server
            result = await session.call_tool("calculator_plus", arguments={"a": 50, "b": 50})
            
            # --- กลับมาเป็นส่วนของ HOST (สมอง) ---
            # Host รับผลลัพธ์มาแสดงผล
            print(f"📨 Host: ได้รับคำตอบคือ {result.content[0].text}")

            # --- ส่วนที่เป็น CLIENT (ปาก) ---
            # Client รับคำสั่งจาก Host แล้ววิ่งไปคุยกับ Server
            print("\n🤖 Host: สั่งให้ทักทาย...")
            result = await session.call_tool("say_hello", arguments={"name": "Somchai"})

            # --- กลับมาเป็นส่วนของ HOST (สมอง) ---
            # Host รับผลลัพธ์มาแสดงผล
            print(f"📨 Host: ได้รับคำตอบคือ {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(run_host())
```

#### 4.2 รัน MCP Client SSE
เปิดเทอร์มินัลหรือคอมมานด์พรอมต์ในโฟลเดอร์โปรเจกต์ของคุณ และรันคำสั่งต่อไปนี้เพื่อเริ่ม MCP Client SSE:
```bash
uv run python client_sse_http.py
```

### 5. FastMCP Server with RESOURCES+PROMPTS+TOOLS
##### 5.1 สร้างไฟล์ server_resources_prompts_tools.py
สร้างไฟล์ชื่อ `server_resources_prompts_tools.py` ในโฟลเดอร์โปรเจกต์ของคุณ และเพิ่มโค้ดต่อไปนี้ลงไป:
```python
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
```

#### 5.2 รัน MCP Server RESOURCES+PROMPTS+TOOLS
เปิดเทอร์มินัลหรือคอมมานด์พรอมต์ในโฟลเดอร์โปรเจกต์ของคุณ และรันคำสั่งต่อไปนี้เพื่อเริ่ม MCP Server RESOURCES+PROMPTS+TOOLS:
```bash
uv run python server_resources_prompts_tools.py
```

### 6. MCP Client with Generative AI Agent
#### 6.1 ติดตั้งไลบรารีที่จำเป็น
ก่อนอื่นให้ติดตั้งไลบรารี `python-dotenv`, `mcp` และ `openai` ด้วยคำสั่ง:
```bash
uv add python-dotenv mcp openai
```

#### 6.2 ตั้งค่า OpenAI API Key
สร้างไฟล์ชื่อ `.env` ในโฟลเดอร์โปรเจกต์ของคุณ และเพิ่มบรรทัดต่อไปนี้ลงไป (เปลี่ยน `your_openai_api_key` เป็นคีย์จริงของคุณ):
```env
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_API_KEY="your_openai_api_key"
export LLM_MODEL="gpt-4o-mini"
```

#### 6.3 สร้างไฟล์ client_generative_agent.py
สร้างไฟล์ชื่อ `client_generative_agent.py` ในโฟลเดอร์โปรเจกต์ของคุณ และเพิ่มโค้ดต่อไปนี้ลงไป:
```python
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
```

#### 6.4 รัน MCP Server SSE
เปิดเทอร์มินัลหรือคอมมานด์พรอมต์ในโฟลเดอร์โปรเจกต์ของคุณ และรันคำสั่งต่อไปนี้เพื่อเริ่ม MCP Server SSE:
```bash
uv run python server_sse_http.py
```

#### 6.5 รัน MCP Client with Generative AI Agent
เปิดเทอร์มินัลหรือคอมมานด์พรอมต์ในโฟลเดอร์โปรเจกต์ของคุณ และรันคำสั่งต่อไปนี้เพื่อเริ่ม MCP Client with Generative AI Agent:
```bash
uv run python client_generative_agent.py
```

### 7. MCP Client RESOURCES+PROMPTS+TOOLS and Generative AI Agent
#### 7.1 สร้างไฟล์ client_resources_prompts_tools_agent.py
สร้างไฟล์ชื่อ `client_resources_prompts_tools_agent.py` ในโฟลเดอร์โปรเจกต์ของคุณ และเพิ่มโค้ดต่อไปนี้ลงไป:
```python
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
MODEL_NAME = os.getenv("LLM_MODEL", "gpt-4o")
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
```
#### 7.2 รัน MCP Server RESOURCES+PROMPTS+TOOLS
เปิดเทอร์มินัลหรือคอมมานด์พรอมต์ในโฟลเดอร์โปรเจกต์ของคุณ และรันคำสั่งต่อไปนี้เพื่อเริ่ม MCP Server RESOURCES+PROMPTS+TOOLS:
```bash
uv run python server_resources_prompts_tools.py
```

#### 7.3 รัน MCP Client RESOURCES+PROMPTS+TOOLS and Generative AI Agent
เปิดเทอร์มินัลหรือคอมมานด์พรอมต์ในโฟลเดอร์โปรเจกต์ของคุณ และรันคำสั่งต่อไปนี้เพื่อเริ่ม MCP Client RESOURCES+PROMPTS+TOOLS and Generative AI Agent:
```bash
uv run python client_resources_prompts_tools_agent.py
```

### 8. ทดสอบการเชื่อม VSCode กับ MCP Server ของเรา

#### 8.2 รัน MCP Server SSE
เปิดเทอร์มินัลหรือคอมมานด์พรอมต์ในโฟลเดอร์โปรเจกต์ของคุณ และรันคำสั่งต่อไปนี้เพื่อเริ่ม MCP Server SSE:
```bash
uv run python server_sse_http.py
```

#### 8.2 สร้าง config ใน VSCode
1. สร้างไฟล์ `.vscode/mcp.json` ในโฟลเดอร์โปรเจกต์ของคุณ และเพิ่มโค้ดต่อไปนี้ลงไป:
```json
{
    "servers": {
        "My Math Server": {
            "command": "npx",
            "args": [
                "-y",
                "mcp-remote",
                "http://127.0.0.1:8000/sse"
            ]
        }
    }
}
```
2. เปิดไฟล์ที่ต้องการใช้ MCP Agent ใน VSCode
3. กด `Ctrl+Shift+P` (หรือ `Cmd+Shift+P` บน Mac) เพื่อเปิด Command Palette
4. พิมพ์ `Claude: Connect to MCP Server` แล้วเลือกการเชื่อมต่อที่สร้างขึ้น (My Math Server)
5. เริ่มแชทกับ MCP Agent ได้เลย!