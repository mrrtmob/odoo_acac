import requests
from odoo import http
from odoo.http import request
from dotenv import load_dotenv
from os.path import join, dirname
import os
import hmac
import hashlib
import base64
import json

class ABAPayWay(http.Controller):

    def __init__(self):
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)


    def get_api_key(self):
        key = os.environ.get("API_KEY")
        return key

    def get_merchant_id(self):
        id = os.environ.get("MERCHANT_ID")
        return id

    def get_api_url(self):
        env = os.environ.get("ENVIRONMENT")
        if env == "TEST":
            test_url = os.environ.get("API_URL_DEV")
            return test_url
        if env == "PRO":
            pro_url = os.environ.get("API_URL_PRO")
            return pro_url

    def get_push_back_url(self):
        url = os.environ.get("PUSHBACK_URL")
        urlSafeEncodedBytes = base64.urlsafe_b64encode(url.encode("utf-8"))
        urlSafeEncodedStr = str(urlSafeEncodedBytes, "utf-8")

        return urlSafeEncodedStr



    def get_hash(self, merchant_id, transaction_id, amount, items):
        # gege = items.decode("utf-8")

        message = bytes(merchant_id + transaction_id + amount + items, 'utf-8')
        key = self.get_api_key()
        secret = key.encode('utf-8')
        dig = hmac.new(secret, msg=message, digestmod=hashlib.sha512).digest()
        signature = base64.b64encode(dig).decode()
        print(signature)
        return signature;

    def get_transaction_items(self, payment_obj):
        print(payment_obj)
        lines = payment_obj.invoice_id.invoice_line_ids
        items = []
        key = 0
        for line in lines:
            items.append(key)
            items[key] = {}
            items[key]['name'] = line.product_id.name
            items[key]['quantity'] = line.quantity
            items[key]['price'] = line.price_subtotal
            key += 1

        json_str = json.dumps(items)
        res = base64.b64encode(json_str.encode('utf-8')).decode("utf-8")

        return res














