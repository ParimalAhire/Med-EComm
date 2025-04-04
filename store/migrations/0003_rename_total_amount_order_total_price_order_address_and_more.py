# Generated by Django 5.1.6 on 2025-03-30 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_cart_cartitem'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='total_amount',
            new_name='total_price',
        ),
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.TextField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='alternate_phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='city',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_instructions',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='email',
            field=models.EmailField(default='', max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='full_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('COD', 'Cash on Delivery'), ('Online', 'Online Payment')], default='Online', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='phone',
            field=models.CharField(default='', max_length=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='pincode',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
            preserve_default=False,
        ),
    ]
