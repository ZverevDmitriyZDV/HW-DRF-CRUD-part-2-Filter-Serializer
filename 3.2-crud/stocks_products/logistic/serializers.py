from rest_framework import serializers

from logistic.models import Product, Stock, StockProduct


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['address', 'positions']

    def create(self, validated_data):

        positions = validated_data.pop('positions')
        stock = super().create(validated_data)
        need_stock = Stock.objects.filter(address=validated_data['address']).values()
        stock_id = list(need_stock.values())[0]['id']

        for product_position in positions:
            product_position['stock_id'] = stock_id
            print(product_position)
            StockProduct(**product_position).save()

        return stock

    def update(self, instance, validated_data):

        positions = validated_data.pop('positions')
        stock = super().update(instance, validated_data)

        for product_position in positions:

            stock_product_needed = StockProduct.objects.get(stock_id=instance.id, product=product_position['product'])
            stock_product_needed.price = product_position.get('price', stock_product_needed.price)
            stock_product_needed.quantity = product_position.get('quantity', stock_product_needed.quantity)
            stock_product_needed.save()

        return stock
