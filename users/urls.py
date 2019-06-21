from django.urls import path,re_path
from users import views
# Django REST framework JWT中提供了用户验证登录功能 只需要我们在路由中配置以下接口即可
from rest_framework_jwt.views import obtain_jwt_token,verify_jwt_token

urlpatterns = [
    # 使用正则路由传参
    re_path(r'image_code/(?P<image_uuid_code>[\w-]+)/',views.ImageCode.as_view(),name=''),
    path('check_username/',views.Check_username.as_view()),
    path('check_user_pwd/',views.Check_user_pwd.as_view()),
    path('check_user_phone/',views.Check_user_phone.as_view()),
    path('check_email/',views.Check_email.as_view()),
    path('sub_email/',views.Sub_email.as_view()),
    path('check_email_code/',views.Check_email_code.as_view()),
    path('sub_reg/',views.Sub_reg.as_view()),
    path('login/',obtain_jwt_token),     # JWT 验证登录
    path('verify/',verify_jwt_token),    # 验证 token 接口
    path('get_weibo_login/',views.Get_weibo_login.as_view()),
    path('get_weibo_uid/',views.Get_weibo_uid.as_view()),
    path('bind_user/',views.Bind_user.as_view()),
    path('user_info/',views.User_info.as_view()),
    path('user_pass/',views.User_pass.as_view()),
    path('send_email/',views.Send_email.as_view()),
    path('update_pwd/',views.Update_pwd.as_view()),
    path('get_edit_one/',views.Get_edit_one.as_view()),
    re_path(r'get_edit_two/(?P<one_city_id>\d+)/',views.Get_edit_two.as_view()),
    re_path(r'get_edit_three/(?P<two_city_id>\d+)/',views.Get_edit_three.as_view()),
    path('inert_addres/',views.Inert_addres.as_view()),
    path('get_address_mes/',views.Get_address_mes.as_view()),
    path('def_address_mes/',views.Def_address_mes.as_view()),
    re_path(r'set_def_address/(?P<adres_id>\d+)/',views.Set_def_address.as_view()),
    re_path(r'delete_def_address/(?P<adres_id>\d+)/',views.Delete_def_address.as_view()),
    re_path(r'redact_address/(?P<adres_id>\d+)/',views.Redact_address.as_view()),
    
]
