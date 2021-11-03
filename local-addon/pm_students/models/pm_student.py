# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import qrcode
import base64
from io import BytesIO
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import calendar


class PMStudentProgression(models.Model):
    _name = 'pm.student.progress'
    class_id = fields.Many2one('op.classroom', 'Class')
    course_id = fields.Many2one('op.course', 'Course')
    batch_id = fields.Many2one(
        'op.batch', 'Term')
    student_id = fields.Many2one('op.student', 'Student Name', required=False)
    date = fields.Date()
    remarks = fields.Text("Remarks")
    return_date = fields.Date("Returning Date")

    education_status = fields.Selection([('active', 'Active'),
                                         ('return', 'Returned'),
                                         ('enrollment', 'Enrollment'),
                                         ('postponed', 'Postponed'),
                                         ('withdrawn', 'Withdrawn'),
                                         ('graduated', 'Graduated'),
                                         ('dismissed', 'Dismissed')
                                         ], 'Status', default='active')

    def store_progression(self, student_id=False, course_id=False,
                                batch_id=False, status=False, remarks=False):
        progress_obj = self.env['pm.student.progress'].sudo()
        val = {
            'student_id': student_id,
            'date': datetime.today(),
            'remarks': remarks,
            'education_status': status,
            'course_id': course_id,
            'batch_id': batch_id,

        }
        print(val)
        progress_obj.create(val)



class OpStudentCourse(models.Model):
    _inherit = 'op.student.course'
    p_active = fields.Boolean('Active', default=True)
    class_id = fields.Many2one('op.classroom', 'Class')
    class_ids = fields.Many2many('op.classroom')
    custom_subject_ids = fields.One2many('pm.student.course.subject', inverse_name='op_student_course_id', string="Subjects")
    education_status = fields.Selection([('active', 'Active'),
                                         ('postponed', 'Postponed'),
                                         ('withdrawn', 'Withdrawn'),
                                         ('graduated', 'Graduated'),
                                         ('dismissed', 'Dismissed'),
                                         ('retake', 'Retake')
                                         ], 'Status', default='active')

    p_e_subject_ids = fields.Many2many('op.subject', relation='student_e_subjects_rel', readonly=False, string='Exempted Subjects')
    is_saved = fields.Boolean(default=False)
    cancel_date = fields.Date(default=lambda self: fields.Datetime.now())
    remarks = fields.Text("Remarks")
    return_date = fields.Date("Returning Date")
    reminding_date = fields.Date(compute="_compute_remind_date", store=True)
    is_reminded = fields.Boolean()
    starting_semester_id = fields.Many2one('pm.semester', 'Starting Semester')

    def compute_custom_subject(self):
        print("hit")
        courses = self.env['op.student.course'].search([])
        for course in courses:
            if course.subject_ids:
                data = []
                print(course.subject_ids)
                for subject in course.subject_ids:
                    val = {
                        'op_student_course_id': course.id,
                        'op_subject_id': subject.id,
                        'is_completed': False
                       }
                    data.append(val)
                print(val)
                self.env['pm.student.course.subject'].create(data)


    def student_reminder_scheduler(self):
        print("Hit Function")
        all_course_search = self.env['op.student.course'].sudo().search(
            [('education_status', '=', 'postponed'),
             ('is_reminded', '!=', True),
             ('return_date', '!=', None)])

        today = fields.Date.today()
        print(all_course_search)
        for course in all_course_search:
            print(today)
            print(course.reminding_date)
            if today == course.return_date or today == course.reminding_date:
                student = course.student_id

                print("Student", student.name)
                ir_model_data = self.env['ir.model.data']
                try:
                    template_id = ir_model_data.get_object_reference('pm_leads', 'student_follow_up_reminder')[1]
                except ValueError:
                    template_id = False
                self.env['mail.template'].browse(template_id).send_mail(course.id, force_send=True)
                if today == course.return_date:
                    print('TODAY!!')
                    course.is_reminded = True

    # @api.onchange('p_e_subject_ids')
    # def onChangeExemptedSubjects(self):
    #     print("Shiba")
    #     e_subjects = self.p_e_subject_ids.ids
    #     sub_array = []
    #     print(e_subjects)
    #     print(self.custom_subject_ids)
    #     for sub in self.custom_subject_ids:
    #         if sub.op_subject_id.id in e_subjects:
    #             record = self.env['pm.student.course.subject'].browse(sub._origin.id)
    #             print(record)
    #             record.unlink()



    @api.depends('p_e_subject_ids')
    def onDepend(selfs):
        print("GEGE")






    @api.depends('return_date')
    def _compute_remind_date(self):
        for course in self:
            if course.return_date:
                return_date = course.return_date
                d = timedelta(days=60)
                date = return_date - d
                course.reminding_date = date

    @api.model
    def create(self, val):
        val['is_saved'] = True
        res = super(OpStudentCourse, self).create(val)
        return res



    @api.onchange('course_id')
    def _onchange_course_id(self):
        self.batch_id = None

