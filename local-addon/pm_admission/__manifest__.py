# -*- coding: utf-8 -*-
{
    'name': "pm_admission",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'crm',
                'pm_leads',
                'pm_general',
                'openeducat_admission',
                'utm',
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/mail_data.xml',
        'security/security.xml',
        'wizards/pm_admission_cancel_wizzard.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/pm_admission.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
