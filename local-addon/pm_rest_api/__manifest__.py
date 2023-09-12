# -*- coding: utf-8 -*-
{
    'name': "Pathmazing API",

    'summary': """ Created to create a Rest API for mobile app
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Pathmazing",
    'website': "https://pathmazing.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'openeducat_core', 'openeducat_rest', 'openeducat_core_enterprise'],

    'data': [
        'views/pm_payment_portal.xml',
        'data/payment_portal_menu.xml',
    ]

}
