# Generated by Django 5.0 on 2023-12-28 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storefront', '0007_alter_collection_feature_product_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='feature_product_id',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
