# Generated by Django 4.1.2 on 2023-02-02 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0002_alter_buyer_pic4_alter_product_pic1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='finalprice',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='discount',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]