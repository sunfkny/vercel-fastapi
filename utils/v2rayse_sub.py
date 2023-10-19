import json
from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding
import base64
import httpx
import time

key = base64.b64decode("plr4EY25bk1HbC6a+W76TQ==")
cipher = AES.new(key=key, mode=AES.MODE_ECB)


def get_cf_verify() -> str:
    now = int(time.time() * 1000)
    str_now = str(now)
    bytes_now = str_now.encode()
    bytes_now_pad = Padding.pad(bytes_now, AES.block_size)
    encrypted_now = cipher.encrypt(bytes_now_pad)
    cf_verify = base64.b64encode(encrypted_now)
    return cf_verify.decode()


class CfVerifyAuth(httpx.Auth):
    def auth_flow(self, request: httpx.Request):
        request.headers["cf-verify"] = get_cf_verify()
        yield request


async def get_sub_nodes() -> list[str]:
    # https://v2rayse.com/free-node
    # r = client.get(url="https://cors.isteed.cc/https://api.v2rayse.com/api/batch")
    async with httpx.AsyncClient(auth=CfVerifyAuth(), verify=False) as client:
        r = await client.get(url="https://cors.isteed.cc/https://api.v2rayse.com/api/live")

    r_bytes = base64.b64decode(r.text)
    r_decrypted = cipher.decrypt(r_bytes)
    r_decrypted = Padding.unpad(r_decrypted, AES.block_size)
    r_json = json.loads(r_decrypted)
    nodes = [i["share"] for i in r_json["proxies"]]
    return nodes


async def get_v2rayse_sub():
    nodes = await get_sub_nodes()
    nodes_str = "\n".join(nodes)
    v2ray_sub = base64.b64encode(nodes_str.encode()).decode()
    return v2ray_sub