# tem

# class OpLibraryCardCustom(models.Model):
#     _inherit = "op.library.card"
#     _rec_name = "student_card_id"
#     student_card_id = fields.Char(related='student_id.student_app_id', store=True)

class StudentCourseSubject(models.Model):
    _name = 'pm.student.course.subject'
    _rec_name = 'op_subject_id'
    op_student_course_id = fields.Many2one('op.student.course')
    op_subject_id = fields.Many2one('op.subject')
    color = fields.Integer('Color Index', compute='_compute_color')
    is_completed = fields.Boolean('Completed')
    transcript_mark = fields.Boolean('Mark as Incomplete in Transcript')

    @api.depends('is_completed')
    def _compute_color(self):
        for subject in self:
            if subject.is_completed:
                subject.color = 7  # green
            else:
                subject.color = 9

class StudentPaymentInstallment(models.Model):
    _name = 'pm.student.installment'
    remarks = fields.Text("Remarks")
    student_id = fields.Many2one('op.student', 'Student')

    semester = fields.Selection([("basic", "Basic"),
                                 ("internship1", "Internship 1"),
                                 ("advance", "Advance"),
                                 ("internship2", "Internship 2")])
    fee_id = fields.Many2one('op.student.fees.details', store=True)
    invoice_id = fields.Many2one('account.move', 'Invoice ID')
    date = fields.Date(realted='fee_id.date', string="Generated Date")
    due_date = fields.Date("Due Date")
    amount = fields.Monetary("Amount")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('invoice', 'Invoice Created'),
        ('cancel', 'Cancel')
    ], string='Status', copy=False)
    invoice_state = fields.Selection(related="invoice_id.state",
                                     string='Invoice Status',
                                     readonly=True)


    def action_get_invoice(self):
        value = True
        if self.invoice_id:
            form_view = self.env.ref('account.view_move_form')
            tree_view = self.env.ref('account.view_invoice_tree')
            value = {
                'domain': str([('id', '=', self.invoice_id.id)]),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                'view_id': False,
                'views': [(form_view and form_view.id or False, 'form'),
                          (tree_view and tree_view.id or False, 'tree')],
                'type': 'ir.actions.act_window',
                'res_id': self.invoice_id.id,
                'target': 'current',
                'nodestroy': True
            }
        return value


