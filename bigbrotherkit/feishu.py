import requests
import yaml
import json

# 读取YAML配置文件
with open("config.yaml", "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)
print('feishu load')
print(config)
# 获取机器人access_token
app_id = config['feishu']['app_id']
app_secret = config['feishu']['app_secret']
access_token_response = requests.request(method='POST',
                            url='https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
                            headers={'Content-Type': 'application/json; charset=utf-8'},
                            data=json.dumps({'app_id': app_id,'app_secret': app_secret}))
access_token = access_token_response.json()['tenant_access_token']
print('token的值：', access_token)
# 获取飞书机器人所在的群列表
chat_response = requests.request(method='GET',
                            url='https://open.feishu.cn/open-apis/im/v1/chats',
                            headers = {'Authorization': 'Bearer {0}'.format(access_token)})
res = chat_response.json()
chats = [{'chat_id': i['chat_id'], 'name': i['name']} for i in res['data']['items']]
print("所在群列表：", chats)

def send_msg(msg: str):
    print('feishu send_msg')
    """
    执行机器人向飞书群组发送消息
    """
    for chat in chats:
        chat_id = chat['chat_id']
        url = "https://open.feishu.cn/open-apis/message/v4/send/"
        # 请求头，加入认证token
        headers = {
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/json"
        }
        # 消息体，这里以发送文本消息为例
        data = {
            "receiver_id_type": "chat_id",  # 接收者类型，如群组
            "chat_id": chat_id,  # 接收消息的群组ID
            "msg_type": "text",  # 消息类型，这里是文本
            "content": {
                "text": msg  # 消息内容
            }
        }
        # 发送POST请求发送消息
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            print("执行机器人向飞书群组发送消息失败")