import os
import requests
import json
import random
import re

# 添加 server 酱通知
server_key = os.environ.get("SERVER_KEY")

# 获取掘金 cookie
jj_cookie = os.environ.get("JJ_COOKIE")

# 掘金 api_url
baseUrl = "https://api.juejin.cn/"
checkInUrl = baseUrl + "growth_api/v1/check_in"
lotteryUrl = baseUrl + "growth_api/v1/lottery/draw"

# user-agent
user_agent_list = [
    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36 Edg/118.0.2088.76",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]
headers = {"User-Agent": user_agent_list[random.randrange(0, len(user_agent_list))]}


# server 酱消息推送
def send_server(title, content):
    url = "https://sctapi.ftqq.com/%s.send" % server_key
    params = {"text": title, "desp": content}
    resp = requests.post(url, params=params)
    print("server 酱推送状态码: %s" % resp.status_code)


# 入口
if __name__ == "__main__":
    print("debugger")
    checkInResp = requests.post(
        checkInUrl, headers=headers, cookies={"Cookie": jj_cookie}
    )
    print(checkInResp.status_code)
    print(checkInResp.text)
    lotteryResp = requests.post(
        lotteryUrl, headers=headers, cookies={"Cookie": jj_cookie}
    )
    print(lotteryResp.status_code)
    print(lotteryResp.text)
    
    checkin_result = "未知"
    dict = json.loads(checkInResp.text)
    if dict["err_no"] == 0 and dict["data"]:
        data = dict["data"]
        inc = data["incr_point"]
        sum = data["sum_point"]
        checkin_result = "签到成功! 今日新增矿石 %s, 共有矿石 %d" % (inc, sum)
    else:
        checkin_result = "签到失败, %s" % dict["err_msg"]

    lottery_result = "未知"
    dict = json.loads(lotteryResp.text)
    print(dict)
    lottery = ""
    if dict["err_no"] == 0 and dict["data"]:
        lottery_data = dict["data"]
        if re.match(r'.(\d+)矿石', lottery_data["lottery_name"]):
            lottery = re.match(r'.(\d+)矿石', lottery_data["lottery_name"]).group(1)
            if sum:
                sum = sum + int(lottery)
        lottery_result = "抽中%s" % lottery_data["lottery_name"]
    else:
        lottery_result = "未抽中, %s" % dict["err_msg"]

    resultMsg = "掘金签到结果\n" + checkin_result + "\n 掘金抽奖结果\n" + lottery_result

    if server_key:
        if sum:
            if lottery:
                send_server("掘金签到+%d矿石抽奖+%d共%d矿石" % (inc, int(lottery), sum), resultMsg)
            else:
                send_server("掘金签到+%d矿石抽奖+%s共%d矿石" % (inc, lottery_data["lottery_name"], sum), resultMsg)
        else:
            send_server("掘金签到+每日抽奖 ", resultMsg)
