from django.shortcuts import render,redirect
from users.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from goods import serializer
from users.serializer import *
from collections import OrderedDict
from api_shop.settings import *
# 导入验证模块               
from rest_framework.permissions import IsAuthenticated
from django.db import transaction 
# Create your views here.



# 获取频道分类
class Goods_channel(APIView):

    def get(self,request):

        '''
           获取所有的频道
           先获取
        '''


       

        # 商品频道及分类菜单  
        dict = {}

        channels = GoodsChannle.objects.order_by('group_id', 'sequence')

        for channel in channels:
            group_id = channel.group_id # 当前组

            if group_id not in dict:
                # 定义一级分类
                dict[group_id] = {'channels': []}

            cat1 = channel.cate # 当前频道的类别
        
            # 获取下一级分类
            cat2 = GoodsCate.objects.filter(parent=cat1)

            list=[]
            for i in cat2:
                dict1 = {'id':i.id,'name':i.name}
                list.append(dict1)

            dict[group_id]['channels'].append({
                'id': cat1.id,
                'name': cat1.name,
                'url': channel.url,
                'sub_cats': list
            })

      
        return Response(dict)

        '''
        {1: {'channels': {'[id': 1, 'name': '手机', 'url': 'https://blog.csdn.net/SJK__', 'sub_cats': ['Iphone', '小米']},{'id': 2, 'name': '电
        脑', 'url': 'https://blog.csdn.net/SJK__', 'sub_cats': ['苹果', '联想']}, {'id': 3, 'name': '数码', 'url': 'https://blog.csdn.net/SJK__', 'sub_cats': ['相机']}]}, 2: {'channels': [{'id': 14, 'name': '服装', 'url': 'https://blog.csdn.net/SJK__', 'sub_cats': ['男装']}]}}
        
        '''
        
from django.conf import settings
from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client     

# 重写存储引擎方法
class FastDfsStroage(Storage):

    def __init__(self, base_url = None, client_conf = None):
        """
            初始化对象
            :param base_url:
            :param client_conf:
        """
        if base_url is None:
            base_url = FDAS_URL
            # 'http://39.106.64.101:8888/'
        self.base_url = base_url

        if client_conf is None:
            client_conf = FDFS_CLIENT_CONF
            # FDFS_CLIENT_CONF = os.path.join(BASE_DIR, 'client.conf')
        self.client_conf = client_conf


    def _open(self, name, mode = 'rb'):
    
        """
            打开文件
            :param name:
            :param mode:
            :return:
        """
        pass

    def _save(self, name, content):
        """
            保存文件
            :param name: 传入文件名
            :param content: 文件内容
            :return:保存到数据库中的FastDFSDE文件名
        """
        client = Fdfs_client(self.client_conf)
        ret = client.upload_by_buffer(content.read())

        if ret.get("Status") != "Upload successed.":
            raise Exception("upload file failed")
        file_name = ret.get("Remote file_id")

        return file_name


    def exists(self, name):
        """
            检查文件是否重复, FastDFS自动区分重复文件
            :param name:
            :return:
        """
        return False

    def url(self, name):
        """
            获取name文件的完整url
            :param name:
            :return:
        """
        return self.base_url + name




# 获取商品列表页数据
class List_goods_mes(APIView):

    def get(self,request,cid):
    
        goodsSkus = GoodsSku.objects.filter(cate=cid)
        
        goodsSku_list = serializer.GoodsSkuSerializer(instance=goodsSkus,many=True)
        
        return Response(goodsSku_list.data)



import redis
# 封装存 redis 方法
# def set_redis(user_id,sku_id):
 
#     r = redis.Redis(host='39.106.64.101')
    
#     r.lrem(user_id,0,sku_id)     # 删除当前 sky的 user_id 所有value, 0:删除所有
#     r.lpush(user_id,sku_id)
#     r.ltrim(user_id,0, 4)       # 删除列表中从指定位置到结束位置以外的数据


