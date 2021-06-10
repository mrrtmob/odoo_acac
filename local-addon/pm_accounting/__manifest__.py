# -*- coding: utf-8 -*-
{
    'name': "Pathmazing Accounting",
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
        'account',
    ],

    # always loaded
    'data': [
        # 'views/pm_accounting.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_view.xml',
        'views/pm_accounting_views.xml',
        'views/reports_menu.xml',
        'reports/tax_invoice.xml',
        'reports/commercial_invoice.xml',
        'reports/commercial_without_tax.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