class OpStudent(models.Model):
    _inherit = 'op.student'


    fill_application = fields.Boolean('Fill Application')
    marital_status = fields.Selection([('single', 'Single'),
                                       ('married', 'Married')])
    constrains = fields.Text('Special Wishes')
    khmer_name = fields.Char('Name in Khmer')
    medical_history_ids = fields.One2many('pm.employee.medical',
                                          inverse_name="student_id")
    student_semester_detail = fields.One2many('pm.student.semester.detail',
                                              inverse_name='student_id',
                                              string='Semester Details')
    class_id = fields.Many2one('op.classroom', 'Class', related="course_detail_ids.class_id", store=True)
    student_app_id = fields.Char('Student ID', readonly=False, tracking=True, track_visibility='onchange')
    primary_language = fields.Many2one('pm.student.language', string='Native Language')
    other_language = fields.Many2many('pm.student.language', string='Other languages', help="Other languages")
    english_score = fields.Float('English Score (%)')
    high_school_id = fields.Many2one('pm.high_school', 'High School')
    highest_education = fields.Selection([('HS', 'High School'),
                                          ('BA', 'Bachelor Degree'),
                                          ('MA', 'Master Degree'),
                                          ('PHD', 'Doctoral Degree')])
    prev_institute_id = fields.Char('Previous Institute')
    prev_course_id = fields.Char('Previous Course')
    prev_result = fields.Char('Previous Result')
    working_experience = fields.Text('Working Experience')
    job_position = fields.Text('Job Position')

    current_address = fields.Char('Current Address')
    hobby = fields.Char('Hobby')
    family_size = fields.Integer('Family Size')
    family_business = fields.Char('Family Business')
    family_status = fields.Selection([('p', 'Poor'),
                                      ('n', 'Normal'),
                                      ('r', 'Rich')])

    passport_number = fields.Char('Passport Number')
    id_card = fields.Char('ID Card')
    medical_checkup = fields.Boolean('Medical Check up', default=True)
    motivational_letter = fields.Boolean('Motivational Letter')
    special_medical = fields.Text('Special Medical Condition')
    emergency_number = fields.Char("Emergency Number")
    is_scholarship = fields.Boolean('Scholarship')
    scholarship_status = fields.Many2one('pm.scholarship.status', string='Scholarship Status')
    is_received_uniform = fields.Boolean('Uniform')
    is_received_shoe = fields.Boolean('Shoes')
    is_received_materiel = fields.Boolean('Study Material')
    is_received_locker = fields.Boolean('Locker')
    locker_number = fields.Char('Locker Number')

    enroll_reason_id = fields.Many2one('pm.enroll_reason', string='Reason to Enroll')
    not_enroll_reason_id = fields.Many2one('pm.not_enroll_reason', string='Reason not to Enroll')
    campaign_id = fields.Many2one('utm.campaign', 'Campaign')
    source_id = fields.Many2one('utm.source', 'Source')
    referred = fields.Char('Referred By')
    education_status = fields.Selection([('active', 'Active'),
                                         ('postponed', 'Postponed'),
                                         ('withdrawn', 'Withdrawn'),
                                         ('graduated', 'Graduated'),
                                         ('dismissed', 'Dismissed')
                                         ], default='active', compute='_compute_student_status', store=True)
    p_street = fields.Char('Permanent Street')
    p_street2 = fields.Char('Permanent Street2')
    p_city = fields.Char('Permanent City', size=64)
    p_zip = fields.Char('Permanent Zip', size=8)
    p_state_id = fields.Many2one(
        'res.country.state', 'Permanent State')
    p_country_id = fields.Many2one(
        'res.country', 'Permanent Country')
    batch_id = fields.Integer()

    _sql_constraints = [
        ('unique_student_app_id',
         'unique(student_app_id)', 'Student ID must be unique')]
    parents = fields.Char('Parents')
    siblings = fields.Integer('Siblings')
    other_depends = fields.Char('Other Dependents')
    family_income = fields.Char('Source of Family income')
    lead_participation = fields.One2many('pm.lead.participation',
                                         inverse_name='student_id',
                                         string='Participation',
                                         help="Participation")
    additional_source = fields.Char('Additional Source Info')
    lead_source = fields.Selection([('social_media', 'Social media'),
                                    ('facebook', 'Facebook'),
                                    ('website', 'Website'),
                                    ('school_visit', 'School Visit'),
                                    ('acac_student', 'By ACAC student'),
                                    ('friend', 'Friend'),
                                    ('school_councelor', 'School councelor'),
                                    ('family', 'Family'),
                                    ('open_day', 'Open day'),
                                    ('fair_exhibition', 'Fair/exhibition'),
                                    ('nea', 'NEA'),
                                    ('other', 'other')])
    chef_uniform = fields.Boolean('Chef’s Uniform	3 sets')
    shoes = fields.Boolean('Shoes')
    knife = fields.Boolean('Knife_set')
    study_material = fields.Boolean('Study Material')
    n_locker_key_s1 = fields.Integer('S1 Locker Key No.')
    n_locker_key_s4 = fields.Integer('S4 Locker Key No.')
    s1_returned = fields.Boolean('S1 Returned')
    s4_returned = fields.Boolean('S4 Returned')
    schooling_year = fields.Char('No. Schooling years')
    lead_educational_achievement = fields.One2many('pm.lead.educational.achievement',
                                                   inverse_name="student_id",
                                                   string='Educational Achievements',
                                                   help="Educational Achievements")
    lead_working_experience = fields.One2many('pm.lead.working.experience',
                                              inverse_name="student_id",
                                              string='Working Experience',
                                              help="Working Experience")
    shoe_size = fields.Selection([
        ('xxs', 'XXS'),
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'Xl'),
        ('xxl', 'XXL'),
    ], 'Shoe Size')
    uniform_size = fields.Selection([
        ('xxs', 'XXS'),
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'Xl'),
        ('xxl', 'XXL'),
    ], 'Uniform Size')
    rank = fields.Selection([('first_contact', 'First Contact'),
                             ('potential', 'Potential'),
                             ('high_potential', 'High Potential')])
    status_detail = fields.Char('Status detail')
    application_form = fields.Boolean('Application Form')
    pictures = fields.Boolean('Pictures')
    # contact_name = fields.Char('Contact Name', tracking=30)
    contact_name = fields.Many2one('res.partner', string='Emergency Contact')
    email_from = fields.Char('Email', help="Email address of the contact", tracking=40, index=True)
    # user_id = fields.Many2one('res.users', index=True, tracking=True,
    #                           default=lambda self: self.env.user)
    user_id = fields.Many2one('res.users', index=True, tracking=True)
    scholar_application = fields.Boolean('Scholar Application')
    financial_status = fields.Boolean('Proof of Financial Status')
    application_fee = fields.Boolean('Application Fee')
    acac_contact = fields.Char('ACAC Contact')
    semester_discipline = fields.One2many(
         'pm.student.discipline', inverse_name='student_id', string='Semester Discipline(s)')
    semester_result = fields.One2many(
         'pm.semester.result', inverse_name='student_id', string='Semester Result(s)', domain=[('semester_mark_sheet_id.state', '=', 'validated')])
    term_result_id = fields.Many2one('pm.term.result', 'Term Result')
    semester_attendance = fields.One2many(
         'pm.semester.attendance', inverse_name='student_id', string= 'Semester Attendance(s)')
    birth_place = fields.Many2one('res.country.state', 'Birth Place')
    student_passcode = fields.Char('Student Passcode')
    facebook = fields.Char('Facebook')
    phone = fields.Char('Mobile 1')
    # current_semester = fields.Integer('Current Semester')
    current_semester = fields.Selection([('1', '1'),
                                         ('2', '2'),
                                         ('3', '3'),
                                         ('4', '4')
                                         ], string='Current Semester')
    count_internship = fields.Integer(compute='_compute_internship', store=True)
    batch_name = fields.Char(compute='_compute_batch', store=True)
    visa_number = fields.Char('Visa Number')
    visa_expiry = fields.Date('Expiry Date')

    pin = fields.Char(string="PIN", compute='_compute_pin',
                      help="PIN used to Sign In in Kiosk Mode", copy=False, store=True)
    test = fields.Char('Mobile 2', compute='_on_change_course_id')

    active_class = fields.Many2many('op.classroom', string="class", compute='_compute_active_class', store=True)
    active_semester = fields.Many2one('pm.semester', string="Current Semester", compute='_compute_active_semester',
                                      store=True)

    qr_code = fields.Binary("QR Code", attachment=True, store=True, compute="generate_qr_code")
    vcard_string = fields.Char("V Card Text")

    def generateCardInfo(self, first_name, last_name, phone, email, company_name, title, work_address):
        value = """BEGIN:VCARD
N:%s;%s;
TEL;TYPE=work,VOICE:%s
EMAIL:%s
ORG:%s
TITLE:%s
ADR;TYPE=MOBILE,PREF:%s
URL: https://acac.edu.kh/
VERSION:3.0
END:VCARD""" % (first_name, last_name, phone, email, company_name, title, work_address)
        return value

    @api.depends('name', 'mobile', 'email')
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        address = str(self.street) + ', ' + str(self.street2) + ', ' + str(self.city) + ', ' + str(self.state_id.name) + ', ' + \
                  str(self.country_id.name)
        vcard_string = self.generateCardInfo(self.first_name, self.last_name, self.mobile, self.email,
                                             self.company_id.name, self.title.name, address)
        print(vcard_string)
        qr.add_data(vcard_string)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_code = qr_image
        self.vcard_string = vcard_string

    def bulkGenerateQRCode(self):
        print("Yes!")
        students = self.env['op.student'].search([])
        for student in students:
            if not student.qr_code:
                student.generate_qr_code()

    @api.depends('course_detail_ids')
    def _compute_active_class(self):
        for student in self:
            student_course = self.env['op.student.course'].search([
                ('student_id', '=', student.id), ('p_active', '=', 'True')
            ], limit=1)
            print("WOFF")
            print(student_course.class_ids)
            print(student_course.class_ids.ids)
            print(student_course.class_ids.id)
            student.active_class = student_course.class_ids.ids


    @api.depends('student_semester_detail')
    def _compute_active_semester(self):
        for student in self:
            details = student.student_semester_detail
            for detail in details:
                if detail.state == 'ongoing':
                    student.active_semester = detail.semester_id.id


    def batch_generate_payment_reports(self):
        students = self.env['op.student'].search([])
        for student in students:
            student_invoices = self.env['account.move'].search([('partner_id', '=', student.partner_id.id)])
            if student_invoices:
                student.generate_student_payment()

    def generate_student_payment(self):
        for student in self:
            print("YO")
            fee_obj = self.env['pm.student.fee']
            fee_line_obj = self.env['pm.student.fee.line']
            paid = {}
            invoiced = {}
            month = 8
            month_name = calendar.month_abbr[month]
            get_month = self.get_months(month)
            start_month = get_month['start_month']
            end_month = get_month['end_month']
            for month_idx in range(1, 13):
                print(calendar.month_abbr[month_idx])
                paid[calendar.month_abbr[month_idx]] = []
                invoiced[calendar.month_abbr[month_idx]] = []

            student_invoices = self.env['account.move'].search([('partner_id', '=', student.partner_id.id)])

            for inv in student_invoices:
                month = inv.create_date.month
                created_month = calendar.month_abbr[month]
                # inv_lines = inv.invoice_line_ids
                inv_lines = self.env['account.move.line'].search([('move_id', '=', inv.id), ('product_id', '!=', False)])
                payment_state = inv.payment_state
                pay_date = False;
                print("*********name**********'")
                print(inv.name)
                print("*********Lines**********'")
                print(inv_lines)
                if payment_state == 'paid':
                    for partial, amount, counterpart_line in inv._get_reconciled_invoices_partials():
                        pay_date = counterpart_line.date
                        print(pay_date)
                for line in inv_lines:
                    student_fee = fee_obj.search([('student_id', '=', student.id),
                                                 ('product_id', '=', line.product_id.id)])
                    print(inv.name)
                    if not student_fee:
                        print("***************")
                        print(line.product_id.name)
                        print(line.product_id.id)
                        student_fee = fee_obj.create({
                            'student_id': student.id,
                            'product_id': line.product_id.id
                        })

                    existing_fee_lines = fee_line_obj.search([('student_fee_id', '=', student_fee.id),
                                                              ('invoice_id', '=', inv.id)])
                    if existing_fee_lines:
                        existing_fee_lines.unlink()

                    val = {
                        'invoice_id': inv.id,
                        'invoice_line_id': line.id,
                        'student_fee_id': student_fee.id,
                        'amount': line.price_unit,
                        'date': inv.invoice_date,
                        'month': created_month,
                        'status': 'invoiced'
                    }
                    fee_line_obj.create(val)
                    if payment_state == 'paid':
                        paid_month = calendar.month_abbr[pay_date.month]
                        val = {
                            'invoice_id': inv.id,
                            'invoice_line_id': line.id,
                            'student_fee_id': student_fee.id,
                            'amount': line.price_unit,
                            'date': pay_date,
                            'month': paid_month,
                            'status': 'paid'
                        }
                        fee_line_obj.create(val)



    def get_months(self, month):
        start_month = int
        end_month = int
        if 1 <= month <= 6:
            start_month = 1
            end_month = 6
        elif 7 <= month <= 12:
            start_month = 7
            end_month = 12

        return {'start_month':start_month, 'end_month':end_month}

    def generate_student_payment(self):
        for student in self:
            print("YO")
            fee_obj = self.env['pm.student.fee']
            fee_line_obj = self.env['pm.student.fee.line']
            paid = {}
            invoiced = {}
            month = 8
            month_name = calendar.month_abbr[month]
            get_month = self.get_months(month)
            start_month = get_month['start_month']
            end_month = get_month['end_month']
            for month_idx in range(1, 13):
                print(calendar.month_abbr[month_idx])
                paid[calendar.month_abbr[month_idx]] = []
                invoiced[calendar.month_abbr[month_idx]] = []

            student_invoices = self.env['account.move'].search([('partner_id', '=', student.partner_id.id)])

            for inv in student_invoices:
                month = inv.create_date.month
                created_month = calendar.month_abbr[month]
                # inv_lines = inv.invoice_line_ids
                inv_lines = self.env['account.move.line'].search([('move_id', '=', inv.id), ('product_id', '!=', False)])
                payment_state = inv.payment_state
                pay_date = False;
                print("*********name**********'")
                print(inv.name)
                print("*********Lines**********'")
                print(inv_lines)
                if payment_state == 'paid':
                    for partial, amount, counterpart_line in inv._get_reconciled_invoices_partials():
                        pay_date = counterpart_line.date
                        print(pay_date)
                for line in inv_lines:
                    student_fee = fee_obj.search([('student_id', '=', student.id),
                                                 ('product_id', '=', line.product_id.id)])
                    print(inv.name)
                    if not student_fee:
                        print("***************")
                        print(line.product_id.name)
                        print(line.product_id.id)
                        student_fee = fee_obj.create({
                            'student_id': student.id,
                            'product_id': line.product_id.id
                        })

                    existing_fee_lines = fee_line_obj.search([('student_fee_id', '=', student_fee.id),
                                                              ('invoice_id', '=', inv.id)])
                    if existing_fee_lines:
                        existing_fee_lines.unlink()

                    val = {
                        'invoice_id': inv.id,
                        'invoice_line_id': line.id,
                        'student_fee_id': student_fee.id,
                        'amount': line.price_unit,
                        'date': inv.invoice_date,
                        'month': created_month,
                        'status': 'invoiced'
                    }
                    fee_line_obj.create(val)
                    if payment_state == 'paid':
                        paid_month = calendar.month_abbr[pay_date.month]
                        val = {
                            'invoice_id': inv.id,
                            'invoice_line_id': line.id,
                            'student_fee_id': student_fee.id,
                            'amount': line.price_unit,
                            'date': pay_date,
                            'month': paid_month,
                            'status': 'paid'
                        }
                        fee_line_obj.create(val)



    def get_months(self, month):
        start_month = int
        end_month = int
        if 1 <= month <= 6:
            start_month = 1
            end_month = 6
        elif 7 <= month <= 12:
            start_month = 7
            end_month = 12

        return {'start_month':start_month, 'end_month':end_month}


    def get_result(self):
        action = self.env.ref("pm_general.act_open_student_pm_term_result_view").read()[0]
        res = self.term_result_id
        action["views"] = [(self.env.ref("pm_general.view_pm_term_result_form").id, "form")]
        action["res_id"] = res.id
        return action

    def action_view_purchase_order(self):
        action = self.env.ref("purchase.purchase_form_action").read()[0]
        lines = self.env['purchase.order'].search([('request_id', '=', self.id),
                                                   ('state', '=', 'done')])
        print(lines)
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = lines.id
        return action


    def get_progression(self):
        action = self.env.ref("pm_students.act_open_student_pm_student_progression_view").read()[0]
        lines = self.env['pm.student.progress'].search([('student_id', '=', self.id)])
        action["domain"] = [("id", "in", lines.ids)]
        return action

    def disable_student_payment(self):
        print("HIT DISBALE")
        for student in self:
            fees = student.fees_detail_ids
            print(fees)
            for fee in fees:
                if fee.state == 'draft' or not fee.invoice_id:
                    fee.payable = False

    def enable_student_payment(self):
        print("Triger Enable")
        for student in self:
            fees = student.fees_detail_ids
            for fee in fees:
                fee.payable = True

    # @api.depends('course_detail_ids')
    # def _compute_active_class(self):
    #     for student in self:
    #         student_course = self.env['op.student.course'].search([
    #             ('student_id', '=', student.id), ('p_active', '=', 'True')
    #         ], limit=1)
    #         student.active_class = student_course.class_id.id

    @api.depends('course_detail_ids.education_status')
    def _compute_student_status(self):
        for student in self:
            student_course = student.course_detail_ids
            if student_course:
                for course in student_course:
                    if course.p_active:
                        if course.education_status != 'active':
                            student.education_status = course.education_status
                            self.disable_student_payment()
                        else:
                            student.education_status = 'active'








    @api.constrains('birth_date')
    def _compute_pin(self):
        for record in self:
            if record.birth_date:
                birth_date = str(record.birth_date.day).zfill(2)
                birth_month = str(record.birth_date.month).zfill(2)
                pin = birth_date + birth_month
                record.pin = pin

    def _compute_batch(self):
        for record in self:
            if record.batch_id:
                record.batch_name = self.env['op.batch'].search(
                    [('id', '=', record.batch_id)])[0].name

    def _compute_internship(self):
        for record in self:
            record.count_internship = self.env['op.placement.offer'].search_count(
                [('student_id', '=', record.id)])


    def get_student_id(self,course_id, batch_id, code):
        course = self.env['op.course'].browse(course_id)
        batch = self.env['op.batch'].browse(batch_id)
        count = self.env['op.student'].search_count(
            [('course_detail_ids.batch_id', 'in', [batch.id]),
             '|', ('active', '=' ,True),  ('active', '=', False)])
        #count need add 1 to avoid student start from 0
        count += 1
        course_code = course.code
        year = batch.start_date.year
        short_year = str(year)[-2:]
        year_term = batch.year_term.name
        app_number = str(count).zfill(3)
        if code:
            app_number = str(code) + str(count).zfill(2)
        return str(short_year) + str(year_term) + str(course_code) + app_number


    def get_subjects_for_students(self, course_id, batch_id, student_id):
        print("********************&&&&&&&&&&&&&&&&&&&&")
        subject_registration = self.env['op.subject.registration'].create({
            'course_id': course_id,
            'batch_id': batch_id,
            'student_id': student_id,
        })

        # Register Subject For Student!!
        subject_registration.get_subjects()
        subject_registration.action_approve()
    def get_student_starting_data(self, course_id, batch_id, student_id):

        self.get_subjects_for_students(course_id, batch_id, student_id)
        student = self.env['op.student'].browse(self.id)
        batch = self.env['op.batch'].browse(batch_id)
        discipline_data = []
        semester_detail_data = []
        semesters = batch.semester_ids
        for semester in semesters:
            state = ''
            if semester.state == 'active':
                state = 'ongoing'
            else:
                state = 'incomplete'
            discipline_data.append({'student_id': student_id, 'semester_id': semester.id})
            semester_detail_data.append(
                {'student_id': student_id,
                 'semester_id': semester.id,
                 'state': state,
                 'batch_id': batch_id,
                 'course_id': course_id})


        #Generate Discipline
        print('=======Discipline==========')
        print(discipline_data)
        print('=======semester_detail_data==========')
        print(semester_detail_data)
        student.env['pm.student.discipline'].create(discipline_data)
        student.env['pm.student.semester.detail'].create(semester_detail_data)




    @api.model
    def create(self, val):
        print("GEGE")
        print(val)
        course_id = 0
        batch_id = 0
        class_id = 0
        res = 0
        if "course_detail_ids" in val:
            batch_id = val['course_detail_ids'][0][2]['batch_id']
            course_id = val['course_detail_ids'][0][2]['course_id']
            class_id = val['course_detail_ids'][0][2]['class_ids']
        elif "batch_id" in val:
            batch_id = val['batch_id']
            course_id = val['course_id']
            class_id = val['class_ids']
        if course_id or batch_id:
            is_scholarship = val.get('is_scholarship')
            status = val.get('scholarship_status')
            print("**********Status")
            print(status)
            student_app_id = 0
            if is_scholarship and status:
                code = 3
                status_object = self.env['pm.scholarship.status'].browse(status)
                if status_object.percentage != 100:
                    code = 2
                print("code is", code)
                student_app_id = self.get_student_id(course_id, batch_id, code)
            else:
                student_app_id = self.get_student_id(course_id, batch_id, False)
            val['student_app_id'] = student_app_id
            val['batch_id'] = batch_id
            print(val)
            res = super(OpStudent, self).create(val)

            # Store Student Progression detail in this case, the student have been enrolled
            progress_obj = self.env['pm.student.progress'].sudo()
            progress_obj.store_progression(res.id, course_id, batch_id , 'active')

            print('res', res)
            print('res.id', res.id)

            self.get_student_starting_data(course_id, batch_id, res.id)

        return res
    def write(self, val):
        print("here")
        print(val)
        res = super(OpStudent, self).write(val)
        if "course_detail_ids" in val:
            for course_detail_id in val['course_detail_ids']:
                course_id = course_detail_id[1]
                if course_id:
                    student_course = self.env['op.student.course'].browse(course_id)
                    student_id = student_course.student_id.id
                    remarks = student_course.remarks
                    status = student_course.education_status
                    batch_id = student_course.batch_id.id
                    course_id = student_course.course_id.id


                    # Store Student Progression detail in this case, the student status must have been changed
                    progress_obj = self.env['pm.student.progress'].sudo()
                    progress_obj.store_progression(student_id, course_id, batch_id, status, remarks)

        return res

