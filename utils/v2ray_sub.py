from typing import List
import httpx
import re
import arrow
import base64
from collections import namedtuple

TrojanEndpoint = namedtuple("TrojanEndpoint", ["address", "port", "password", "remarks"])


async def get_sub() -> List[TrojanEndpoint]:
    async with httpx.AsyncClient() as client:
        pwd1 =(await client.get("https://www.youhou8.com/pwd1")).content.decode("utf8").strip()
        pwd2 =(await client.get("https://www.youhou8.com/pwd2")).content.decode("utf8").strip()
        v2ray = (await client.get("https://www.youhou8.com/v2ray")).content.decode("utf8")
        pwd_list = [pwd1, pwd2]
        # print(pwd_list)
        v2ray_info = [line for line in v2ray.split("\n") if line.find("pwd") != -1]
        pattern = re.compile("(?<=<b>)(.*?)(?=</b>)")
        now = arrow.now("Asia/Shanghai")
        datetime_str = now.format("MM-DD_HH:mm")
        remarks = "zkq8_" + datetime_str
        sub_list = []
        for i, line in enumerate(v2ray_info):
            trojan = pattern.findall(line)
            address = trojan[1]
            port = trojan[3]
            password = pwd_list[i]
            sub_list.append(TrojanEndpoint(address=address, port=port, password=password, remarks=remarks))
        print(sub_list)
        return sub_list

async def get_sub1() -> List[TrojanEndpoint]:
    async with httpx.AsyncClient() as client:
        pwd1 =(await client.get("https://www.youhou8.com/pwd1")).content.decode("utf8").strip()
        pwd2 =(await client.get("https://www.youhou8.com/pwd2")).content.decode("utf8").strip()
        v2ray = (await client.get("https://www.youhou8.com/v2ray")).content.decode("utf8")
        port1, port2 = "", ""
        port_list = re.findall(r"<b>([1-9][0-9]+)</b>", v2ray)
        if len(port_list) == 2:
            port1, port2 = port_list
        now = arrow.now("Asia/Shanghai")
        datetime_str = now.format("MM-DD_HH:mm")
        remarks = "zkq8_" + datetime_str

        sub_list = []
        server1="www.youhou8.gq"
        server2="www.youhou8.ml"
        sub_list.append(TrojanEndpoint(address=server1, port=port1, password=pwd1, remarks=remarks))
        sub_list.append(TrojanEndpoint(address=server2, port=port2, password=pwd2, remarks=remarks))
        print(sub_list)
        
        return sub_list


# trojan://e589c9f4@www.youhou8.gq:1202

async def get_b64sub1():
    sub = ""
    sub_list = await get_sub1()
    for i in sub_list:
        sub += f"trojan://{i.password}@{i.address}:{i.port}#{i.remarks}\n"
    b64sub = base64.b64encode(bytes(sub, encoding="utf8")).decode("utf8")
    print(b64sub)
    return b64sub


async def get_b64sub():
    sub = ""
    sub_list = await get_sub()
    for i in sub_list:
        sub += f"trojan://{i.password}@{i.address}:{i.port}#{i.remarks}\n"
    b64sub = base64.b64encode(bytes(sub, encoding="utf8")).decode("utf8")
    print(b64sub)
    return b64sub


if __name__ == "__main__":
    import asyncio
    asyncio.run(get_b64sub())
