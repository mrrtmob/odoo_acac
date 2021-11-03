# -*- coding: utf-8 -*-
{
    'name': "pm_lead",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Pathmazing Inc",



    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'crm',
        'mail',
        'sales_team',
        'utm',
        'board',
        # 'pm_culinary',
        'openeducat_admission',
        'openeducat_core',
        'openeducat_core_enterprise',

    ],

    # always loaded
    'data': [
        # 'security/marketing_security.xml',
        'security/ir.model.access.csv',
        'views/pm_lead.xml',
        'views/pm_campaign.xml',
        'views/marketing_dashboard.xml',
        'data/mail_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
