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
    'name': 'OpenEduCat Web',
    'version': '14.0.1.0',
    'category': 'Education',
    "sequence": 1,
    'summary': 'Manage Students, Faculties and Education Institute',
    'complexity': "easy",
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'web',
        'openeducat_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_param_data.xml',
        'views/assets.xml',
        'views/res_config_setting_view.xml',
        'views/webclient_templates.xml',
        'views/openeducat_portal_menu.xml',
        'views/openeducat_student_portal_menus.xml',
        'views/course_navbar_templates.xml',
    ],
    'demo': [
    ],
    'css': [],
    'qweb': [
        'static/src/xml/menu_content.xml',
        'static/src/xml/subscription.xml',
    ],
    'js': [
    ],
    'images': [
        'static/description/openeducat_enterprise_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
