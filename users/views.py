from django.shortcuts import render
from django.views import View
# Create your views here.
from api_shop.settings import STATICFILES_DIRS,DEFAULT_FROM_EMAIL,MEMCACHE_HOST,MEMCACHE_PORT,WEIBO_APP_KEY,WEIBO_APP_SECRET,WEIBO_CALL_BACK,SECRET_KEY
import io
from django.http import HttpResponse,JsonResponse
from PIL import Image,ImageDraw,ImageFont
import random
import os
import re
from django.core.cache import cache
# 导入 memcache 缓存
import memcache
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from users import serializer
from goods.serializer import *
from users import models
from urllib.parse import urlencode
import requests,json
from rest_framework_jwt.settings import api_settings 
from django.db import transaction   # django 事务模块

def generate_code_image(image_uuid_code):
    '''
        验证码图片生成接口
            1. 生成图片
            2. 图片打上去随机字符串
            3. 随机字符串保存至memcached
            4. 返回图片
    '''
    bgcolor = (random.randrange(20, 100), random.randrange(
        20, 100), random.randrange(20, 100))
    width = 110
    height = 40
    # 创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point()函数绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    # 定义验证码的备选值
    str = '1234567890QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str[random.randrange(0, len(str))]
    # 构造字体对象

    fonts_files = os.path.join(
        STATICFILES_DIRS[0], 'fonts/' + 'SourceCodePro-Medium.ttf')
    font = ImageFont.truetype(fonts_files, 30)
    # 构造字体颜色
    fontcolor1 = (255, random.randrange(0, 255), random.randrange(0, 255))
    fontcolor2 = (255, random.randrange(0, 255), random.randrange(0, 255))
    fontcolor3 = (255, random.randrange(0, 255), random.randrange(0, 255))
    fontcolor4 = (255, random.randrange(0, 255), random.randrange(0, 255))
    # 绘制4个字
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor1)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor2)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor3)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor4)
    # 释放画笔
    del draw
    # 存入缓存，用于做进一步验证，并设置超时时间为10分组
    cache.set(image_uuid_code,rand_str.upper(),60*10) # 图片随机字符
    buf = io.BytesIO()
    # 将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    # 将内存中的图片数据返回给客户端，MIME类型为图片png！
    return HttpResponse(buf.getvalue(), 'image/png')

class ImageCode(View):
    # image_uuid_code:uuid 路由传参过来的 
    def get(self,request,image_uuid_code):
        '''
            返回图片数据
            key: image_uuid_code
            value: random_str
        '''
        # 将生成验证码函数返回到前端
        return generate_code_image(image_uuid_code)
    def post(self,request,image_uuid_code):
        '''
            校验图片验证码
        '''
        data = {}
        image_code = request.POST.get('image_code')
        cache_image_code = cache.get(image_uuid_code)
        image_code_upper = image_code.upper()

        if image_code_upper == cache_image_code:
            data['code'] = 200
        else:
            data['code'] = 201
        
        return JsonResponse(data)


# 验证用户名是否存在
class Check_username(View):
    def post(self,request):
        data = {}
        username = request.POST.get('username')
        user = models.Users.objects.filter(username=username).first()
        if user:
            data['code'] = 201
            data['mes'] = '用户名已存在'
        else:
            reslut = re.match(r'^[a-zA-Z]+[a-zA-Z0-9_-]{6,16}$',username)
            if reslut:
                data['code'] = 200
                data['mes'] = '有效的用户名'
            else:
                data['code'] = 201
                data['mes'] = '用户名不标准'
        return JsonResponse(data)


# 验证密码
class Check_user_pwd(View):
    def post(self,request):
        data = {}
        password = request.POST.get('password')
        
        reslut = re.match(r'(?=.*[0-9])(?=.*[a-zA-Z])(?=.*[^a-zA-Z0-9]).{6,16}',password)
        if reslut:
            data['mes'] = '难'
        else:
            reslut1 = re.match(r'^[a-zA-Z]+[a-zA-Z0-9_-]{6,16}$',password)
            if reslut1:
                data['mes'] = '中'
            elif re.match(r'^[a-zA-Z0-9_-]{6,16}$',password):
                data['mes'] = '简单'
            else:               
                data['mes'] = '密码不规范'
        data['code'] = 200
        return JsonResponse(data)


