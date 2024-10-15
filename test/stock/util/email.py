# import smtplib
# from email.mime.text import MIMEText
# from email.utils import formataddr
# import time
#
# my_sender = 'messager_xinxinjia@163.com'  # 发件人邮箱账号
# my_pass = 'LIIUHYWWVAJQFHLH'  # 发件人邮箱密码
# # reviever = ['707216098@qq.com', '767139527@qq.com']
# # recipients = [
# #     ('心心家成员', '707216098@qq.com'),
# #     ('心心家成员', '767139527@qq.com')
# # ]
# reviever = ['707216098@qq.com']
# recipients = [
#     ('心心家成员', '707216098@qq.com'),
# ]
#
#
# def send(message):
#     ret = True
#     try:
#         current_dt = time.strftime("%Y-%m-%d", time.localtime())
#         # current_dt = datetime.strptime(current_dt, '%Y-%m-%d')
#         title = current_dt.split(" ")[0] + " 心心家"
#
#         msg = MIMEText(message, 'plain', 'utf-8')
#         msg['From'] = formataddr(('心心家', my_sender))  # 发件人昵称
#         # 使用formataddr格式化多个收件人
#         msg['To'] = ', '.join([formataddr(recipient) for recipient in recipients])
#         msg['Subject'] = title  # 邮件的主题
#         server = smtplib.SMTP_SSL("smtp.163.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
#         server.login(my_sender, my_pass)  # 发件人邮箱账号、邮箱密码
#         server.sendmail(my_sender, reviever, msg.as_string())  # 发件人邮箱账号、收件人邮箱账号、发送邮件
#         server.quit()  # 关闭连接
#     except Exception as e:  # 如果 try 中的语句没有执行，则会执行下面的 ret = False
#         ret = False
#         print(e)
#     return ret