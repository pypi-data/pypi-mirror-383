import os
import aiohttp
import zipfile
import io
import uuid
import random
import json
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Sequence
import logging

# --- File Logging Setup ---
log_file = Path(__file__).parent.parent.parent / "mcp_server_debug.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=str(log_file),
    filemode='w'
)
logging.info("--- Server script started ---")
# --- End Logging Setup ---


from mcp.server import Server
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from fastapi.responses import FileResponse
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.shared.exceptions import McpError

# --- 核心逻辑 ---

NOVELAI_API_CONFIG = {
    "BASE_URL": "https://image.novelai.net",
    "IMAGE_GENERATION_ENDPOINT": "/ai/generate-image",
    "DEFAULT_PARAMS": {
        "model": "nai-diffusion-4-5-full",
        "parameters": {
            "steps": 23,
            "scale": 5,
            "sampler": "k_euler_ancestral",
            "n_samples": 1,
            "ucPreset": 0,
            "qualityToggle": True,
            "params_version": 3,
            "noise_schedule": "karras",
            "prefer_brownian": True,
            "add_original_image": False,
            "autoSmea": False,
            "cfg_rescale": 0,
            "controlnet_strength": 1,
            "deliberate_euler_ancestral_bug": False,
            "dynamic_thresholding": False,
            "legacy": False,
            "legacy_uc": False,
            "legacy_v3_extend": False,
            "normalize_reference_strength_multiple": True,
            "skip_cfg_above_sigma": None,
            "use_coords": False,
        },
        "DEFAULT_NEGATIVE_PROMPT": "lowres, artistic error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, dithering, halftone, screentone, multiple views, logo, too many watermarks, negative space, blank page",
        "DEFAULT_ARTIST_STRING": "artist:ekita_kuro,[[[artist:yoneyama_mai]]],artist:toosaka_asagi,{{artist:syagamu}},{{{artist:momoko_(momopoco)}}},artist:drawdream1025",
    },
}
async def generate_image_from_novelai(args: Dict[str, Any], api_key: str) -> (str | None, list[str]):
    """
    根据参数调用 NovelAI API 生成图片, 保存后返回文件名。
    :return: 一个元组，包含 (文件名, 调试消息列表)
    """
    debug_messages = ["[DEBUG] Starting image generation..."]
    
    
    # --- 读取配置 ---
    proxy_server = os.environ.get("PROXY_SERVER", "http://127.0.0.1:7897")
    project_base_path = os.environ.get("PROJECT_BASE_PATH", ".")
    server_port = os.environ.get("SERVER_PORT", "8000")
    image_key = os.environ.get("IMAGESERVER_IMAGE_KEY", "your-secret-key")
    var_http_url = os.environ.get("VarHttpUrl", "http://127.0.0.1")
    var_https_url = os.environ.get("VarHttpsUrl")
    debug_mode = True # Force debug mode
    debug_messages.append(f"[DEBUG] PROXY_SERVER: {proxy_server}")
    debug_messages.append(f"[DEBUG] PROJECT_BASE_PATH: {project_base_path}")


    # --- 参数校验和处理 ---
    debug_messages.append(f"[DEBUG] Received arguments: {args}")
    prompt = args.get("prompt")
    resolution = args.get("resolution")
    if not prompt or not isinstance(prompt, str) or not prompt.strip():
        return None, debug_messages + [f"ValueError: 参数 'prompt' 不能为空。"]
    if not resolution or not isinstance(resolution, str):
        return None, debug_messages + [f"ValueError: 参数 'resolution' 不能为空。"]
    
    try:
        width_str, height_str = resolution.split('x')
        width, height = int(width_str.strip()), int(height_str.strip())
    except ValueError:
        return None, debug_messages + [f"ValueError: 参数 'resolution' 格式不正确，应为 '宽x高'，例如 '1024x1024'。"]

    # --- 构建请求 ---
    effective_negative_prompt = args.get("negative_prompt") or NOVELAI_API_CONFIG["DEFAULT_PARAMS"]["DEFAULT_NEGATIVE_PROMPT"]
    # Add the artist string to the prompt, same as the JS version
    artist_string = NOVELAI_API_CONFIG["DEFAULT_PARAMS"]["DEFAULT_ARTIST_STRING"]
    final_prompt = f"{prompt}, {artist_string}"
    debug_messages.append(f"[DEBUG] Final prompt: {final_prompt[:300]}...")
    debug_messages.append(f"[DEBUG] Negative prompt: {effective_negative_prompt[:300]}...")

    # Replicate the exact payload structure from the working JS plugin
    payload = {
        "action": "generate",
        "model": NOVELAI_API_CONFIG["DEFAULT_PARAMS"]["model"],
        "input": final_prompt,
        "parameters": {
            **NOVELAI_API_CONFIG["DEFAULT_PARAMS"]["parameters"],
            "width": width,
            "height": height,
            "seed": random.randint(0, 4294967295),
            "negative_prompt": effective_negative_prompt,
            # Add the required v4 structures
            "v4_prompt": {
                "caption": {"base_caption": final_prompt, "char_captions": []},
                "use_coords": False,
                "use_order": True,
            },
            "v4_negative_prompt": {
                "caption": {"base_caption": effective_negative_prompt, "char_captions": []},
                "legacy_uc": False,
            },
        },
    }
    
    debug_messages.append(f"[DEBUG] Final payload: {json.dumps(payload, indent=2)}")

    # --- 发送请求 ---
    debug_messages.append(f"[DEBUG] Preparing to send request to NovelAI API...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(
            f"{NOVELAI_API_CONFIG['BASE_URL']}{NOVELAI_API_CONFIG['IMAGE_GENERATION_ENDPOINT']}",
            json=payload,
            proxy=proxy_server if proxy_server and proxy_server.strip() else None,
            timeout=180.0
        ) as response:
            debug_messages.append(f"[DEBUG] Received response, status: {response.status}, content-type: {response.headers.get('content-type')}")

            # --- 处理响应 ---
            content_type = response.headers.get('content-type', '')
            is_zip_response = 'application/zip' in content_type or 'octet-stream' in content_type

            if response.status != 200 or not is_zip_response:
                error_text = await response.text()
                debug_messages.append(f"[ERROR] NovelAI API Error: {error_text}")
                return None, debug_messages

            debug_messages.append(f"[DEBUG] Reading response bytes...")
            response_bytes = await response.read()
            debug_messages.append(f"[DEBUG] Read {len(response_bytes)} bytes from response.")

    # --- 解压并保存图片 ---
    debug_messages.append(f"[DEBUG] Preparing to process ZIP file from response bytes...")
    novelai_image_dir = Path(project_base_path) / "image" / "novelaigen"
    novelai_image_dir.mkdir(parents=True, exist_ok=True)
    
    saved_images = []
    with io.BytesIO(response_bytes) as zip_buffer:
        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
            debug_messages.append(f"[DEBUG] ZIP contents: {zip_ref.namelist()}")
            for file_info in zip_ref.infolist():
                if file_info.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    # 保存并返回第一张找到的图片的文件名
                    debug_messages.append(f"[DEBUG] Found image: {file_info.filename}")
                    image_bytes = zip_ref.read(file_info.filename)
                    
                    # 生成唯一文件名并保存
                    saved_filename = f"{uuid.uuid4()}.png"
                    save_path = novelai_image_dir / saved_filename
                    with open(save_path, "wb") as f:
                        f.write(image_bytes)
                    
                    debug_messages.append(f"[DEBUG] Image extracted and saved to {save_path}")
                    return saved_filename, debug_messages

    debug_messages.append("[ERROR] No valid image found in the returned ZIP file.")
    return None, debug_messages

