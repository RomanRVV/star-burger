import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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


@api_view(['POST'])
def register_order(request):
    try:
        data = request.data
        products = data['products']
    except ValueError:
        return Response({
            'error': 'ValueError',
        })
    except KeyError:
        return Response({
            'products': 'Обязательное поле.',

        },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    if isinstance(products, str):
        return Response({
             'products': 'Ожидался list со значениями, но был получен "str" ',
        },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    if isinstance(products, list):
        if not products:
            return Response({
                'products': 'Этот список не может быть пустым.',
            },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    if not products:
        return Response({
            'products': 'Это поле не может быть пустым.',
        },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    order = Order.objects.create(first_name=data['firstname'],
                                 last_name=data['lastname'],
                                 phonenumber=data['phonenumber'],
                                 address=data['address'])

    for product in products:
        OrderItem.objects.create(order=order,
                                 product=Product.objects.get(id=product['product']),
                                 quantity=product['quantity'])
    return Response(data)