# 验证手机号
class Check_user_phone(View):
    def post(self,request):
        data = {}
        user_phone = request.POST.get('user_phone')
        reslut = re.match(r'^1([3-5]|[7-8])[0-9]{9}$',user_phone)
        if reslut:
            data['code'] = 200
        else:
            data['code'] = 201
        return JsonResponse(data)



# 验证邮箱号
class Check_email(View):
    def post(self,request):
        data = {}
        email = request.POST.get('email')
        result = re.match('[a-zA-Z0-9]{5,20}@(qq|sina|wangyi)\.com',email)
        if result:
            data['code'] = 200
        else:
            data['code'] = 201
        return JsonResponse(data)






# 封装原生 memcache 缓存类
class CacheCode:
    '''
        连接缓存数据库
        加入值 获取值 
    '''

    def __init__(self, host, port):
        # 初始化 memcache 连接
        self.mc = memcache.Client([host], port)

    # 取值
    def get(self, key):
        '''
            获取对应key的value
        '''
        return self.mc.get(key)

    # 修改
    def replace(self, key, new_value, expire=60):
        '''
            根据已有key值，更新对应value
            email -> code
        '''
        if not self.mc.replace(key, new_value, expire):
            self.set(key, new_value, expire)
        return True

    # 添加
    def set(self, key, value, expire=60):
        self.mc.set(key, value, expire)




# 验证码生成入缓存
class Sub_email(View):
    def post(self,request):
        ''' 
            key: 邮箱地址
            value: 邮件验证码
            api/generate_emailcode/
        '''
        send_email = request.POST.get('email')

        # 生成随机6位验证码    %06d：% 是格式化，6:6位，d：整型数
        ran_str = '%06d' % (random.randint(0, 999999))

        # 调用缓存类 将host,port传参
        cache = CacheCode(MEMCACHE_HOST, MEMCACHE_PORT)
        '''
            生成验证码后就应该将验证码入缓存，但下面调用的是修改函数，原因是你不知道它这个key在缓存中是否存在，
            如果缓存有这个key的话直接添加会报错，这里就索性就直接调用修改函数，在修改函数中做了判断
        '''      
        cache.replace(send_email,ran_str)
        # 生成验证码，扔到目标邮件里
        subject = '欢迎你'
        message = '''
            这是你的验证码:%s \r\n
            请你好好输入
        ''' % ran_str
        try:
            # subject:主题 ，message：内容， DEFAULT_FROM_EMAIL：发送账号， send_email：接受账号
            send_mail(subject, message, DEFAULT_FROM_EMAIL, [send_email])
        except:
            pass
        data = {'code': 200}
        return JsonResponse(data)



# 验证用户邮箱验证码
class Check_email_code(View):
    def post(self,request):
        data = {}
        send_email = request.POST.get('email')
        email_code = request.POST.get('email_code')
        if not all([send_email,email_code]):
            data['code'] = 201
            data['mes'] = '输入不能为空'
        else:
            cache = CacheCode(MEMCACHE_HOST, MEMCACHE_PORT)
            cache_str = cache.get(send_email)
            if email_code == cache_str:
                data['code'] = 200
                data['mes'] = '验证成功'
            else:
                data['code'] = 201
                data['mes'] = '验证失败'

        return JsonResponse(data)



# 提交注册
class Sub_reg(APIView):
    def post(self,request):
        data = {}
        if not all([request.data['username'],request.data['password'],request.data['password2'],request.data['mobile'],request.data['email']]):
            data['code'] = 202
            data['mes'] = '输入不能为空'
        else:       
            user = serializer.userSerializer(data=request.data)
            if user.is_valid():
                user.save()
                data['code'] = 200
            else:
                data['code'] = 201
                data['mes'] = user.errors
        return Response(data)


# 内部的JWT 只是返回的 token，我们需要它返回给我们 uesr_id，username，这里就重写JWT内置函数
# 这个函数 名是JWT库里内置的函数名，这里定义重写后在 setting 里配置一下即可
def jwt_response_payload_handler(token, user=None, request=None, **kwargs):
    return {
        'token':token,
        'username': user.username,
        'user_id': user.id,
    }

