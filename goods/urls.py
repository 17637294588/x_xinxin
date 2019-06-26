from django.urls import path,re_path
from goods import views
# Django REST framework JWT中提供了用户验证登录功能 只需要我们在路由中配置以下接口即可
from rest_framework_jwt.views import obtain_jwt_token,verify_jwt_token

urlpatterns = [
    # 使用正则路由传参
    # re_path(r'image_code/(?P<image_uuid_code>[\w-]+)/',views.ImageCode.as_view(),name=''),
    path('goods_channel/',views.Goods_channel.as_view()),
    re_path(r'list_goods_mes/(?P<cid>\d+)/',views.List_goods_mes.as_view()),
    re_path(r'get_detail_goods/',views.Get_detail_goods.as_view()),
    re_path(r'check_sku/(?P<id>\d+)/',views.Check_sku.as_view()),
    path(r'add_detail/',views.Add_detail.as_view()),
    re_path(r'cart/(?P<sku_id>\d+)/',views.Cart.as_view()),
    path(r'send_redis/',views.Send_redis.as_view()),
    re_path(r'cart_mes/(?P<user_id>\d+)/',views.Cart_mes.as_view()),
    path(r'sub_order/',views.Sub_order.as_view()),
    re_path(r'get_orders_message/',views.Get_orders_message.as_view()),
    path(r'change_adres/',views.Change_adres.as_view()),
    re_path(r'get_my_orders/',views.Get_my_orders.as_view()),
    re_path(r'paymes/',views.Paymes.as_view()),
    re_path(r'go_pay_money/(?P<order_code>\d+)/',views.Go_pay_money.as_view()),
    re_path(r'refund_money/(?P<order_code>\d+)/',views.Refund_money.as_view()),
    path(r'alipayreturn/',views.Alipayreturn.as_view()),
    path(r'return_money/',views.Return_money.as_view()),

    path(r'demo/',views.Demo.as_view()),

]
