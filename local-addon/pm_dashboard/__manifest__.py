# -*- coding: utf-8 -*-
{
    'name': "PM Dashboard",

    'summary': """
        Created Registrar Dashboard, HR Dashboard, Marketing Dashboard, Accounting Dashboard""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Pathmazing Inc",
    'website': "https://pathmazing.com/",

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