class Set_redis():

    def __init__(self):
        self.r = redis.Redis(host='39.106.64.101')

    
    def set_list(self,user_id,sku_id):
        self.r.lrem(user_id,0,sku_id)     # 删除当前 sky的 user_id 所有value, 0:删除所有
        self.r.lpush(user_id,sku_id)
        self.r.ltrim(user_id,0, 4)       # 删除列表中从指定位置到结束位置以外的数据
    
    def set_set(self,user_id,sku_id,number):
        '''
            先去redis查是否存在当前 key,
            有就让数量相加， hset 可以覆盖之前的
            没有就直接入库
        '''
        res = self.r.hget(name='cart_%d'%user_id,key=sku_id)

        if res:
            number = int(number) + int(res)

        self.r.hset(name='cart_%d'%user_id,key=sku_id,value=number)


    def get_cart_mes(self,user_id):
        '''
            根据用户 id 查找所有的 value
        '''
        goods_sku = self.r.hgetall(name='cart_%d'%int(user_id))
        if goods_sku:
            return goods_sku
        return None


    def get_one_mes(self,user_id,sku_id):
        '''
            根据 key user_id,取sku_id的值
        '''
        sku_one = self.r.hget(name='cart_%d'%user_id,key=sku_id)
        if sku_one:
            return sku_one
        return None


    def del_sku(self,user_id,sku_id):
        '''
            删除 sky user_id的sku_id的值
        '''
        self.r.hdel('cart_%d'%user_id,sku_id)

  



# 获取详情页商品
class Get_detail_goods(APIView):
    
    def post(self,request):

        goods_sid = request.data['goods_sid']

        # 商品 sku
        goodsSku = GoodsSku.objects.filter(id=goods_sid).first()


        # 规格分类
        spec_Cate = GoodsSpecification.objects.filter(goods=goodsSku.goods)

        list1 = []
        for i in spec_Cate:
            dict1 = {}
            dict1['cate_name'] = i.name
            dict1['cate_value'] = i.specificationoption_set.all().values('value','id')
            list1.append(dict1)

        goods_sku = serializer.GoodsSkuSerializer(instance=goodsSku)
        data = {
            'goods_sku':goods_sku.data,'sku_list':list1,'goods_mes':goodsSku.goods.desc_detail,
            'goods_pack':goodsSku.goods.desc_pack,'goods_service':goodsSku.goods.desc_service
            }

        return Response(data)

    

'''
    {
        'goods_sku': {'id': 4, 'name': 'Apple iPhoneX 512G 黑色 全网通 苹果X', 'price': '8000.00', 'default_image_url': 'http://39.106.64.101:8888/group1\\M00/00/00/rBHmx10BpamASAeEAAAplyZxA0s3550998', 'comments': 0, 'caption': '很好用的手机'},
            
        'sku_list': [{'cate_name': '颜色', 'cate_value': <QuerySet [{'value': '银色', 'id': 4}, {'value': '黑色', 'id': 6}]>}, {'cate_name': '内存', 'cate_value': <QuerySet [{'value': '512G', 'id': 5}]>}]
            
    }

'''

# 浏览记录入 redis
class Send_redis(APIView):

    def post(self,request):

        user_id = request.data['user_id']
        goods_sid = request.data['goods_sid']
        r_obj = Set_redis()
        r_obj.set_list(user_id,goods_sid)

        return Response({'code':200})



class Check_sku(APIView):

    def get(self,request,id):
        
        spec = SkuSpecification.objects.filter(option=id).first()   # 商品 sku：spec.sku

         # 规格分类
        spec_Cate = GoodsSpecification.objects.filter(goods=spec.sku.goods)

        list1 = []
        for i in spec_Cate:
            dict1 = {}
            dict1['cate_name'] = i.name
            dict1['cate_value'] = i.specificationoption_set.all().values('value','id')
            list1.append(dict1)

        goods_sku = serializer.GoodsSkuSerializer(instance=spec.sku)
        data = {
            'goods_sku':goods_sku.data,'sku_list':list1,'goods_mes':spec.sku.goods.desc_detail,
            'goods_pack':spec.sku.goods.desc_pack,'goods_service':spec.sku.goods.desc_service
            }

        return Response(data)



