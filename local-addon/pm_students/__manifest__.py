# -*- coding: utf-8 -*-
{
    'name': "Pathmazing Student",

    'summary': """
        Customize student object according to client needs""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Pathmazing",
    'website': "https://pathmazing.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Education',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'board',
                'openeducat_core',
                'openeducat_fees',
                'openeducat_placement_enterprise',
                'openeducat_core_enterprise',
                'openeducat_admission',
                'openeducat_discipline',
                'pm_leads',
                'report_xlsx',
                'pm_general',
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/student_return_wizard_view.xml',
        'views/pm_student_view.xml',
        'views/pm_student_dashboard.xml',
        'views/pm_student_fee_view.xml',
        'views/pm_student_fee_line_view.xml',
        'reports/report_menu.xml',
        'reports/student_transcript.xml',
        'reports/student_id_card.xml',
        'reports/student_fee_report.xml',
        'wizards/student_fee_report_wizzard.xml',
    ],

}