# 多账号登录
from django.contrib.auth.backends import ModelBackend

class UserModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        '''
            多账号登陆
            username == mobile   手机号可登陆
            username == email    邮箱号可登陆
            username == username  用户名可登录
        '''
        try:
            user = models.Users.objects.get(username=username)
            # 校验 用户名是否是原来用户名
        except:
            user = None
            # 当前输入的不是用户名，可能是手机号 还有邮箱
            try:
                user = models.Users.objects.get(email=username)
            except:
                user = None
                try:
                    user = models.Users.objects.get(mobile=username)
                except:
                    user = None
        if user and user.check_password(password):
            # a1234567 = pbkdf2_sha256$100000$ePk0zrf52uPG$jHKbpBaXhYVWipItYnv1vxFCMROuu1ccOP9xaB9oI7w=
            return user



# 拼接微博登录页面链接返回前端
class Get_weibo_login(APIView):

    '''  
        微博的登陆页面地址:https://api.weibo.com/oauth2/authorize?
        链接需要携带三个参数，是我们注册应用时微博给的参数还有一回调地址
        我们在settings配置好，哪里用哪里取

        client_id = 4152203033
        reponse_type=code
        redirect_uri=http://127.0.0.1:8000/api/weibo_back/  
    '''
    
    def get(self,request):
        url = 'https://api.weibo.com/oauth2/authorize?'
        data = {'client_id':WEIBO_APP_KEY,'reponse_type':'code','redirect_uri':WEIBO_CALL_BACK}
        weibo_url = url + urlencode(data)   # urlencode 能将dict 解析成路由拼接

        return Response({'weibo_url':weibo_url})


# 创建payload的函数   载荷
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
# 创建 token 函数
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


# 获取vue 传来的code 向微博获取 uid,access_token
class Get_weibo_uid(APIView):
    '''
        这次访问微博是获取 uid,access_token
        url = https://api.weibo.com/oauth2/access_token?
        连接需要拼接一些必要的参数方便微博认证
       
    '''
    
    def get(self,request):
        code = request.query_params.get('code')
        url = 'https://api.weibo.com/oauth2/access_token?'
        data = {
            'client_id':WEIBO_APP_KEY,
            'client_secret':WEIBO_APP_SECRET,
            'grant_type': 'authorization_code',
            'code':code,
            'redirect_uri':WEIBO_CALL_BACK
        }
        # 这次是发起的 post 请求 返回的响应是json字符串，需要解析取值
        # try:
        response = json.loads(requests.post(url,data).text)
        # except:
        #     return Response({'code':202,'mes':'授权失败'})

        '''
            这是返回的 response 数据
            {'access_token': '2.00jqYNTGfgNAXEbd85e6c672uTGF8E',
            'remind_in': '157679999', 'expires_in': 157679999,
            'uid': '5928542965', 'isRealName': 'true'}
        '''
        uid = response.get('uid')
        if not uid:
            # 如果没有返回 uid 证明第三方授权失败
            data = {'code':202,'mes':'三方授权失败'}
        else:
            '''
                有uid的话就拿uid去三方社交表去查表里有没有这个uid，如果有就可以直接返回token登录，没有就需要前端引导用户去绑定自己的信息
            '''
            try:
                socialuser = models.SocialUser.objects.get(uid=uid)
                # 将查询出来的 socialuser 生成载荷 创建 token
                payload = jwt_payload_handler(socialuser.user)   # 创建载荷
                token = jwt_encode_handler(payload)              # 创建 token
                data = {'code':200,'token':token,'username':socialuser.user.username,'user_id':socialuser.user.id}

            except:
                '''
                    将response返回前端，前端保存access_token,uid再通过后台访问微博获取用户信息入库
                '''
                data = {'code':201,'mes':json.dumps(response)}

        return Response(data)