class Add_detail(APIView):
    
    def post(self,request):
        sku_id = request.data['sku_id']
        state = request.data['state']
        number = request.data['number']
        mes = {}
        
        # 加
        if int(state) == 1:

            goods_sku = GoodsSku.objects.filter(id=sku_id).first()
            n = int(number) + 1
            if goods_sku.stock >= n:
                mes['code'] = 200
            else:
                mes['code'] = 10010
                mes['mes'] = '库存不足'

        # 减
        else:
            if int(number) == 1:
                mes['code'] = 10010
                mes['mes'] = '亲 已经不能再减了'

            else:
                mes['code'] = 200
        
        return Response(mes)



# 加入购物车
class Cart(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self,request,sku_id):
        user = request.user
        goodsSku = GoodsSku.objects.filter(id=sku_id).first()
        number = request.data['number']
        if int(number) > goodsSku.stock:
            return Response({'code':201,'mes':'库存不足'})

        try:
            r_obj = Set_redis()
            r_obj.set_set(user.id,sku_id,number)
            data = {'code':200,'mes':'以加入购物车'}
        except Exception as e:
            print(e,'==================')
            data = {'code':201,'mes':'操作失败'}
        return Response(data)



# 获取购物车数据
class Cart_mes(APIView):

    def get(self,request,user_id):
        
        r_obj = Set_redis()
        sku_id_list = r_obj.get_cart_mes(user_id)  # sku_id_list:里面包含 key:sku_id,value:number

        total = 0
        data = []
        for sku_id,number in sku_id_list.items():
            goods_sku = GoodsSku.objects.filter(id=int(sku_id)).first()
            dict1 = {
                'id':goods_sku.id,
                'image_url':goods_sku.default_image_url.url,
                'name':goods_sku.name,
                'price':goods_sku.price,
                'number':int(number),
                'total':int(number) * goods_sku.price
            }
            total += int(number) * goods_sku.price
            data.append(dict1)
        lens = len(data)
        return Response({'data':data,'lens':lens,'total':total})


        # {b'4': b'2', b'1': b'1'}

# 生成订单号
import time
def get_order_code():
    order_no = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))+ str(time.time()).replace('.', '')[-7:]
    return order_no





class Sub_order(APIView):
    
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        '''
            遍历前端用户选中的购买商品
            根据user_id,sku_id从redis中取出每样商品购买的数量，先入订单详情表，最后入订单表，
            根据 user 可以查到用户的默认地址
        '''

        user = request.user
        check_list = request.data['check_list']

        if check_list:

            check_list = check_list.split(',')

            r_obj = Set_redis()
            order_code = get_order_code()    # 创建 订单号
            
            total_number = 0
            total_manoy = 0
            try:
                with transaction.atomic():
                    for i in check_list:     # i 是前端传来的 sku_id

                        redis_sku_number = int(r_obj.get_one_mes(user.id,int(i)))  # 从 redis 里面获取 购物车 sku 数量
                        goods_sku = GoodsSku.objects.filter(id=i).first()
                        total_number += redis_sku_number
                        total_manoy += float(redis_sku_number * goods_sku.price)
                        
                        if redis_sku_number > goods_sku.stock:
                            return Response({'code':201,'mes':'库存不足，购买失败'})
                        
                        else:
                            # 入订单详情表
                            order_dital = Ordersdetail(order_code=order_code,goods_number=redis_sku_number,goodsSku=goods_sku)
                            order_dital.save()
                            
                            # 修改库存
                            GoodsSku.objects.filter(id=i).update(stock=goods_sku.stock-redis_sku_number)
                            # 删除 redis 购物车数据
                            r_obj.del_sku(user.id,int(i))

                    # 入订单表
                    address = Address.objects.filter(user=user,default_address=1).first()
                    orders = Orders(order_code=order_code,user=user,total_number=total_number,
                            total_manoy=total_manoy,pay_type=2,status=1,address=address.id)
                    orders.save()

                    return Response({'code':200,'order_code':orders.order_code})
            except Exception as e:
                print(e)
                return Response({'code':201,'mes':'操作失败'})
        else:
            return Response({'code':201,'mes':'勾选商品'})