# --- MCP 服务器实现 ---

app = FastAPI()
server = Server("mcp-novelaigen")
api_key = os.environ.get("NOVELAI_API_KEY")

class ToolCallRequest(BaseModel):
    name: str
    arguments: dict

# --- 新增图片服务路由 ---
@app.get("/images/novelaigen/{filename}")
async def get_image(filename: str):
    """Serve a previously generated image."""
    project_base_path = os.environ.get("PROJECT_BASE_PATH", ".")
    image_path = Path(project_base_path) / "image" / "novelaigen" / filename
    if not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found.")
    return FileResponse(str(image_path))

@app.get("/tools", response_model=List[Tool])
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="NovelAIGen",
            description="Generates an image using NovelAI.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "核心【英文】提示词。请严格遵循文档中的工作流和语法规则。",
                    },
                    "resolution": {
                        "type": "string",
                        "description": "图片分辨率，例如 '1024x1024'。默认为 '832x1216'。",
                    },
                    "negative_prompt": {
                        "type": "string",
                        "description": "反向提示词(UC)。用于避免不希望出现的特征。",
                    },
                },
                "required": ["prompt", "resolution"],
            },
        )
    ]

@app.post("/tools/call", response_model=Sequence[TextContent | ImageContent | EmbeddedResource])
async def call_tool(
    request: ToolCallRequest
) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for NovelAI image generation."""
    if request.name != "NovelAIGen":
        raise HTTPException(status_code=404, detail=f"Unknown tool: {request.name}")

    if not api_key:
        raise HTTPException(status_code=500, detail="服务器配置错误: 环境变量 NOVELAI_API_KEY 未设置。")

    saved_filename, debug_logs = await generate_image_from_novelai(request.arguments, api_key)
    
    log_text = "\n".join(debug_logs)

    if saved_filename:
        # 从环境变量构建基础URL
        var_http_url = os.environ.get("VarHttpUrl", "http://127.0.0.1")
        server_port = os.environ.get("SERVER_PORT", "8000")
        # 确保基础URL没有尾部斜杠
        base_url = f"{var_http_url.rstrip('/')}:{server_port}"
        
        image_url = f"{base_url}/images/novelaigen/{saved_filename}"
        logging.info(f"Generated image URL: {image_url}")
        return [TextContent(type="text", text=image_url)]
    else:
        error_message = f"Failed to generate image. See logs for details.\n\n--- DEBUG LOGS ---\n{log_text}"
        return [TextContent(type="text", text=error_message)]

async def serve() -> None:
    logging.info("Entering serve() function.")
    try:
        logging.info("Starting FastAPI server.")
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
        logging.info("FastAPI server stopped.")
            
    except Exception as e:
        logging.exception("An unhandled exception occurred in serve()")
        raise