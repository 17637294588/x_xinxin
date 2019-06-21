from django.db import models
# 引入 AbstractUser 表
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
# Create your models here.


class Users(AbstractUser):
    mobile = models.CharField(max_length=11,verbose_name='手机号')
    email_active = models.BooleanField(default=False,verbose_name='邮箱')
    avator = models.ImageField(
        upload_to='avator',verbose_name='头像',
        null=True,
        blank=True,
        )
    '''
        image = request.FILES.get('img')
        image.read() -> write(fp)
        avator = image // 图片验证 png jpeg webp 
        pip install pillow 
        avator/1.png md5(时间戳)->1.png->abc.png 
            a: 1.png == 1.png == 1_z234v5.png 
        avator.url
    '''
    # 头像本地化处理
    avator_url = models.URLField(
        null=True,
        blank=True,
        verbose_name='头像地址',
        )
    # 头像云端处理


    class Meta:
        db_table = 'users'
        # django原生ORM创建出来的表
        # users_users
        verbose_name_plural = '用户表'    # 在django admin 后台显示的表名



# 第三方社交表
class SocialUser(models.Model):
    user = models.ForeignKey(Users,on_delete=models.CASCADE,verbose_name='用户',related_name='user_info')
    platfrom_type_choices = (
        (1,'PC'),
        (2,'Androia'),
        (3,'IOS'),
    )
    platfrom_id = models.IntegerField(max_length=1,choices=platfrom_type_choices,verbose_name='平台类型')

    platfrom_choices = (
        (1,'QQ'),
        (2,'微博'),
        (3,'微信'),
    )
    platfrom_type = models.IntegerField(max_length=1,choices=platfrom_choices,verbose_name='社交平台')
    uid = models.CharField(max_length=100,verbose_name='用户社交id')

    class Meta:
        db_table = 'socialuser'
        verbose_name_plural = '用户社交表'



# 城市表  自关联表
class City(models.Model):

    name = models.CharField(max_length=20,verbose_name='城市名字')
    city_id = models.IntegerField(verbose_name='城市ID')
    parent = models.ForeignKey(
        to = 'self',      # 自己关联自己
        on_delete = models.SET_NULL,
        null = True,     # 允许字段为 None值
        blank = True,    # 输入框可以不输入
        related_name = 'subs'    # 反向查询
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'city'
        verbose_name_plural = '城市'


# 时间表
class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time =  models.DateTimeField(auto_now_add=True)
    class Meta():
       abstract = True

# 地址表
class Address(BaseModel,models.Model):
    user = models.ForeignKey(Users,on_delete=models.CASCADE,related_name='addres',verbose_name='用户')
    receiver = models.CharField(max_length=20,verbose_name='收件人')
    # models.PROTECT：删除关联数据,引发错误ProtectedError
    province = models.ForeignKey(City,on_delete=models.PROTECT,related_name='province_addres',verbose_name='省')
    city = models.ForeignKey(City,on_delete=models.PROTECT,related_name='city_addres',verbose_name='市')
    town = models.ForeignKey(City,on_delete=models.PROTECT,related_name='town_addres',verbose_name='区')
    place = models.CharField(max_length=50,verbose_name='地址')
    mobile = models.CharField(max_length=11,verbose_name='手机号')
    email = models.CharField(max_length=30,null=True,blank=True,default="",verbose_name='邮箱')
    is_delete = models.BooleanField(default=False,verbose_name='逻辑删除')
    default_address = models.IntegerField(default=0,verbose_name='默认地址')

    class Meta:
        db_table = 'address'
        verbose_name = '用户地址表'
        ordering = ['-update_time']   # 默认的排序方式




# 商品分类表
class GoodsCate(BaseModel):
    
    name = models.CharField(max_length=10, verbose_name='名称')
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='商品父类',
    )

    class Meta:
        db_table = 'tb_goods_category'
        verbose_name_plural = '商品分类'

    def __str__(self):
        return self.name


# 商品频道表
class GoodsChannle(BaseModel):

    group_id = models.IntegerField(
        verbose_name='组号'
    )

    cate = models.ForeignKey(
        GoodsCate,
        on_delete = models.CASCADE,
        verbose_name = '商品频道'
    )

    url = models.CharField(
        max_length = 50,
        verbose_name = '商品页面链接'
    )

    sequence = models.IntegerField(
        verbose_name = '顺序'
    )

    class Meta:
        db_table = 'tb_goods_channel'
        verbose_name_plural = '商品频道'

    def __str__(self):
        return self.cate.name



# 品牌表
class Brand(BaseModel):

    name = models.CharField(
        max_length = 20,
        verbose_name = '名字'
    )

    logo = models.ImageField(
        verbose_name = 'LOGO图片'
    )

    first_letter = models.CharField(
        max_length = 1,
        verbose_name = '品牌首字母'
    )

    class Meta:
        db_table = 'tb_brand'
        verbose_name_plural = '商品品牌'

    def __str__(self):
        return self.name


