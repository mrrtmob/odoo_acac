# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

import time
import logging

from odoo import models, api, fields

_logger = logging.getLogger(__name__)

try:
    import secrets

    def token_urlsafe():
        return secrets.token_urlsafe(64)
except ImportError:
    import re
    import uuid
    import base64

    def token_urlsafe():
        rv = base64.b64encode(uuid.uuid4().bytes).decode('utf-8')
        return re.sub(
            r'[\=\+\/]',
            lambda m: {'+': '-', '/': '_', '=': ''}[m.group(0)], rv)


class RESTToken(models.Model):
    _name = 'openeducat_rest.token'
    _description = 'openeducat rest tokens'

    token = fields.Char(
        string="Token",
        required=True)

    lifetime = fields.Integer(
        string="Lifetime",
        required=True)

    user = fields.Many2one(
        'res.users',
        string="User",
        required=True)

    @api.model
    def lifetime_token(self, token):
        token = self.search([['token', '=', token]], limit=1)
        if token:
            return int(token.lifetime - time.time())
        return False

    @api.model
    def delete_token(self, token):
        token = self.search([['token', '=', token]], limit=1)
        if token:
            return token.unlink()
        return False

    @api.model
    def refresh_token(self, token, lifetime=3600):
        token = self.search([['token', '=', token]], limit=1)
        if token:
            timestamp = int(time.time() + lifetime)
            return token.write({'lifetime': timestamp})
        return False

    @api.model
    def check_token(self, token):
        token = self.search([['token', '=', token]], limit=1)
        return token.user.id if token and int(time.time()) < token.lifetime else False

    @api.model
    def generate_token(self, uid, lifetime=3600):
        token = token_urlsafe()
        timestamp = int(time.time() + lifetime)
        return self.create({'token': token, 'lifetime': timestamp, 'user': uid})

    @api.model
    def _garbage_collect(self):
        token = self.search([['lifetime', '>', int(time.time())]], limit=1)
        token.unlink()
