# -*- coding: utf-8 -*-
{
    'name': "pm_hr",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'hr_recruitment', 'pm_approval', 'pm_leads', 'hr_skills', 'hr_holidays', 'hr_contract'],

    # always loaded
    'data': [
        # 'security/hr_security.xml',
        'security/ir.model.access.csv',
        'views/pm_recruitment_view.xml',
        'views/pm_planning_view.xml',
        'data/contract_code.xml',
        'wizards/employee_certificate_view.xml',
        'wizards/applicant_create_employee_wizard_view.xml',
        'wizards/employee_recommendation_view.xml',
        'views/pm_employees.xml',
        'views/pm_contracts.xml',
        'views/pm_hr_leave.xml',
        # reports
        'reports/report_menu.xml',
        'reports/employee_certificate_report.xml',
        'reports/employee_recommendation_report.xml',
        'reports/report_footer.xml',
        'reports/offer_letter_report.xml',
        'reports/job_announcement_report.xml',
        'reports/interview_question_report.xml',
        'reports/interview_question_job_position.xml',
        'reports/applicant_report.xml',
        'views/pm_job_position_view.xml',
        'views/pm_application_view.xml',
        'data/recruitment_request_sequence.xml',
        'data/application_sequence.xml',
        'data/employee_sequence.xml',
        'data/ir_cron.xml',
        'data/mail_data.xml',
        'data/hr_recruitment_templates.xml',
        'data/hr_appraisal_templates.xml',
        'views/pm_employee_promotion.xml',
        'views/pm_employee_transfers.xml',
        'views/pm_activity_list.xml',
        'views/pm_training.xml',
        'views/tax_range_config_view.xml',
        'views/pm_survey.xml',
        'menus/hr_menu.xml',

    ],
}
