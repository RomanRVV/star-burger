import json

from django.http import JsonResponse
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
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


def check_products(data):
    try:
        products = data['products']
    except KeyError:
        return {
            'products': 'Обязательное поле.',
        }

    if isinstance(products, list):
        if not products:
            return {
                'products': 'Этот список не может быть пустым.',
            }
    else:
        if products:
            return {
                'products': f'Ожидался list со значениями, но был получен {type(products)} ',
            }

    if not products:
        return {
            'products': 'Это поле не может быть пустым.',
        }


def check_order(data):
    try:
        firstname = data['firstname']
        lastname = data['lastname']
        phonenumber = data['phonenumber']
        address = data['address']
    except KeyError:
        return {
            'firstname, lastname, phonenumber, address': 'Обязательное поле'
        }

    if isinstance(firstname, str):
        if not firstname:
            return {
                'firstname': 'Это поле не может быть пустым.',
            }
    else:
        return {
            'firstname': 'Not a valid string',
        }

    if isinstance(lastname, str):
        if not lastname:
            return {
                'lastname': 'Это поле не может быть пустым.',
            }
    else:
        return {
            'lastname': 'Not a valid string',
        }

    if isinstance(phonenumber, str):
        if not phonenumber:
            return {
                'phonenumber': 'Это поле не может быть пустым.',
            }
    else:
        return {
            'phonenumber': 'Not a valid string',
        }

    if isinstance(address, str):
        if not address:
            return {
                'address': 'Это поле не может быть пустым.',
            }
    else:
        return {
            'address': 'Not a valid string',
        }

    number = PhoneNumber.from_string(phonenumber, region='RU')
    if not number.is_valid():
        return {
            'phonenumber': 'Введен некорректный номер телефона'
        }


@api_view(['POST'])
def register_order(request):
    try:
        data = request.data
        if check_order(data):
            return Response(
                check_order(data),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        if check_products(data):
            return Response(
                check_products(data),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                            )
        products = data['products']
    except ValueError:
        return Response({
            'error': 'ValueError',
        })

    order = Order.objects.create(first_name= data['firstname'],
                                 last_name=data['lastname'],
                                 phonenumber=data['phonenumber'],
                                 address=data['address'])
    try:
        for product in products:
            OrderItem.objects.create(order=order,
                                     product=Product.objects.get(id=product['product']),
                                     quantity=product['quantity'])
    except ObjectDoesNotExist:
        return Response({
            'products': f'Недопустимый первичный ключ {product["product"]}'
        })
    return Response(data)
