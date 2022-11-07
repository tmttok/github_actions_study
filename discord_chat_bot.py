import json5
import json
import os
import time
import requests
import random
from urllib.parse import quote


name = os.environ['NAME']
auth = os.environ['AUTH']
headers = {
    "Authorization": auth,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
}


# 获取频道
def get_channel_dict(channel_json='channels.json'):
    with open(channel_json, 'r') as f:
        channels = json5.load(f)
    return channels


# 获取最近聊天记录
def get_last_records(channel_name, channel_id, total=100):
    try:
        res = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/messages?limit={total}", headers=headers, timeout=30)
        if res.status_code == 200:
            return json.loads(res.content)
        else:
            print(f'❌ {channel_name}获取最近{total}条聊天记录失败：{res.status_code}')
    except Exception as e:
        print(f'❌ {channel_name}获取最近{total}条聊天记录异常：{e}')
    return None


# 调用聊天api
def qingyunke_api(content):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
    }
    try:
        res = requests.get(f'http://api.qingyunke.com/api.php?key=free&appid=0&msg={quote(content)}', headers=headers, timeout=30)
        if res.status_code == 200:
            return json.loads(res.content)['content']
    except Exception as e:
        pass
    return None


# 获取回答内容
def get_content(channel_name, channel_id, type=1):
    # 获取最近聊天记录
    total = 100
    result = get_last_records(channel_name, channel_id, total)
    if result is None:
        return None

    # 最近发过就不用发了
    check_num = 30
    for i in range(check_num):
        if name in result[i]['author']['username']:
            print(f'{channel_name}最近{check_num}条发过')
            return None

    # 从最近记录选一条记录
    content = result[random.randrange(check_num)]['content']
    while check_content(content):
        content = result[random.randrange(check_num)]['content']

    if type == 1:
        # 从剩余记录选一条作为回答
        answer = result[total-check_num + random.randrange(check_num)]['content']
        while check_content(answer):
            answer = result[total-check_num + random.randrange(check_num)]['content']
    else:
        # 调用聊天api回答
        answer = qingyunke_api(content)

    return (content, answer)


def check_content(content):
    return '<' in content or '>' in content or '@' in content or '#' in content or 'http' in content or '?' in content or len(content)>100


# 自动聊天
def auto_chat(channel_name, channel_id):
    content = get_content(channel_name, channel_id)
    if content is None:
        return

    payload = {
        "content": content[1],
        "nonce": "82329451214{}33232234".format(random.randrange(0, 1000)),
        "tts": False
    }
    try:
        res = requests.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', data=json.dumps(payload),  headers=headers, timeout=30)
        if res.status_code==200:
            print(f'✅ {channel_name}发送成功 => {content[0]}: {content[1]}')
        else:
            print(f'❌ {channel_name}发送失败：{res.status_code}')
    except Exception as e:
        print(f'❌ {channel_name}发送异常：{e}')
    

def main():
    channels = get_channel_dict()
    for channel in channels.items():
        channel_name, channel_id = channel
        auto_chat(channel_name, channel_id)
        time.sleep(1)


if __name__ == "__main__":
    main()