# 拿到前端的 access_token,uid向微博获取用户信息 入库返回前端 token/
class Bind_user(APIView):

    def post(self,request):
        from django.http import QueryDict
        
        username = request.data['username']
        password = request.data['password']
        password2 = request.data['password2']
        try:
            access_token_object = json.loads(request.data.get('access_token_object'))
        except:
            return Response({'code':201,'mes':'没有第三方认证'})

        if not all([username,password,access_token_object]):
            mes = {'code':201,'mes':'输入不能为空'}
            return Response(mes)
        else:

            get_user_url = "https://api.weibo.com/2/users/show.json?access_token=%s&uid=%s"%(
                access_token_object['access_token'],access_token_object['uid']
            )
            # 获取到了用户信息  准备入库
            data = requests.get(url=get_user_url).text
            data_user = {'username':username,'password':password,'password2':password2,'email':'***@qq.com','mobile':'***'}
            try:
                with transaction.atomic():
                    user = serializer.userSerializer(data=data_user)
                    if user.is_valid():
                        users = user.save()
                    else:
                        print(user.errors)

                    data_socialuser = {'platfrom_id':1,'platfrom_type':2,'uid':access_token_object['uid']}
                                                                                # 涉及到外键就要把对象传过去反序列器接受
                    socialuser = serializer.socialuserSerializer(data=data_socialuser,context={'outer_key':users})
                    if socialuser.is_valid():
                        socialuser.save()
                        payload = jwt_payload_handler(users)   # 创建载荷
                        token = jwt_encode_handler(payload)              # 创建 token
                        mes = {'token':token,'username':users.username,'user_id':users.id}
                       
                        return Response(mes)
                    else:
                        print(socialuser.errors)
                    return Response({'mes':'都没有入库'})
            except:       
                  return Response('授权失败')


                
# 导入验证模块               
from rest_framework.permissions import IsAuthenticated

# 个人中心验证返回用户数据
class User_info(APIView):
    # IsAuthenticated会自动验证，验证结束，如果验证OK 有效用户对象会被保存
    # permission_classes:是底层的一个类方法
    permission_classes = (IsAuthenticated,)

    # 验证结束会将 user 传递给 request
    def get(self,request):
        data_user = request.user
        # 将 user 序列化处理
        user = serializer.userSerializer(instance=data_user)

        import redis
        r = redis.Redis(host='39.106.64.101')

        goods_sku = models.GoodsSku.objects.filter(id__in=r.lrange(data_user.id,0,-1)).all()
        sku_list = GoodsSkuSerializer(instance=goods_sku,many=True)

        return Response({'user':user.data,'sku_list':sku_list.data})



# 修改密码页面权限
class User_pass(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self,request):
        user = request.user
        vue_data = request.data
        change_user = serializer.ChangePasswordSerializer(instance=user,data=vue_data)

        if change_user.is_valid():
            change_user.save()
            return Response({'code':200})
        
        else:   
            return Response({change_user.errors})



# 导入创建 token 模块
from itsdangerous import TimedJSONWebSignatureSerializer,SignatureExpired
# 导入异步消息队列
from . import tasks

# 创建载荷
ser = TimedJSONWebSignatureSerializer(SECRET_KEY,600)

# 找回密码 发送邮箱
class Send_email(APIView):

    def post(self,request):
        '''
            接受前端邮箱，创建 token 发给celery消息任务
        '''
        email = request.data['email']
    
        try:
            user_email = models.Users.objects.get(email=email)
        
        except:
            return Response({'code':201,'mes':'邮箱不存在'})

        else:

            # 邮箱存在，将邮箱信息封装，放入载荷生成 token
            data = {'email':email}
            token = ser.dumps(data).decode()      # dumps后的 data是二进制的 token 串前有个 b',需要decode解码

            # 将邮箱号和生成的 token 发给传给队列
            tasks.send_user_email.delay(email,token)
            
            # 消息队列会异步发送邮箱。这里直接返回200即可
            return Response({'code':200})


# 修改密码
class Update_pwd(APIView):
    
    def post(self,request):
        token = request.data['token']
        password = request.data['new_pwd']

        try:

            # ser.loads：载荷.loads 可以将 token 解析
            email = ser.loads(token)['email']

        except SignatureExpired:
            return Response({'data':'邮箱过期'})

        '''
            将当前用户和新密码传给 序列化器 修改密码
        '''
        user = models.Users.objects.filter(email=email).first()
        res_user = serializer.FindPasswordSerializer(
            instance = user,
            data = {'password':password}    # data 需要传递的是个对象或一个字典
        )

        if res_user.is_valid():
            res_user.save()
            return Response({'code':200})
        else:
            return Response({'code':201,'mes':res_user.errors})