# 获取订单数据
class Get_orders_message(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self,request):

        user = request.user
        order_code = request.data['order_code']

        order_detail = Ordersdetail.objects.filter(order_code=order_code).all()

        total = 0
        data = []
        for i in order_detail:
            dict1 = {
                'image':i.goodsSku.default_image_url.url,
                'name':i.goodsSku.name,
                'price':i.goodsSku.price,
                'number':i.goods_number,
                'subtotal':float(i.goods_number * i.goodsSku.price)
            }
            total += float(i.goods_number * i.goodsSku.price)
            data.append(dict1)


        # 获取用户地址 和 付款方式
        orders = Orders.objects.filter(order_code=order_code).first()
        address = Address.objects.filter(user=user,default_address=1).first()
        address = addressSerializer(instance=address)
        orders_dict = {'order_address':address.data,'pay_type':orders.pay_type}

        return Response({
            'orders_data':data,'orders_dict':orders_dict,'lens':len(order_detail),'total':total
        })  



# 修改订单的收货地址
class Change_adres(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self,request):
        adres_id = request.data['adres_id']
        order_code = request.data['order_code']
        try:
            Orders.objects.filter(order_code=order_code).update(address=adres_id)
        except:
            return Response({'code':201,'mes':'地址修改失败'})
        else:
            return Response({'code':200})




from datetime import datetime
# 获取我的订单数据
class Get_my_orders(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self,request):
        '''
            [
                {'订单详情':[{},{}],'订单':{}}，
                {'订单详情':[{},{}],'订单':{}}
            ]
            先查到用户所有订单，遍历订单，用每个订单的订单号获取订单详情数据，进行封装


            [
                {
                    'orders_detail': [{'image': 'http://39.106.64.101:8888/group1\\M00/00/00/rBHmx10Bn4CAXopdAAEGx9ms61I5053257', 'name': '小米8 幻彩蓝 8G+128G 全网通', 'price': Decimal('3500.00'), 'number': 1, 'xiaoji': 3500.0}], 
                    'orders': {'order_code': '201906201724018679285', 'total_manoy': Decimal('3500.00'), 'pay_type': 2, 'status': 1}
                    }
                    
            ]
        '''
        user = request.user
        order_list = Orders.objects.filter(user=user).all()

        data = []
        for i in order_list:

            orders_detail_list = Ordersdetail.objects.filter(order_code=i.order_code).all()

            list1 = []
            for order in orders_detail_list:
                dict2 = {
                    'image':order.goodsSku.default_image_url.url,
                    'name':order.goodsSku.name,
                    'price':order.goodsSku.price,
                    'number':order.goods_number,
                    'xiaoji':float(order.goodsSku.price * order.goods_number)
                }
                list1.append(dict2)
            
          
            # 订单表
            orders_dict = {
                'order_code':i.order_code,
                'total_manoy':i.total_manoy,
                'pay_type':i.pay_type,
                'status':i.status,
                'datetime':datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
            }

            dict1 = {
                'orders_detail':list1,
                'orders':orders_dict
            }
            data.append(dict1)
        data.reverse()
        return Response(data)





'''
    支付宝支付逻辑：前端但订单号发起请求获取，后台将支付宝支付链接拼接好返回给前端
    前端访问支付宝链接，用户扫描支付成功会将一些参数返回给 django 回调接口，回调接口
    将参数获取验证订单支付是否成功，True是成功，成功就修改该订单支付状态为已支付
'''
# AliPay：本身是一个 alipay 底层的类，这里将它重写封装到了 pay.py文件里，引入进来
from .pay import AliPay