# 商品表
class Goods(BaseModel):
    # 商品SPU，SPU一个产品的类型
    name = models.CharField(
        max_length = 50,
        verbose_name = '名称'
    )

    brand = models.ForeignKey(
        Brand,
        on_delete = models.PROTECT,   # 删除关联数据，会引发 ProtectedError，保护关联外键
        related_name='brand_goods',
        verbose_name = '品牌'
    )

    cate1 = models.ForeignKey(
        GoodsCate,
        on_delete = models.PROTECT,
        related_name = 'cate1_goods',
        verbose_name = '一级分类'
    )

    cate2 = models.ForeignKey(
        GoodsCate,
        on_delete = models.PROTECT,
        related_name = 'cate2_goods',
        verbose_name = '二级分类'
    )

    cate3 = models.ForeignKey(
        GoodsCate,
        on_delete = models.PROTECT,
        related_name = 'cate3_goods',
        verbose_name = '三级分类'
    )

    sales = models.IntegerField(
        default = 0,
        verbose_name = '销量'
    )

    comments = models.IntegerField(
        default = 0,
        verbose_name = '评论数'
    )

    desc_detail = RichTextUploadingField(default='', verbose_name='详细介绍')
    desc_pack = RichTextField(default='', verbose_name='包装信息')
    desc_service = RichTextUploadingField(default='', verbose_name='售后服务')
    
    class Meta:
        db_table = 'tb_goods'
        verbose_name_plural = '商品'

    def __str__(self):
        return self.name



# 商品规格表
class GoodsSpecification(BaseModel):

    goods = models.ForeignKey(
        Goods,
        on_delete = models.CASCADE,
        verbose_name = '商品'
    )

    name = models.CharField(
        max_length = 20,
        verbose_name = '规格分类'
    )

    class Meta:
        db_table = 'tb_goodsspecification'
        verbose_name_plural = '商品规格'

    def __str__(self):
        return '%s:%s' % (self.goods.name,self.name)




# 规格选项表
class SpecificationOption(BaseModel):

    spec = models.ForeignKey(
        GoodsSpecification,
        on_delete = models.CASCADE,
        verbose_name = '规格分类'
    )

    value = models.CharField(
        max_length = 20,
        verbose_name = '规格选项'
    )

    class Meta:
        db_table = 'tb_specificationoption'
        verbose_name_plural = '规格选项'

    def __str__(self):
        return '%s-%s' %(self.spec.name,self.value)



# 商品 SKU 属性表
class GoodsSku(BaseModel):

    name = models.CharField(max_length=50,verbose_name='名称')
    caption = models.CharField(max_length=100,verbose_name='副标题')
    goods = models.ForeignKey(
        Goods,
        on_delete = models.CASCADE,
        verbose_name = '商品',
        related_name = 'goods_sku'      
    )

    cate = models.ForeignKey(
        GoodsCate,
        on_delete = models.PROTECT,
        verbose_name = '类别'
    )

    price = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
        verbose_name = '单价'
    )

    purchase_price = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
        verbose_name = '进价'
    )

    market_price = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
        verbose_name = '市场价'
    )

    stock = models.IntegerField(
        default = 0,
        verbose_name = '库存'
    )

    sales = models.IntegerField(
        default = 0,
        verbose_name = '销量'
    )

    comments = models.IntegerField(
        default = 0,
        verbose_name = '评论数量'
    )

    is_launched = models.BooleanField(
        default = True,
        verbose_name = '是否上架'
    )

    default_image_url = models.ImageField(

        verbose_name='商品默认图片',
        null=True,
        blank=True,
    )

    class Meta:
        db_table = 'tb_sku'
        verbose_name_plural = '商品SKU属性'

    def __str__(self):
        return self.name



#  图片描述
class SkuImage(BaseModel):
    # sku图片描述
    sku = models.ForeignKey(
        GoodsSku,
        on_delete=models.CASCADE,
        verbose_name='sku',
    )
    image = models.ImageField(verbose_name='图片')

    class Meta:
        db_table = 'tb_sku_image'
        verbose_name_plural = 'SKU图片描述'

    def __str__(self):
        return self.sku.name


# SKU 规格信息表
class SkuSpecification(BaseModel):

    sku = models.ForeignKey(
        GoodsSku,
        on_delete = models.CASCADE,
        verbose_name = 'sku'
    )

    spec = models.ForeignKey(
        GoodsSpecification,
        on_delete = models.PROTECT,
        verbose_name = '商品规格'
    )

    option = models.ForeignKey(
        SpecificationOption,
        on_delete = models.PROTECT,
        verbose_name = '规格选项'
    )

    class Meta:
        db_table = 'tb_sku_specification'
        verbose_name_plural = 'SKU规格'

    def __str__(self):
        return self.sku.name

'''
     user = models.ForeignKey(Users,on_delete=models.CASCADE,verbose_name='用户',related_name='user_info')
    platfrom_type_choices = (
        (1,'PC'),
        (2,'Androia'),
        (3,'IOS'),
    )
    platfrom_id = models.IntegerField(max_length=1,choices=platfrom_type_choices,verbose_name='平台类型')
'''

# 订单表
class Orders(BaseModel):
    order_code = models.CharField(max_length=250,unique=True)
    user = models.ForeignKey(Users,on_delete=models.CASCADE,verbose_name='用户')
    total_number = models.IntegerField(verbose_name='总数量')
    total_manoy = models.DecimalField(decimal_places=2,max_digits=8,verbose_name='总金额')
    pay_type_choices = {
        (1,'货到付款'),
        (2,'支付宝')
    }
    pay_type = models.IntegerField(choices=pay_type_choices,verbose_name='支付方式')
    status_choices = {
        (1,'去付款'),
        (2,'已付款')
    }
    status = models.IntegerField(choices=status_choices,verbose_name='支付状态')
    address = models.IntegerField()

    class Meta:
        db_table = 'tb_sku_orders'
        verbose_name_plural = '订单表'



# 订单详情表
class Ordersdetail(BaseModel):
    order_code = models.CharField(max_length=250)
    goods_number = models.IntegerField(verbose_name='商品数量')
    goodsSku = models.ForeignKey(GoodsSku,on_delete=models.CASCADE,verbose_name='商品sku')
    
    class Meta:
        db_table = 'tb_sku_ordersdetail'
        verbose_name_plural = '订单详情表'