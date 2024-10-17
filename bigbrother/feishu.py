import requests
import yaml

# 读取 YAML 文件
with open("config.yaml", "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)
print('feishu load')
print(config)

def send_msg():
    print('send msg')

#
# # 飞书API地址
# url = "https://open.feishu.cn/open-apis/message/v4/send/"
# # 用于发送消息的access_token
# access_token = "你的access_token"
#
# # 请求头，加入认证token
# headers = {
#     "Authorization": "Bearer " + access_token,
#     "Content-Type": "application/json"
# }
#
# # 消息体，这里以发送文本消息为例
# data = {
#     "receiver_id_type": "chat_id",  # 接收者类型，如群组
#     "chat_id": "群组ID",  # 接收消息的群组ID
#     "msg_type": "text",  # 消息类型，这里是文本
#     "content": {
#         "text": "这是一条测试消息"  # 消息内容
#     }
# }
#
# # 发送POST请求发送消息
# response = requests.post(url, headers=headers, json=data)
#
# # 打印响应结果
# print(response.json())