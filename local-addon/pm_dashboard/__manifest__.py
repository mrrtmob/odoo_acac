# -*- coding: utf-8 -*-
{
    'name': "PM Dashboard",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Pathmazing Inc",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'pm_students'
    ],

    # always loaded
    'data': [
        'views/dashboard_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],

    'qweb': [
        'static/src/xml/financial_dashboard.xml',
        'static/src/xml/registrar_dashboard.xml',
        'static/src/xml/marketing_dashboard.xml',
        'static/src/xml/pm_hr_dashboard.xml'
    ],
}
