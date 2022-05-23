import requests
import re
import time
import base64

def get_sub():
    pwd_list = []
    pwd_list.append(requests.get("https://www.youhou8.com/pwd1").content.decode("utf8").strip())
    pwd_list.append(requests.get("https://www.youhou8.com/pwd2").content.decode("utf8").strip())
    # print(pwd_list)
    v2ray = requests.get("https://www.youhou8.com/v2ray").content.decode("utf8")
    v2ray_info = [line for line in v2ray.split("\n") if line.find("pwd") != -1]
    pattern = re.compile("(?<=<b>)(.*?)(?=</b>)")
    date_str = time.strftime("%m-%d_%H:%M", time.localtime())
    remarks = 'zkq8_' + date_str
    sub = ""
    sub_list = []
    for i, line in enumerate(v2ray_info):
        trojan = pattern.findall(line)
        # print(trojan)
        # trojan://e589c9f4@www.youhou8.gq:1202
        address = trojan[1]
        port = trojan[3]
        password = pwd_list[i]
        sub_list.append([address, port, password, remarks])
        sub += f"trojan://{password}@{address}:{port}#{remarks}\n"
    print(sub_list)
    return sub_list


def get_b64sub():
    sub = ""
    sub_list = get_sub()
    for address, port, password, remarks in sub_list:
        sub += f"trojan://{password}@{address}:{port}#{remarks}\n"
    b64sub = base64.b64encode(bytes(sub, encoding="utf8")).decode("utf8")
    # print(b64sub)
    return b64sub
