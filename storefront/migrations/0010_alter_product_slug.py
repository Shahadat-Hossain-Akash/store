# Generated by Django 5.0 on 2024-01-02 15:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "storefront",
            "0009_alter_product_options_alter_orderitem_unit_price_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="slug",
            field=models.SlugField(),
        ),
    ]