class PmStudentFeesDetails(models.Model):
    _inherit = "op.student.fees.details"
    date = fields.Date('Payment Date')
    remarks = fields.Text("Remarks")
    state = fields.Selection(selection_add=[('installment', 'Installment Generated')])
    semester = fields.Selection([("basic", "Basic"),
                                 ("internship1", "Internship 1"),
                                 ("advance", "Advance"),
                                 ("internship2", "Internship 2")])
    alert_date = fields.Date('Alert Date')
    payable = fields.Boolean(default=True)
    installments = fields.One2many(comodel_name='pm.student.installment', inverse_name="fee_id")
    payment_option = fields.Selection([('normal', 'Normal'),
                                       ('exempted', 'Exempted'),
                                       ('installment', 'Installment')], default='normal')

    def _cron_create_invoice(self):
        d = timedelta(days=10)
        date = datetime.today() - d
        fees_ids = self.env['op.student.fees.details'].search(
            [('date', '=', date), ('invoice_id', '=', False), ('payable', '=', True)])
        print(fees_ids)
        ir_model_data = self.env['ir.model.data']
        for fees in fees_ids:
            fees.get_invoice()

    def _cron_payment_reminder(self):
        today = datetime.today()
        one_week_before = today - timedelta(days=7)
        one_week_late = today + timedelta(days=7)

        reminder_fee = self.env['op.student.fees.details'].search(
            [('date', '=', one_week_before), ('invoice_id', '!=', False),
             ('invoice_state', '!=', 'posted'), ('payable', '=', True)])

        over_due_fee = self.env['op.student.fees.details'].search(
            [('date', '=', one_week_late), ('invoice_id', '!=', False),
             ('invoice_state', '!=', 'posted'), ('payable', '=', True)])

        print(over_due_fee)
        print(reminder_fee)

        ir_model_data = self.env['ir.model.data']

        for late in over_due_fee:
            try:
                template_id = ir_model_data.get_object_reference('pm_admission', 'payment_overdue_template')[1]
            except ValueError:
                template_id = False
            self.env['mail.template'].browse(template_id).send_mail(late.id, force_send=True)

        for remind in reminder_fee:
            try:
                template_id = ir_model_data.get_object_reference('pm_admission', 'payment_reminder_template')[1]
            except ValueError:
                template_id = False
            self.env['mail.template'].browse(template_id).send_mail(remind.id, force_send=True)

    def get_default_tuition_fee(self):
        # 168168 is manually set
        product = self.env['product.product'].search(['default_code', '=', '168@168'],
                                                     order='semester_order asc',
                                                     limit=1)
        return product.id

    def get_invoice(self):
        """ Create invoice for fee payment process of student """
        inv_obj = self.env['account.move'].with_context(check_move_validity=False)
        partner_id = self.student_id.partner_id
        MoveLine = self.env['account.move.line'].with_context(check_move_validity=False)
        student = self.student_id
        account_id = False
        product = self.product_id
        notification_obj = self.env['pm.menu.notification']
        notification_obj.update_notification('payment_schedule', student.id)

        if product.property_account_income_id:
            account_id = product.property_account_income_id.id
        if not account_id:
            account_id = product.categ_id.property_account_income_categ_id.id
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s".'
                  'You may have to install a chart of account from Accounting'
                  ' app, settings menu.') % product.name)

        if self.amount <= 0.00:
            raise UserError(
                _('The value of the deposit amount must be positive.'))
        else:
            amount = self.amount
            name = product.name

        element_id = self.env['op.fees.element'].search([
            ('fees_terms_line_id', '=', self.fees_line_id.id)])
        invoice_lines = []
        if self.payment_option == "installment":
            invoice = inv_obj.create({
                'move_type': 'out_invoice',
                'partner_id': partner_id.id,
                'invoice_date': self.date,
            })
            tuition_fee = self.env['op.fees.element'].search([
                ('fees_terms_line_id', '=', self.fees_line_id.id)], order="price desc", limit=1)

            installments = self.env['pm.student.installment'].search([('fee_id', '=', self.id)], order="due_date asc")
            print("yoo")
            print(installments)
            if not installments:
                raise UserError(
                    _('There is no installment for this semester: "%s".') % self.semester)

            for records in element_id:
                if records.id != tuition_fee.id:
                    line_values = {'name': records.product_id.name,
                                   'account_id': records.product_id.property_account_income_id.id,
                                   'price_unit': records.price,
                                   'quantity': 1.0,
                                   'move_id': invoice.id,
                                   'product_uom_id': records.product_id.uom_id.id,
                                   'product_id': records.product_id.id, }
                    invoice_lines.append(line_values)

            first_installment = True
            if len(element_id) <= 1:
                first_installment = False

            for installment in installments:
                if first_installment:
                    line_values = {'name': tuition_fee.product_id.name,
                                   'account_id': tuition_fee.product_id.property_account_income_id.id,
                                   'price_unit': installment.amount,
                                   'quantity': 1.0,
                                   'move_id': invoice.id,
                                   'product_uom_id': tuition_fee.product_id.uom_id.id,
                                   'product_id': tuition_fee.product_id.id}
                    invoice_lines.insert(0, line_values)
                    print(invoice_lines)
                    MoveLine.create(invoice_lines)
                    invoice.write({
                        'invoice_date_due': installment.due_date,
                        'invoice_date': self.date,
                    })
                    installment.write({
                        'invoice_id': invoice.id,
                        'amount': invoice.amount_total,
                        'state': 'invoice'
                    })
                    invoice._compute_invoice_taxes_by_group()
                    invoice._move_autocomplete_invoice_lines_values()

                    first_installment = False
                else:
                    print("yo")
                    split_invoice = inv_obj.create({
                        'move_type': 'out_invoice',
                        'partner_id': partner_id.id,
                        'invoice_date': self.date,
                        'invoice_date_due': installment.due_date,
                    })
                    line_values = {'name': tuition_fee.product_id.name,
                                   'account_id': tuition_fee.product_id.property_account_income_id.id,
                                   'price_unit': installment.amount,
                                   'quantity': 1.0,
                                   'move_id': split_invoice.id,
                                   'product_uom_id': tuition_fee.product_id.uom_id.id,
                                   'product_id': tuition_fee.product_id.id}
                    MoveLine.create(line_values)
                    installment.write({'invoice_id': split_invoice.id, 'state': 'invoice'})
                    split_invoice._compute_invoice_taxes_by_group()
                    split_invoice._move_autocomplete_invoice_lines_values()
            self.state = 'installment'
            return True

        elif self.payment_option == "normal":
            invoice = inv_obj.create({
                'move_type': 'out_invoice',
                'partner_id': partner_id.id,
                'invoice_date': self.date,
            })
            for records in element_id:
                print(records.product_id.name, records.price)
                if records:
                    line_values = {'name': records.product_id.name,
                                   'account_id': records.product_id.property_account_income_id.id,
                                   'price_unit': records.price,
                                   'quantity': 1.0,
                                   'move_id': invoice.id,
                                   'product_uom_id': records.product_id.uom_id.id,
                                   'product_id': records.product_id.id, }
                    invoice_lines.append(line_values)
            if not element_id:
                line_values = {'name': name,
                               # 'origin': student.gr_no,
                               'account_id': account_id,
                               'price_unit': amount,
                               'quantity': 1.0,
                               'discount': 0.0,
                               'product_uom_id': product.uom_id.id,
                               'product_id': product.id}
            print(invoice_lines)
            MoveLine.create(invoice_lines)
            invoice._compute_invoice_taxes_by_group()
            invoice._move_autocomplete_invoice_lines_values()
            self.state = 'invoice'
            self.invoice_id = invoice.id
            return True

