from rest_framework import generics
# 获取一级城市
class Get_edit_one(generics.ListAPIView):
    '''
        条件查询数据库 parent=None的城市代表是最上级，
        用 generics.ListAPIView 类视图可以直接调用它的序列化器，自动返回
        这边直接添加查询返回数据就好，用 ListAPIView 太花哨
    '''
    # queryset:底层的方法
    queryset = models.City.objects.filter(parent=None).all()

    serializer_class = serializer.CitySerializer


# 获取二级城市数据
class Get_edit_two(generics.ListAPIView):

    serializer_class = serializer.CitySerializer

    def get_queryset(self):
        # self.kwargs：前端发过来的数据
        one_city_id = self.kwargs['one_city_id']

        city_two_mes = models.City.objects.filter(parent__city_id=one_city_id).all()

        return city_two_mes


# 获取三级城市数据
class Get_edit_three(generics.ListAPIView):

    serializer_class = serializer.CitySerializer

    def get_queryset(self):
        two_city_id = self.kwargs['two_city_id']

        city_three_mes = models.City.objects.filter(parent__city_id=two_city_id).all()

        return city_three_mes


# 地址入库
class Inert_addres(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self,request):

        user = request.user
        province_id = request.data['province']
        city_id = request.data['city']
        town_id = request.data['town']
        adres_id = request.data['adres_id']    # 获取前端传的ID，有ID就是修改，没有就是添加

        if not all([province_id,city_id,town_id]):
            return Response({'code':201,'mes':'选项不能为空'})

        province = models.City.objects.filter(city_id=province_id).first()
        city = models.City.objects.filter(city_id=city_id).first()
        town = models.City.objects.filter(city_id=town_id).first()
        
        # 有 id 就是修改
        if adres_id:
            receiver = request.data['receiver']
            place = request.data['place']
            mobile = request.data['mobile']
            email = request.data['email']
            models.Address.objects.filter(id=adres_id).update(
                receiver = receiver,place = place,mobile = mobile,email = email,
                province = province,city = city,town = town
            )
            return Response({'code':200})
        else:
            address = serializer.addressSerializer(data=request.data,context={'user':user,'province':province,'city':city,'town':town})
            if address.is_valid():
                address.save()
                return Response({'code':200})
            else:

                return Response({'code':201,'mes':address.errors})


# 获取用户地址
class Get_address_mes(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self,request):
        user = request.user
        address = models.Address.objects.filter(user=user,is_delete=False,default_address=0).all()
        address_all = models.Address.objects.filter(user=user,is_delete=False).all()
        len_address = len(address_all)
        user_address = serializer.addressSerializer(instance=address,many=True)


        return Response({
            'address':user_address.data,
            'len_address':len_address
            })


# 默认地址
class Def_address_mes(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self,request):
        user = request.user
        address = models.Address.objects.filter(user=user,is_delete=False,default_address=1).all()

        if address:
            def_address = serializer.addressSerializer(instance=address,many=True)

            return Response(
                {'code':200,'mes':def_address.data}
            )
        else:
            return Response(
                {'code':201}
            )

from django.db.models import Q   # ~Q：不等于  
# 设置默认地址
class Set_def_address(APIView):

    permission_classes = (IsAuthenticated,)

    # adres_id：正则路由传参
    def get(self,request,adres_id):

        models.Address.objects.filter(id=adres_id).update(default_address=1)
        models.Address.objects.filter(~Q(id=adres_id)).update(default_address=0)

        return Response({'code':200})

    
# 删除地址
class Delete_def_address(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self,request,adres_id):
        models.Address.objects.filter(id=adres_id).update(is_delete=True)

        return Response({'code':200})


# 编辑地址
class Redact_address(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self,request,adres_id):

        address = models.Address.objects.filter(id=adres_id).first()
        if address:
            red_address = serializer.addressSerializer(instance=address)

            return Response({'code':200,'mes':red_address.data})

        else:
            return Response({'code':201})

