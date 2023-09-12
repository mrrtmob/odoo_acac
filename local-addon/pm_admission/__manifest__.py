# -*- coding: utf-8 -*-
{
    'name': "Pathmazing Admission",

    'summary': """
        Customize Admission module based on client needs""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Pathmazing Inc",
    'website': "https://pathmazing.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Education',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'crm',
                'pm_leads',
                'pm_students',
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
