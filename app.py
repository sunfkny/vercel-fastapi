import asyncio
import re
from typing import Optional

from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, PlainTextResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import httpx

from utils.v2ray_sub import get_b64sub, get_b64sub1
from utils.v2rayse_sub import get_v2rayse_sub

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    # 允许跨域的源列表，例如 ["http://www.example.org"] 等等，["*"] 表示允许任何源
    allow_origins=["*"],
    # 跨域请求是否支持 cookie，默认是 False，如果为 True，allow_origins 必须为具体的源，不可以是 ["*"]
    allow_credentials=False,
    # 允许跨域请求的 HTTP 方法列表，默认是 ["GET"]
    allow_methods=["*"],
    # 允许跨域请求的 HTTP 请求头列表，默认是 []，可以使用 ["*"] 表示允许所有的请求头
    # 当然 Accept、Accept-Language、Content-Language 以及 Content-Type 总之被允许的
    allow_headers=["*"],
    # 可以被浏览器访问的响应头, 默认是 []，一般很少指定
    # expose_headers=["*"]
    # 设定浏览器缓存 CORS 响应的最长时间，单位是秒。默认为 600，一般也很少指定
    # max_age=1000
)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    async with httpx.AsyncClient() as client:
        pwd1_req = client.get("https://www.youhou8.com/pwd1")
        pwd2_req = client.get("https://www.youhou8.com/pwd2")
        count1_req = client.get("https://www.youhou8.com/count1")
        count2_req = client.get("https://www.youhou8.com/count2")
        v2ray_req = client.get("https://www.youhou8.com/v2ray")

        results_future = asyncio.gather(pwd1_req, pwd2_req, count1_req, count2_req, v2ray_req)

        results = await results_future
        pwd1, pwd2, count1, count2, v2ray = [result.content.decode("utf8").strip() for result in results]

    port1, port2 = "", ""
    host1, host2 = "www.youhou8.gq", "www.youhou8.ml"
    port_list = re.findall(r"<b>([1-9][0-9]+)</b>", v2ray)
    if len(port_list) == 2:
        port1, port2 = port_list
    message_list = re.findall(r"<p.*?>(.+)</p>", v2ray)
    message = "".join(message_list)

    context = dict(
        request=request,
        message=message,
        servers=[
            {"host": host1, "port": port1, "password": pwd1, "count": count1},
            {"host": host2, "port": port2, "password": pwd2, "count": count2},
        ],
    )
    return templates.TemplateResponse("index.html", context=context)


@app.get("/sub", response_class=PlainTextResponse)
async def sub(request: Request):
    return PlainTextResponse(await get_b64sub())


@app.get("/sub1", response_class=PlainTextResponse)
async def sub1(request: Request):
    return PlainTextResponse(await get_b64sub1())


@app.get("/v2rayse")
async def api_v2rayse(request: Request):
    return PlainTextResponse(await get_v2rayse_sub())


@app.get("/cors", response_class=Response)
async def cors(request: Request, url: str):
    async with httpx.AsyncClient() as client:
        try:
            await client.head(url, timeout=3)
        except Exception as e:
            return PlainTextResponse(str(e))

        def stream():
            with httpx.stream("GET", url) as r:
                for chunk in r.iter_bytes(chunk_size=4 * 1024):
                    if chunk:
                        yield chunk

        return StreamingResponse(content=stream())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("__main__:app", host="127.0.0.1", port=8000, reload=True)
