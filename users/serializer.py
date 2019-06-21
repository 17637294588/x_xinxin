from users import models
from rest_framework import serializers
from django.contrib.auth.hashers import check_password

# 定义序列化器
class userSerializer(serializers.ModelSerializer):
    '''
        序列化器：
            接受的参数就是 request.data
            序列化器接受的 data 里面有 password2 这个字段我不需要入库这边只需要判断和第一次密码
            是否一致，所以要先为 password2 定义一个字段
    '''
    password2 = serializers.CharField(
        min_length=6,    # 长度至少6位
        max_length=20,   # 最长20位
        required=True,   # 那个data里必须得有一个叫password2的字段
        write_only=True, # 只能被填写 不能被返回
        error_messages={
            'min_length': '太短了',
            'max_length': '太长了',
        }
        
            # 错误做键 ，value为错误信息
            # 反序列化才有password2去接收 write_only 别人给我的
            # 序列化返回的时候 数据库里是没有password2，是不需要返回的 
            # read_only 我给别人的 是不需要给password2
           
    ) 

    password = serializers.CharField(
        min_length=6,    # 长度至少6位
        max_length=20,   # 最长20位
        required=True,   # 那个data里必须得有一个叫password2的字段
        write_only=True, # 只能被填写 不能被返回
        error_messages={
            'min_length': '太短了',
            'max_length': '太长了',
        }
        
            # 错误做键 ，value为错误信息
            # 反序列化才有password2去接收 write_only 别人给我的
            # 序列化返回的时候 数据库里是没有password2，是不需要返回的 
            # read_only 我给别人的 是不需要给password2
           
    ) 
    #整体校验 
    def validate(self,attrs):
        # attrs == request.data 是一个整体数据属性
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一样')
        return attrs
    
    # POST提交数据 存储 
    # create 创建
    # update 修改

    # 创建序列化对象
    def create(self,validate):
        # validate == attrs
        # 入库前要先把 password2 从序列化器里删除掉
        del validate['password2']
        users = models.Users.objects.create_user(**validate)   # 创建用户

        return users

    '''
        下面反序列化操作
        fields 里面有 password2 ？？？
        fields 是指定反序列化的字段
    '''
    class Meta:
        fields = ('username', 'password', 'password2', 'email', 'mobile')
        model = models.Users   # 指定的表




'''
    将对象反序列化用到的是 data传参
    socialuser = serializer.socialuserSerializer(data=queryDict_socialuser,context={'outer_key':users})
    将数据序列化用到的是 instance传参
    data_socialuser = serializer.socialuserSerializer(instance=socialuser_data)
    将对象序列化后传给前端是 data_socialuser.data
'''
# 用户社交表 反序列化器
class socialuserSerializer(serializers.ModelSerializer):

    # 外键字段设为可读字段   是为了序列化查询用的
    # PrimaryKeyRelatedField：只显示外键关联对象的主键ID
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:

        fields = "__all__"
        model = models.SocialUser   # 指定的表
        related_name='user_info'
    def create(self,validated_data):
        
        #                                     反序列化入库外键对象要传参过来  user：表外键字段
        users = models.SocialUser.objects.create(user=self.context['outer_key'],**validated_data)   # 创建用户

        return users



# 定义验证密码序列化器  修改密码
class ChangePasswordSerializer(serializers.Serializer):
    # read_only 我给别人的 是不需要给password2
    old_password = serializers.CharField(
        min_length=8,
        max_length=20,
        required=True, # 那个data里必须得有一个叫password2的字段
        write_only=True, # 只能被填写 不能被返回
        error_messages={
            'min_length': '太短了',
            'max_length': '太长了',
        }
    )    

    new_password = serializers.CharField(
        min_length=8,
        max_length=20,
        required=True, # 那个data里必须得有一个叫password2的字段
        write_only=True, # 只能被填写 不能被返回
        error_messages={
            'min_length': '太短了',
            'max_length': '太长了',
        }
    )    

    def update(self,instance,validate):
        '''
            instance:是views传过来的数据，是当前用户对象，里面有用户信息
            validate：是views 传过来的数据，是前端vue传过来的数据
        '''

        # 将旧密码和新密码都从前端发送过来的容器里取出来
        old_password = validate['old_password']
        new_password = validate['new_password']
        
        if check_password(old_password,instance.password):
            # 前端发来的旧密码和用户解析出来的密码校验成功 就赋值新密码
            instance.set_password(new_password)
            instance.save()
        else:
            # 抛出错误
            raise serializers.ValidationError('旧密码输入错误')
        # 操作成功将 instance 返回 views
        return instance

   

# 找回密码修改密码入库 因为这里只操作了 password 所以没必要用 ModelSerializer
class FindPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only = True,
        min_length = 8,
        max_length = 20,
        error_messages={
            'min_length': '太短了',
            'max_length': '太长了',
        }
    )
    
    def update(self,instance,validate):
        # instance 当前用户对象 set_password:设置密码 validate:views接受的前端数据
        instance.set_password(validate['password'])
        instance.save()
        return instance     # 将修改过的用户返回 views
    

   
# 城市表序列化器
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.City
        fields = ('city_id','name')



# 地址表序列化器
class addressSerializer(serializers.ModelSerializer):

    # 外键字段设为可读字段   是为了序列化查询用的
    # PrimaryKeyRelatedField：只显示外键关联对象的主键ID
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    # 指定反序列化入库的外键
    province = serializers.IntegerField(label='省ID', write_only= True)
    city = serializers.IntegerField(label='市ID', write_only= True)
    town = serializers.IntegerField(label='区ID', write_only= True)


     # 序列化输出   外键入库的是ID，但我需要查询出来的是 名字，这里定义外键输出类型
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    town = serializers.StringRelatedField(read_only=True)

    
    class Meta:

        fields = "__all__"
        model = models.Address   # 指定的表

    def create(self,validated_data):
        
        #  反序列化入库外键对象要传参过来  user：表外键字段
        users = models.Address.objects.create(
            user=self.context['user'],
            province=self.context['province'],
            city=self.context['city'],
            town=self.context['town'],
            **validated_data
            )   # 创建用户

        return users



