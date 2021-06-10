# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################


import os
import logging
import requests

import odoo
from odoo.tests import common

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

HOST = '127.0.0.1'
PORT = odoo.tools.config['http_port']

DB = "testing"
MPW = odoo.tools.config['admin_passwd'] or "admin"
LOGIN = "admin"
PW = "admin"


class RESTTestCase(common.TransactionCase):
    at_install = False
    post_install = True

    def setUp(self):
        super(RESTTestCase, self).setUp()

    def tearDown(self):
        super(RESTTestCase, self).tearDown()

    def url(self, url):
        if url.startswith('/'):
            url = "http://%s:%s%s" % (HOST, PORT, url)
        return url

    def authentication(self):
        response = requests.post(
            self.url('/api/authenticate'),
            data={
                'db': DB,
                'login': LOGIN,
                'password': PW})
        self.assertTrue(response)
        return response.json()['token']

    def test_verison(self):
        response = requests.get(self.url('/api'))
        self.assertTrue(response)

    def test_catch(self):
        response = requests.get(self.url('/api/noroute'))
        self.assertFalse(response)

    def test_authentication(self):
        response = requests.post(
            self.url('/api/authenticate'),
            data={
                'db': DB,
                'login': LOGIN,
                'password': PW})
        self.assertTrue(response)
        token = response.json()['token']
        response = requests.get(
            self.url('/api/life'),
            data={'token': token})
        self.assertTrue(response)
        response = requests.post(
            self.url('/api/refresh'),
            data={'token': token})
        self.assertTrue(response)
        response = requests.post(
            self.url('/api/close'),
            data={'token': token})
        self.assertTrue(response)
        response = requests.get(
            self.url('/api/life'),
            data={'token': token})
        self.assertFalse(response)

    def test_invalid_authentication(self):
        response = requests.post(
            self.url('/api/authenticate'),
            data={
                'db': DB,
                'login': "invalid",
                'password': "invalid"})
        self.assertFalse(response)

    def test_invalid_token(self):
        response = requests.get(
            self.url('/api/search'),
            data={'token': "invalid",
                  'model': 'res.partner'})
        self.assertFalse(response)

    def test_invalid_arguments(self):
        response = requests.get(
            self.url('/api/search'),
            data={})
        self.assertFalse(response)

    def test_search(self):
        token = self.authentication()
        response = requests.get(
            self.url('/api/search'),
            data={'token': token,
                  'model': 'res.partner'})
        self.assertTrue(response)
        response = requests.get(
            self.url('/api/search'),
            data={'token': token,
                  'model': 'res.partner',
                  'id': 1})
        self.assertTrue(response)
        response = requests.get(
            self.url('/api/search'),
            data={'token': token,
                  'model': 'res.partner',
                  'domain': '[["id", "=", 1]]'})
        self.assertTrue(response)

    def test_read(self):
        token = self.authentication()
        response = requests.get(
            self.url('/api/read'),
            data={'token': token,
                  'model': 'res.users',
                  'fields': '["login", "name"]'})
        self.assertTrue(response)

    def test_create(self):
        token = self.authentication()
        response = requests.post(
            self.url('/api/create'),
            data={'token': token,
                  'values': '{"name": "OpenEduCat IT"}'})
        self.assertTrue(response)

    def test_write(self):
        token = self.authentication()
        response = requests.put(
            self.url('/api/write'),
            data={'token': token,
                  'ids': '[1]',
                  'values': '{"name": "OpenEduCat IT"}'})
        self.assertTrue(response)
        response = requests.put(
            self.url('/api/write'),
            data={'token': token,
                  'ids': '[1]',
                  'values': '{"category_id": [[6, 0, [1]]]}'})
        self.assertTrue(response)

    def test_unlink(self):
        token = self.authentication()
        response = requests.delete(
            self.url('/api/unlink'),
            data={'token': token,
                  'model': 'res.users',
                  'ids': '[2]'})
        self.assertTrue(response)

    def test_method(self):
        token = self.authentication()
        response = requests.post(
            self.url('/api/call'),
            data={'token': token,
                  'method': 'copy',
                  'ids': '[1]'})
        self.assertTrue(response)
        response = requests.post(
            self.url('/api/call'),
            data={'token': token,
                  'method': 'fields_get_keys'})
        self.assertTrue(response)

    def test_report(self):
        token = self.authentication()
        response = requests.post(
            self.url('/api/report'),
            data={'token': token,
                  'report': 'base.report_ir_model_overview',
                  'model': 'ir.model',
                  'ids': '[1]'})
        self.assertTrue(response)

    def test_binary(self):
        token = self.authentication()
        response = requests.post(
            self.url('/api/binary'),
            data={'token': token,
                  'id': '1'})
        self.assertTrue(response)
