# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

{
    'name': 'OpenEduCat Job Enterprise',
    'version': '14.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Job',
    'complexity': "easy",
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': ['base',
                'openeducat_core_enterprise',
                'website_form'],
    'data': ['security/op_security.xml',
             'security/ir.model.access.csv',
             'data/job_post_code.xml',
             'data/config_data.xml',
             'data/job_applicant_code.xml',
             'views/job_applicant_templates.xml',
             'views/job_applicant_view.xml',
             'views/job_post_view.xml',
             'views/job_type_view.xml',
             'views/student_view.xml',
             'views/web_job_post_view.xml',
             'views/job_post_apply_template.xml',
             'views/openeducat_student_job_post_portal.xml',
             'views/stages_demo.xml',
             'views/templates.xml',
             'menus/op_menu.xml'],
    'demo': ['demo/job_type_demo.xml',
             'demo/job_post_view_demo.xml',
             'demo/job_post_applicant_demo.xml'],
    'images': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 100,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
