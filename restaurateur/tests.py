from django.test import TestCase
import requests
from phonenumber_field.phonenumber import PhoneNumber

from star_burger.settings import PHONENUMBER_DEFAULT_REGION

#
# test = '+79186268110'
# number = PhoneNumber.from_string(test, region='RU')
# print(number.is_valid())
#
# # if isinstance(test, list):
# #     if not test:
# #         print('лист')

test = ""
print(type(test))
