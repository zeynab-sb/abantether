from django.db import migrations, models
import django.db.models.deletion

def create_initial_coins(apps, schema_editor):
    Coin = apps.get_model('coin', 'Coin')
    Coin.objects.get_or_create(name='ABAN', defaults={'price': 2})
    Coin.objects.get_or_create(name='BTC', defaults={'price': 10})

def migrate_currency_to_coin(apps, schema_editor):
    Order = apps.get_model('order', 'Order')
    Coin = apps.get_model('coin', 'Coin')
    
    # Get or create coins for existing orders
    coin_map = {}
    for order in Order.objects.all():
        if order.currency not in coin_map:
            coin, _ = Coin.objects.get_or_create(
                name=order.currency,
                defaults={'price': 1}  # Default price for existing coins
            )
            coin_map[order.currency] = coin
        order.coin = coin_map[order.currency]
        order.save()

class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
        ('coin', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_coins),
        migrations.AddField(
            model_name='order',
            name='coin',
            field=models.ForeignKey(
                'coin.Coin',
                on_delete=models.PROTECT,
                null=True,  # Allow null temporarily for migration
                related_name='orders'
            ),
        ),
        migrations.RunPython(migrate_currency_to_coin),
        migrations.AlterField(
            model_name='order',
            name='coin',
            field=models.ForeignKey(
                'coin.Coin',
                on_delete=models.PROTECT,
                null=False,  # Make it non-nullable after migration
                related_name='orders'
            ),
        ),
        migrations.RemoveField(
            model_name='order',
            name='currency',
        ),
    ] 