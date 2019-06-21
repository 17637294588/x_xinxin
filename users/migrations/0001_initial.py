# Generated by Django 2.0.4 on 2019-06-11 01:37

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('mobile', models.CharField(max_length=11, verbose_name='手机号')),
                ('email_active', models.BooleanField(default=False, verbose_name='邮箱')),
                ('avator', models.ImageField(blank=True, null=True, upload_to='avator', verbose_name='头像')),
                ('avator_url', models.URLField(blank=True, null=True, verbose_name='头像地址')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': '用户表',
                'db_table': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.CharField(max_length=20, verbose_name='收件人')),
                ('place', models.CharField(max_length=50, verbose_name='地址')),
                ('mobile', models.CharField(max_length=11, verbose_name='手机号')),
                ('email', models.CharField(blank=True, default='', max_length=30, null=True, verbose_name='邮箱')),
                ('is_delete', models.BooleanField(default=False, verbose_name='逻辑删除')),
                ('default_address', models.IntegerField(default=0, verbose_name='默认地址')),
            ],
            options={
                'verbose_name': '用户地址表',
                'db_table': 'address',
                'ordering': ['-update_time'],
            },
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=20, verbose_name='名字')),
                ('logo', models.ImageField(upload_to='', verbose_name='LOGO图片')),
                ('first_letter', models.CharField(max_length=1, verbose_name='品牌首字母')),
            ],
            options={
                'verbose_name_plural': '商品品牌',
                'db_table': 'tb_brand',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='城市名字')),
                ('city_id', models.IntegerField(verbose_name='城市ID')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subs', to='users.City')),
            ],
            options={
                'verbose_name_plural': '城市',
                'db_table': 'city',
            },
        ),
        migrations.CreateModel(
            name='Goods',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=50, verbose_name='名称')),
                ('sales', models.IntegerField(default=0, verbose_name='销量')),
                ('comments', models.IntegerField(default=0, verbose_name='评论数')),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='brand_goods', to='users.Brand', verbose_name='品牌')),
            ],
            options={
                'verbose_name_plural': '商品',
                'db_table': 'tb_goods',
            },
        ),
        migrations.CreateModel(
            name='GoodsCate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=10, verbose_name='名称')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.GoodsCate', verbose_name='商品父类')),
            ],
            options={
                'verbose_name_plural': '商品分类',
                'db_table': 'tb_goods_category',
            },
        ),
        migrations.CreateModel(
            name='GoodsChannle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
                ('group_id', models.IntegerField(verbose_name='组号')),
                ('url', models.CharField(max_length=50, verbose_name='商品页面链接')),
                ('sequence', models.IntegerField(verbose_name='顺序')),
                ('cate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.GoodsCate', verbose_name='商品频道')),
            ],
            options={
                'verbose_name_plural': '商品频道',
                'db_table': 'tb_goods_channel',
            },
        ),
        migrations.CreateModel(
            name='GoodsSku',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=50, verbose_name='名称')),
                ('caption', models.CharField(max_length=100, verbose_name='副标题')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='单价')),
                ('purchase_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='进价')),
                ('market_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='市场价')),
                ('stock', models.IntegerField(default=0, verbose_name='库存')),
                ('sales', models.IntegerField(default=0, verbose_name='销量')),
                ('comments', models.IntegerField(default=0, verbose_name='评论数量')),
                ('is_launched', models.BooleanField(default=True, verbose_name='是否上架')),
                ('default_image_url', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='商品默认图片')),
                ('cate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='users.GoodsCate', verbose_name='类别')),
                ('goods', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goods_sku', to='users.Goods', verbose_name='商品')),
            ],
            options={
                'verbose_name_plural': '商品SKU属性',
                'db_table': 'tb_sku',
            },
        ),
        migrations.CreateModel(
            name='GoodsSpecification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=20, verbose_name='规格分类')),
                ('goods', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Goods', verbose_name='商品')),
            ],
            options={
                'verbose_name_plural': '商品规格',
                'db_table': 'tb_goodsspecification',
            },
        ),
        migrations.CreateModel(
            name='SkuImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
                ('image', models.ImageField(upload_to='', verbose_name='图片')),
                ('sku', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.GoodsSku', verbose_name='sku')),
            ],
            options={
                'verbose_name_plural': 'SKU图片描述',
                'db_table': 'tb_sku_image',
            },
        ),
        migrations.CreateModel(
            name='SkuSpecification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'SKU规格',
                'db_table': 'tb_sku_specification',
            },
        ),
        migrations.CreateModel(
            name='SocialUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platfrom_id', models.IntegerField(choices=[(1, 'PC'), (2, 'Androia'), (3, 'IOS')], max_length=1, verbose_name='平台类型')),
                ('platfrom_type', models.IntegerField(choices=[(1, 'QQ'), (2, '微博'), (3, '微信')], max_length=1, verbose_name='社交平台')),
                ('uid', models.CharField(max_length=100, verbose_name='用户社交id')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_info', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name_plural': '用户社交表',
                'db_table': 'socialuser',
            },
        ),
        migrations.CreateModel(
            name='SpecificationOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
                ('value', models.CharField(max_length=20, verbose_name='规格选项')),
                ('spec', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.GoodsSpecification', verbose_name='规格分类')),
            ],
            options={
                'verbose_name_plural': '规格选项',
                'db_table': 'tb_specificationoption',
            },
        ),
        migrations.AddField(
            model_name='skuspecification',
            name='option',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='users.SpecificationOption', verbose_name='规格选项'),
        ),
        migrations.AddField(
            model_name='skuspecification',
            name='sku',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.GoodsSku', verbose_name='sku'),
        ),
        migrations.AddField(
            model_name='skuspecification',
            name='spec',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='users.GoodsSpecification', verbose_name='商品规格'),
        ),
        migrations.AddField(
            model_name='goods',
            name='cate1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cate1_goods', to='users.GoodsCate', verbose_name='一级分类'),
        ),
        migrations.AddField(
            model_name='goods',
            name='cate2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cate2_goods', to='users.GoodsCate', verbose_name='二级分类'),
        ),
        migrations.AddField(
            model_name='goods',
            name='cate3',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cate3_goods', to='users.GoodsCate', verbose_name='三级分类'),
        ),
        migrations.AddField(
            model_name='address',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='city_addres', to='users.City', verbose_name='市'),
        ),
        migrations.AddField(
            model_name='address',
            name='province',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='province_addres', to='users.City', verbose_name='省'),
        ),
        migrations.AddField(
            model_name='address',
            name='town',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='town_addres', to='users.City', verbose_name='区'),
        ),
        migrations.AddField(
            model_name='address',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addres', to=settings.AUTH_USER_MODEL, verbose_name='用户'),
        ),
    ]
