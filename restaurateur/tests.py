from django.test import TestCase
import requests
from phonenumber_field.phonenumber import PhoneNumber
from foodcartapp.models import *
from star_burger.settings import PHONENUMBER_DEFAULT_REGION

test = Order.objects.get(id=54)
print(test.price)
