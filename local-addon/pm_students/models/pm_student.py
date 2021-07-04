# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


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
                                batch_id=False, class_id=False, status=False, remarks=False):
        progress_obj = self.env['pm.student.progress'].sudo()
        val = {
            'student_id': student_id,
            'date': datetime.today(),
            'remarks': remarks,
            'education_status': status,
            'course_id': course_id,
            'batch_id': batch_id,
            'class_id': class_id,
        }
        progress_obj.create(val)






class OpStudentCourse(models.Model):
    _inherit = 'op.student.course'
    p_active = fields.Boolean('Active', default=True)
    class_id = fields.Many2one('op.classroom', 'Class')
    education_status = fields.Selection([('active', 'Active'),
                                         ('postponed', 'Postponed'),
                                         ('withdrawn', 'Withdrawn'),
                                         ('graduated', 'Graduated'),
                                         ('dismissed', 'Dismissed')
                                         ], 'Status', default='active')

    p_e_subject_ids = fields.Many2many('op.subject', relation='student_e_subjects_rel', readonly=False, string='Exempted Subjects')
    is_saved = fields.Boolean(default=False)
    cancel_date = fields.Date(default=lambda self: fields.Datetime.now())
    remarks = fields.Text("Remarks")
    return_date = fields.Date("Returning Date")
    reminding_date = fields.Date(compute="_compute_remind_date", store=True)
    is_reminded = fields.Boolean()
    starting_semester_id = fields.Many2one('pm.semester', 'Starting Semester')


    @api.depends('return_date')
    def _compute_remind_date(self):
        for course in self:
            if course.return_date:
                return_date = course.return_date
                d = timedelta(days=3)
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


class OpStudent(models.Model):
    _inherit = 'op.student'
    fill_application = fields.Boolean('Fill Application')
    marital_status = fields.Selection([('single', 'Single'),
                                       ('married', 'Married')])
    constrains = fields.Text('Special Wishes')
    khmer_name = fields.Char('Name in Khmer')
    # tem:
    # medical_history_ids = fields.One2many('pm.employee.medical',
    #                                       inverse_name="student_id")
    student_semester_detail = fields.One2many('pm.student.semester.detail',
                                              inverse_name='student_id',
                                              string='Detail(s)')
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
    active_class = fields.Many2one('op.classroom', compute='_compute_active_class', store=True)

    def student_reminder_scheduler(self):
        print("Hit Function")
        all_course_search = self.env['op.student.course'].sudo().search(
            [('education_status', '=', 'postponed'),
             ('is_reminded', '=', False),
             ('return_date', '!=', None)])

        print(all_course_search)

        for course in all_course_search:
            today = datetime.date.today()
            print('today', today)
            if today == course.return_date or today == course.reminding_date:
                student = course.student_id
                ir_model_data = self.env['ir.model.data']
                try:
                    template_id = ir_model_data.get_object_reference('pm_leads', 'student_follow_up_reminder')[1]
                except ValueError:
                    template_id = False
                self.env['mail.template'].browse(template_id).send_mail(student.id, force_send=True)
                if today == course.return_date:
                    print('TODAY!!')
                    course.is_reminded = True


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

    @api.depends('course_detail_ids')
    def _compute_active_class(self):
        for student in self:
            student_course = self.env['op.student.course'].search([
                ('student_id', '=', student.id), ('p_active', '=', 'True')
            ], limit=1)
            student.active_class = student_course.class_id.id

    @api.depends('course_detail_ids.education_status')
    def _compute_student_status(self):
        print("Trigger!!!")
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
            class_id = val['course_detail_ids'][0][2]['class_id']
        elif "batch_id" in val:
            batch_id = val['batch_id']
            course_id = val['course_id']
            class_id = val['class_id']
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
            res = super(OpStudent, self).create(val)

            # Store Student Progression detail in this case, the student have been enrolled
            progress_obj = self.env['pm.student.progress'].sudo()
            progress_obj.store_progression(res.id, course_id, batch_id, class_id, 'active')

            self.get_student_starting_data(course_id, batch_id, res.id)

        return res
    def write(self, val):
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
                    class_id = student_course.class_id.id

                    # Store Student Progression detail in this case, the student status must have been changed
                    progress_obj = self.env['pm.student.progress'].sudo()
                    progress_obj.store_progression(student_id, course_id, batch_id, class_id, status, remarks)

        return res

































