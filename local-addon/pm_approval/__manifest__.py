# -*- coding: utf-8 -*-
{
    'name': "Pathmazing Approval",
    "sequence": 1,
    'category': 'Education',
    'summary': 'Approval Process',
    'author': "Pathmazing Inc",
    'website': "https://pathmazing.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'openeducat_discipline',
                'openeducat_core',
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/pm_approval.xml',
        'menus/approval_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
