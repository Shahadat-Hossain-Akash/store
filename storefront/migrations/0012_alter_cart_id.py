# Generated by Django 5.0 on 2024-01-05 15:10

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("storefront", "0011_alter_orderitem_product_review"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cart",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, primary_key=True, serialize=False
            ),
        ),
    ]