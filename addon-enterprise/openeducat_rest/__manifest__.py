# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################


{
    "name": "OpenEduCat REST API",
    "summary": """Restful API for OpenEduCat""",
    "version": "14.0",
    "category": "Extra Tools",
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/rest_menu.xml",
        "views/rest_token_view.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "images": [
        'static/description/banner.png'
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
    "price": 99.00,
    "currency": 'EUR',
}
