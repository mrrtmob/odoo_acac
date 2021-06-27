# -*- coding: utf-8 -*-
{
    'name': "pm_student_registration",

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
        'openeducat_admission'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/student_registration.xml',
        'views/complete.xml'
    ]
}
