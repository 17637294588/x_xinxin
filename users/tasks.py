from django.core.mail import send_mail    # 发送邮箱模块
from celery import task                  # ??任务模块
from api_shop.settings import EMAIL_HOST_USER    # 邮箱发送人
import django     #  ???
django.setup()
from time import sleep


@task
def send_user_email(email,token):
    title = '欢迎你'
    mes = '''
            点击该链接重置密码：\r\n
            http://127.0.0.1:8080/#/change_pwd?token=%s       
        '''% token

    # 发送邮件，邮件也可能会由于某种因素发送失败，如果发送失败，用户再点击发送一次就好
    try:
        send_mail(title,mes,EMAIL_HOST_USER,[email])
    except:
        pass