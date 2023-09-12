# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

{
    'name': 'OpenEduCat Exam Enterprise',
    'version': '14.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Exam',
    'complexity': "easy",
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_exam',
        'openeducat_core_enterprise',
        'openeducat_student_progress_enterprise',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/op_security.xml',
        'data/exam_portal_menu.xml',
        'views/exam_view.xml',
        'views/exam_attendees_view.xml',
        'views/result_template_view.xml',
        'views/marksheet_register_view.xml',
        'views/marksheet_line_view.xml',
        'views/result_line_view.xml',
        'views/exam_room_view.xml',
        'views/exam_type_view.xml',
        'views/exam_dashboard_view.xml',
        'dashboard/exam_dashboard.xml',
        'wizards/progression_marksheet_wizard_view.xml',
        'views/exam_session_view.xml',
        'views/exam_onbaord.xml',
        'views/openeducat_exam_portal.xml',
        'views/openeducat_marksheet_line_view.xml',
        'views/openeducat_progression_marksheet_line.xml',
        'views/student_progression_exam_portal.xml',
        'views/assets.xml',
        'reports/exam_progression_report.xml',
    ],
    'demo': [
        'demo/progression_marksheet_demo.xml',
    ],
    'images': [
        'static/description/openeducat_exam_enterprise_banner.jpg',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 75,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
