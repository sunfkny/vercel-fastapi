import asyncio
from typing import List
import httpx
import re
import arrow
import base64
from collections import namedtuple

TrojanEndpoint = namedtuple("TrojanEndpoint", ["host", "port", "password", "remarks"])


def get_format_time():
    now = arrow.now("Asia/Shanghai")
    datetime_str = now.format("MM-DD_HH:mm")
    return datetime_str


async def get_sub() -> List[TrojanEndpoint]:
    async with httpx.AsyncClient() as client:
        pwd1_req = client.get("https://www.youhou8.com/pwd1")
        pwd2_req = client.get("https://www.youhou8.com/pwd2")
        v2ray_req = client.get("https://www.youhou8.com/v2ray")

        results_future = asyncio.gather(pwd1_req, pwd2_req, v2ray_req)

        results = await results_future
        pwd1, pwd2, v2ray = [result.content.decode("utf8").strip() for result in results]

    pwd_list = [pwd1, pwd2]
    nbsp_pattern = re.compile(r"(&nbsp;\s*)+")
    v2ray_info = [nbsp_pattern.sub("", line) for line in v2ray.split("\n") if "pwd" in line]
    pattern = re.compile("(?<=<td><b>)(.*?)(?=</b></td>)")
    remarks = "zkq8_" + get_format_time()
    sub_list = []
    for i, line in enumerate(v2ray_info):
        trojan = pattern.findall(line)
        print(trojan)
        if len(trojan) != 3:
            continue
        host = trojan[0]
        port = trojan[2]
        password = pwd_list[i] if i < len(pwd_list) else ""
        sub_list.append(TrojanEndpoint(host=host, port=port, password=password, remarks=remarks))

    for sub in sub_list:
        print(sub)

    return sub_list


async def get_sub1() -> List[TrojanEndpoint]:
    async with httpx.AsyncClient() as client:
        pwd1_req = client.get("https://www.youhou8.com/pwd1")
        pwd2_req = client.get("https://www.youhou8.com/pwd2")
        v2ray_req = client.get("https://www.youhou8.com/v2ray")

        results_future = asyncio.gather(pwd1_req, pwd2_req, v2ray_req)

        results = await results_future
        pwd1, pwd2, v2ray = [result.content.decode("utf8").strip() for result in results]

    port1, port2 = "", ""
    host1, host2 = "www.youhou8.gq", "www.youhou8.ml"

    port_list = re.findall(r"<b>([1-9][0-9]+)</b>", v2ray)
    if len(port_list) == 2:
        port1, port2 = port_list
    datetime_str = get_format_time()
    remarks = "zkq8_" + datetime_str

    sub_list = []
    sub_list.append(TrojanEndpoint(host=host1, port=port1, password=pwd1, remarks=remarks))
    sub_list.append(TrojanEndpoint(host=host2, port=port2, password=pwd2, remarks=remarks))

    for sub in sub_list:
        print(sub)

    return sub_list


async def get_b64sub_from(sub_list: List[TrojanEndpoint]):
    # trojan://password@remote_host:remote_port#remarks
    sub = ""
    for i in sub_list:
        sub += f"trojan://{i.password}@{i.host}:{i.port}#{i.remarks}\n"
    b64sub = base64.b64encode(bytes(sub, encoding="utf8")).decode("utf8")
    print(b64sub)
    return b64sub


async def get_b64sub():
    sub_list = await get_sub()
    return await get_b64sub_from(sub_list)


async def get_b64sub1():
    sub_list = await get_sub1()
    return await get_b64sub_from(sub_list)


if __name__ == "__main__":
    asyncio.run(get_b64sub())
    # asyncio.run(get_b64sub1())
