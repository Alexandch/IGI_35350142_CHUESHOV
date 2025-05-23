# Generated by Django 5.2.1 on 2025-05-21 13:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery_app', '0004_manufacturer_order_delivery_cost_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_method',
            field=models.CharField(choices=[('pickup', 'Самовывоз'), ('courier', 'Курьер')], default='pickup', max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='delivery_app.employee'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Pending', 'В ожидании'), ('Shipped', 'Отправлен'), ('Delivered', 'Доставлен'), ('Canceled', 'Отменен')], default='Pending', max_length=20),
        ),
    ]
