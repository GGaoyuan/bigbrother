import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import time
import logging


def pb_ratio() -> float:
    """
    市净率
    公司的股价除以每股净资产，反映市场对公司每股净资产的估值倍数。
    """
    return 0



def send_email(message):
    ret = True
    msg_from = ('心心家', 'messager_xinxinjia@163.com')
    sender_name = '心心家的QMT'
    sender_email = 'messager_xinxinjia@163.com'
    sender_psw = 'LIIUHYWWVAJQFHLH'

    reviever = ['707216098@qq.com']
    recipients = [
        ('心心家成员', '707216098@qq.com'),
    ]

    my_sender = 'messager_xinxinjia@163.com'  # 发件人邮箱账号
    my_pass = 'LIIUHYWWVAJQFHLH'  # 发件人邮箱密码
    # reviever = ['707216098@qq.com', '767139527@qq.com']
    # recipients = [
    #     ('心心家成员', '707216098@qq.com'),
    #     ('心心家成员', '767139527@qq.com')
    # ]

    try:
        current_dt = time.strftime("%Y-%m-%d", time.localtime())
        # current_dt = datetime.strptime(current_dt, '%Y-%m-%d')
        title = current_dt.split(" ")[0] + " 心心家"
        # 邮件内容
        msg = MIMEText(message, 'plain', 'utf-8')
        # 发件人昵称
        msg['From'] = formataddr((sender_name, sender_email))
        # 使用formataddr格式化多个收件人
        msg['To'] = ', '.join([formataddr(recipient) for recipient in recipients])
        # 邮件的主题
        msg['Subject'] = title
        # 发件人邮箱中的SMTP服务器，端口是465
        server = smtplib.SMTP_SSL("smtp.163.com", 465)
        # 发件人邮箱账号、邮箱密码
        server.login(my_sender, my_pass)
        # 发件人邮箱账号、收件人邮箱账号、发送邮件
        server.sendmail(my_sender, reviever, msg.as_string())
        # 关闭连接
        server.quit()
    except Exception as e:
        # 如果 try 中的语句没有执行，则会执行下面的 ret = False
        ret = False
        print(e)
    return ret