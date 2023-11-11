from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ListField

from .models import Order
from .models import OrderItem

from phonenumber_field.serializerfields import PhoneNumberField


class OrderItemSerializer(ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['quantity', 'product']


class OrderSerializer(ModelSerializer):

    products = ListField(
        child=OrderItemSerializer(), allow_empty=False, write_only=True
    )
    phonenumber = PhoneNumberField()

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for product_data in products_data:
            OrderItem.objects.create(
                order=order,
                price=product_data['product'].price,
                **product_data
            )
        return order

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']
