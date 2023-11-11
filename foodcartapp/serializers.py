from django.core.exceptions import ObjectDoesNotExist

from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import CharField
from rest_framework.serializers import ListField
from rest_framework.serializers import ValidationError

from .models import Product
from .models import Order
from .models import OrderItem


class OrderItemSerializer(ModelSerializer):

    product = CharField()

    def validate_product(self, value):
        try:
            Product.objects.get(id=value)
            return value
        except ObjectDoesNotExist:
            raise ValidationError(
                f'products: Недопустимый первичный ключ {value}'
            )

    class Meta:
        model = OrderItem
        fields = ['quantity', 'product']


class OrderSerializer(ModelSerializer):

    products = ListField(
        child=OrderItemSerializer(), allow_empty=False, write_only=True
    )

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']
