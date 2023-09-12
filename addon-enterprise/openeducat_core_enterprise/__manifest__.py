# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

{
    'name': 'OpenEduCat Core Enterprise',
    'version': '14.0.1.0',
    'category': 'Education',
    "sequence": 1,
    'summary': 'Manage Students, Faculties and Education Institute',
    'complexity': "easy",
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'gamification',
        'openeducat_core',
        'openeducat_web',
        'openeducat_rest'
    ],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'wizard/op_grant_badge_wizard_view.xml',
        'data/portal_menu_data.xml',
        'views/batch_view.xml',
        'views/student_view.xml',
        'views/faculty_view.xml',
        'views/subject_view.xml',
        'views/student_badge_view.xml',
        'views/openeducat_personal_info_portal.xml',
        'views/openeducat_educational_info_portal.xml',
        'views/board_affiliation_view.xml',
        'views/op_section_view.xml',
        'views/onboard.xml',
        'views/openeducat_subject_registration_portal.xml',
        'views/assets.xml',
        'dashboard/openeducat_dashboard_view.xml',
        'views/course_view.xml',
        'views/subject_registration_analysis.xml',
        'menu/course_menu.xml'
    ],
    'css': [],
    'qweb': [
        'static/src/xml/custom.xml'
    ],
    'js': [],
    'images': [
        'static/description/openeducat_core_enterprise_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 300,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
