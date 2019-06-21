from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Users)
admin.site.register(models.SocialUser)
admin.site.register(models.City)
admin.site.register(models.Address)

admin.site.register(models.GoodsCate)
admin.site.register(models.GoodsChannle)
admin.site.register(models.Brand)
admin.site.register(models.Goods)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.GoodsSku)
admin.site.register(models.SkuImage)
admin.site.register(models.SkuSpecification)
admin.site.register(models.Orders)
admin.site.register(models.Ordersdetail)