def get_ali_object():

    '''
        初始化一个支付宝接口对象，该对象可以进行连接参数的构造，以及返回结果的校验
    '''

    app_id = "2016101000656732"  #  APPID （沙箱应用）

    # 支付完成后，支付偷偷向这里地址发送一个post请求，识别公网IP,如果是 192.168.20.13局域网IP ,支付宝找不到，def page2() 接收不到这个请求
    notify_url = 'http://localhost:8000/api/paymes/'   

    # 支付完成后，跳转的地址。
    return_url = 'http://localhost:8000/api/paymes/' 
    # return_url：返回路由，支付宝支付成功会返回一个参数，你需要那参数去验证订单支付是否成功，True或False

    merchant_private_key_path = "E:/Django_meiduo_shop/api_shop/private_key.txt" # 应用私钥
    alipay_public_key_path = "E:/Django_meiduo_shop/api_shop/public_key.txt"  # 支付宝公钥

    # AliPay:初始化参数数据
    alipay = AliPay(
        appid=app_id,
        app_notify_url=notify_url,
        return_url=return_url,
        app_private_key_path=merchant_private_key_path,
        alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
        debug=True,  # 默认False,
    )
    return alipay




# 支付成功返回的路由   
class Paymes(APIView):
    '''
        回调接口
        支付宝返回的参数：
        <QueryDict: {'charset': ['utf-8'], 'out_trade_no': ['201906201724018679285'], 'method': ['alipay.trade.page.pay.return'], 'total_amount': ['3500.00'], 'sign': ['Isn1me90kTE5gLsSWpuxDqu4k/ab/lgaQmcCvB/W+JhGphtp2762Zbnxm04bCVbqdTb2qfdIkWwilDAo1LOGLdlXiAHPRGnNfm8P/P51qgQg/4mN5B8D5KBjjKRJER88UiC227rnC4thHHHnsTsOgML4Vz3EMzOw+FXk5/pIWW5jzm96xvsjnErVNqbcjYVQu1ClfUt+Yqdy7Dh1cfsXiu3V6VY8r3Wd61gu48ooVhOcVdKmXjUga2/hr/5w7FNopJjUZnTPU8gcNrKrrPo/8eMQkBVJwg4AodscL/dq8gfns3p2yLdkXLvyisKDBmjxPH98MsyU3JHD75oduNz7PQ=='], 'trade_no': ['2019062122001400971000042952'], 'auth_app_id': ['2016101000656732'], 'version': ['1.0'], 'app_id': ['2016101000656732'], 'sign_type': ['RSA2'], 'seller_id': ['2088102179003700'], 'timestamp': ['2019-06-21 14:53:17']}>
    '''
    def get(self,request):

        params = request.GET.dict()         # 处理get参数部分
        order_code = params['out_trade_no']
        sign = params.pop('sign', None)     # 获取sign签证值
        alipay = get_ali_object()
        status = alipay.verify(params, sign) # 校验，如果校验成功则返回True
        
        if status == True:
            # 订单验证成功修改数据库支付状态
            Orders.objects.filter(order_code=order_code).update(status=2)


        return redirect('http://127.0.0.1:8080/#/user_center_order/')



# 订单付款
class Go_pay_money(APIView):

    '''
        接受前端请求拼接支付宝支付链接，将链接返回，前端发起三方支付链接请求
    '''

    def get(self,request,order_code):
        
        orderDetail = Ordersdetail.objects.filter(order_code=order_code).all()
        
        # 判断库存
        for i in orderDetail:
            if i.goods_number > i.goodsSku.stock:
                return Response({'code':201,'mes':'库存不足，付款失败'})

        order = Orders.objects.filter(order_code=order_code).first()    
        total_price = float(order.total_manoy)

        alipay = get_ali_object()

        # direct_pay: alipay的一个方法，需要携带参数访问
        query_params = alipay.direct_pay(
            subject=str(order.total_number)+'个商品',  # 商品简单描述
            out_trade_no=order_code,  # 用户购买的商品订单号（每次不一样） 20180301073422891
            total_amount=total_price,  # 交易金额(单位: 元 保留俩位小数)
        )

        # 将
        pay_url = "https://openapi.alipaydev.com/gateway.do?{0}".format(query_params)  # 支付宝网关地址（沙箱应用）

        return Response({'code':200,'pay_url':pay_url})

