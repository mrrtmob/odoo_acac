# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

{
    'name': 'OpenEduCat Student Attendance Kiosk',
    'version': '14.0.1.0',
    'category': 'Tools',
    "sequence": 3,
    'summary': 'Track student attendance',
    'complexity': "easy",
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_core',
        'openeducat_attendance_enterprise',
        'barcodes',
        'openeducat_student_progress_enterprise'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/web_asset_backend_template.xml',
        'views/op_student_progression_portal.xml',
        'views/student_attendance_view.xml',
        'views/op_student_view.xml',
        'menus/openeducat_student_attendance_enterprise_menu.xml',
        'reports/student_badge.xml',
        'reports/attendance_timesheet_progression_report.xml',
    ],
    'qweb': [
        "static/src/xml/student_attendance.xml",
    ],
    'images': [
        'static/description/openeducat_student_attendance_kiosk.jpg'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 100,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
