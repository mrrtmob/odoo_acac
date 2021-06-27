# -*- coding: utf-8 -*-
{
    'name': "pm_general",

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
        'mail',
        'openeducat_core',
        'openeducat_core_enterprise',
        'openeducat_classroom',
        'openeducat_discipline',
        'openeducat_exam',
        'pm_approval',
        # 'pm_admission',

    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/pm_subject_view.xml',
        'views/pm_placement_view.xml',
        'views/pm_misbehaviour_category_view.xml',
        'views/pm_fees_view.xml',
        'views/pm_discipline_view.xml',
        'views/pm_exam_view.xml',
        'views/pm_attendance_view.xml',
        'views/pm_class_view.xml',
        'views/pm_semester_view.xml',
        'menus/exam_menu.xml',
        'menus/dashboard_menu.xml',
        'views/pm_student_course.xml',
        'views/pm_student_portal.xml',
        'views/pm_menu_icons.xml',
        'views/template_asset.xml',
        # 'src/xml/custom_dashboard.xml',
        'views/pm_faculties.xml',
        'views/pm_payslip_report_menu.xml',

        # for template report
        'reports/report_menu.xml',
        'reports/report_header.xml',
        'reports/report_footer.xml',
        'reports/report_page_border.xml',
        'reports/signature.xml',
        'reports/course_absence_1st_warning.xml',
        'reports/course_absence_invalidation.xml',
        'reports/disciplinary_1st_warning.xml',
        'reports/disciplinary_2nd_warning.xml',
        'reports/disciplinary_dismissal.xml',
        'reports/internship_1st_warning.xml',
        'reports/internship_2nd_warning.xml',
        'reports/internship_dismissal.xml',
        'reports/semester_absence_1st_warning.xml',
        'reports/semester_absence_2nd_warning.xml',
        'reports/semester_absence_dismissal.xml',
        'reports/payslipdetail.xml',
        'reports/payslip_header.xml',

        'wizards/student_transcript_wizard_view.xml'
    ]
}
