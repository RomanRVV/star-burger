import json

from django.http import JsonResponse
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import CharField
from rest_framework.serializers import ListField
from rest_framework.serializers import ValidationError
from rest_framework import status
from phonenumber_field.phonenumber import PhoneNumber

from .models import Product
from .models import Order
from .models import OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


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


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    order = Order.objects.create(firstname=serializer.validated_data['firstname'],
                                 lastname=serializer.validated_data['lastname'],
                                 phonenumber=serializer.validated_data['phonenumber'],
                                 address=serializer.validated_data['address'])

    products = serializer.validated_data['products']
    print(products)
    for product in products:
        print(product)
        OrderItem.objects.create(order=order,
                                 product=Product.objects.get(id=product['product']),
                                 quantity=int(product['quantity']))

    order_serializer = OrderSerializer(order)

    return Response(order_serializer.data)
