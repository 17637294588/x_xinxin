from users import models
from rest_framework import serializers



# 频道序列化器
class ChannleSerializer(serializers.ModelSerializer):

    cate = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = models.GoodsChannle
        fields = '__all__'


# 分类序列化器
class cateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.GoodsCate
        fields = '__all__'



# 商品 sku 序列化器
class GoodsSkuSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.GoodsSku
        fields = ('id', 'name', 'price', 'default_image_url', 'comments','caption')





