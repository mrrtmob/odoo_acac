# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################


import io
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


class RESTTestCase(common.BaseCase):
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

    def test_change_password(self):
        response = requests.post(
            self.url('/api/change_master_password'),
            data={
                'password_old': MPW,
                'password_new': "new_pw"})
        self.assertTrue(response)
        response = requests.post(
            self.url('/api/change_master_password'),
            data={
                'password_old': "new_pw",
                'password_new': MPW})
        self.assertTrue(response)

    def test_database_list(self):
        response = requests.get(self.url('/api/database/list'))
        self.assertTrue(response)

    def test_database_create(self):
        response = requests.post(
            self.url('/api/database/create'),
            data={
                'master_password': MPW,
                'database_name': "create_db",
                'admin_login': LOGIN,
                'admin_password': PW})
        self.assertTrue(response)
        response = requests.post(
            self.url('/api/database/drop'),
            data={
                'master_password': MPW,
                'database_name': "create_db"})
        self.assertTrue(response)

    def test_database_clone(self):
        response = requests.post(
            self.url('/api/database/duplicate'),
            data={
                'master_password': MPW,
                'database_old': DB,
                'database_new': "clone"})
        self.assertTrue(response)
        response = requests.post(
            self.url('/api/database/drop'),
            data={
                'master_password': MPW,
                'database_name': "clone"})
        self.assertTrue(response)

    def test_backup(self):
        response = requests.post(
            self.url('/api/database/backup'),
            data={
                'master_password': MPW,
                'database_name': DB})
        self.assertTrue(response)
        backup_file = io.BytesIO(response.content)
        response = requests.post(
            self.url('/api/database/restore'),
            data={
                'master_password': MPW,
                'database_name': "restore_db"},
            files={
                'backup_file': (
                    "backup.zip",
                    backup_file,
                    'application/x-zip-compressed',
                    {'Expires': '0'})})
        self.assertTrue(response)
        response = requests.post(
            self.url('/api/database/drop'),
            data={
                'master_password': MPW,
                'database_name': "restore_db"})
        self.assertTrue(response)
