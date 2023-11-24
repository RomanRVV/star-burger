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

    products = OrderItemSerializer(many=True, allow_empty=False, write_only=True)
    phonenumber = PhoneNumberField()

    def create(self, validated_data):
        products = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for product in products:
            OrderItem.objects.create(
                order=order,
                price=product['product'].price,
                **product
            )
        return order

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']
