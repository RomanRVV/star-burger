from django.test import TestCase
import requests


test = requests.post('http://127.0.0.1:8000/api/order/').text
print(test)
