# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

{
    'name': 'OpenEduCat Attendance Enterprise',
    'version': '14.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Attendances',
    'complexity': "easy",
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_attendance',
        'openeducat_core_enterprise',
        'openeducat_student_progress_enterprise',
        'website'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/op_security.xml',
        'wizards/progression_attendance_wizard_view.xml',
        'data/auto_create_attendance_sheet.xml',
        'data/auto_create_attendance_sheet_if_session.xml',
        'views/templates.xml',
        'views/attendance_sheet_view.xml',
        'views/openeducat_dashboard_view.xml',
        'views/attendance_register.xml',
        'views/onboard.xml',
        'views/openeducat_attendance_portal.xml',
        'views/attendance_line_view.xml',
        'views/openeducat_progression_attendance.xml',
        'views/student_progression_attendance_portal.xml',
        'reports/attendance_progression_report.xml',
        'menu/attendance_portal_menu.xml'
    ],
    'demo': ['demo/progression_attendance_demo.xml',
             'demo/attendance_register_demo.xml'],
    'css': [],
    'qweb': [],
    'js': [],
    'images': [
        'static/description/openeducat_attendance_enterprise_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 75,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
