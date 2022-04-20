from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.http import request
from datetime import datetime, timedelta


class OpStudentCourse(models.Model):
    _inherit = 'op.student.course'
    class_ids = fields.Many2many('op.classroom')



class OpTermMarksheetRegister(models.Model):
    _name = "pm.term.marksheet.register"
    _order = "id desc"
    _inherit = ["mail.thread"]
    _description = "Terms Marksheet"

    batch_id = fields.Many2one(
        'op.batch', 'Term', required=True, index=True)
    term_result_ids = fields.One2many(
        comodel_name="pm.term.result",
        inverse_name="term_marksheet_register_id")
    generated_date = fields.Date(
        'Generated Date', required=True,
        default=fields.Date.today(), track_visibility='onchange')
    generated_by = fields.Many2one(
        'res.users', 'Generated By',
        default=lambda self: self.env.uid,
        required=True, track_visibility='onchange')
    state = fields.Selection(
        [('draft', 'Draft'), ('validated', 'Validated'),
         ('cancelled', 'Cancelled')], 'Status',
        default="draft", required=True, track_visibility='onchange')
    total_pass = fields.Integer('Total Pass', compute='_compute_total_pass_fail',store=False)
    total_failed = fields.Integer('Total Fail', compute='_compute_total_pass_fail',store=False)
    name = fields.Char('Marksheet Register', size=256, required=True,
                       track_visibility='onchange')

    def _compute_total_pass_fail(self):
        print("FF")
        for record in self:
            passed = 0
            failed = 0
            for results in record.term_result_ids:
                if results.status == 'pass':
                    passed += 1
                elif results.status == 'fail':
                    failed += 1
            record.total_pass = passed
            record.total_failed = failed

    def action_validate(self):
        for res in self.term_result_ids:
            res.student_id.term_result_id = res.id

        self.state = 'validated'

    def action_draft(self):
        self.state = 'draft'

    def act_cancel(self):
        self.state = 'cancel'




class PmTermSemesterResult(models.Model):
    _name = "pm.term.result.associate"
    name = fields.Char()
    term_result_id = fields.Many2one('pm.term.result', 'Term Result')
    semester_id = fields.Many2one('pm.semester', 'Semester')
    status = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')
    ], 'Status', store=True)
    gpa = fields.Float('GPA', readonly=True, digits=(12, 1))
    color = fields.Integer(string='Color Index', default=0, compute="_compute_result_color")
    @api.depends('status')
    def _compute_result_color(self):
        for rec in self:
            if rec.status == 'pass':
                rec.color = 10
            elif rec.status == 'fail':
                rec.color = 9




class PmTernResult(models.Model):
    _name = "pm.term.result"
    name = fields.Char()
    semester_results = fields.Many2many('pm.semester.result')
    internship_result = fields.Many2many('op.placement.offer')
    term_marksheet_register_id = fields.Many2one("pm.term.marksheet.register", index=True)
    student_id = fields.Many2one('op.student', 'Student', required=True)
    batch_id = fields.Many2one(
        'op.batch', 'Term', required=True, index=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('validated', 'Validated'),
         ('cancelled', 'Cancelled')], 'Status',
        default="draft", required=True, track_visibility='onchange')
    status = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')
    ], 'Status', compute='_compute_status', store=True)
    gpa = fields.Float('GPA', readonly=True, digits=(12, 1))
    term_associated_ids = fields.One2many(
        comodel_name="pm.term.result.associate",
        inverse_name="term_result_id",
        string='Semester Result')

    @api.depends('semester_results', 'gpa')
    def _compute_status(self):
        for rec in self:
            semester_results = rec.term_associated_ids.mapped('status')
            print(semester_results)
            if 'fail' in semester_results or rec.gpa < 2:
                rec.status = 'fail'
            else:
                rec.status = 'pass'







class OpSubject(models.Model):
    _inherit = 'op.subject'
    grade_weightage = fields.Float('Grade Weightage', default=100)
    p_hours = fields.Float("Hours", default=None, required=True)
    p_credits = fields.Float("Credits", default=None, required=True)
    semester_id = fields.Many2one(
        'pm.semester', 'Semester',
        required=False)
    semester = fields.Selection([('1', '1'),
                                 ('2', '2'),
                                 ('3', '3'),
                                 ('4', '4')], 'Semester Order', required=True)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self.env.context.get('get_parent_subject', False):
            lst = []
            lst.append(self.env.context.get('semester_id'))
            semester = self.env['pm.semester'].search([('id', 'in', lst)])
            if semester:
                subject = semester.get_semester_subject()
                return subject.name_get()
            return False
        return super(OpSubject, self).name_search(
            name, args, operator=operator, limit=limit)

    def write(self, val):
        old_sem_order = self.semester
        old_course_id = self.course_id.id
        res = super(OpSubject, self).write(val)
        if 'p_credits' in val or 'course_id' in val or 'semester' in val:
            semester = self.env['pm.semester'].search([('course_id', '=', res.course_id.id),
                                                       ('semester_order', '=', res.semester)])
            if semester:
                semester.calculate_total_semester_credit()

            previous_semester = self.env['pm.semester'].search([('course_id', '=', old_course_id),
                                                        ('semester_order', '=', old_sem_order)])
            if previous_semester:
                previous_semester.calculate_total_semester_credit()

        return res

    @api.model
    def create(self, val):
        res = super(OpSubject, self).create(val)
        if 'p_credits' in val or 'course_id' in val or 'semester' in val:
            print('course:', res.course_id.id)
            print('order:', res.semester)
            semester = self.env['pm.semester'].search([('course_id', '=', res.course_id.id),
                                                       ('semester_order', '=', res.semester)])
            if semester:
                semester.calculate_total_semester_credit()
        return res

    def unlink(self):
        semester = self.env['pm.semester'].search([('course_id', '=', self.course_id.id),
                                                   ('semester_order', '=', self.semester)])
        res = super(OpSubject, self).unlink()
        if semester:
            semester.calculate_total_semester_credit()
        return res


class OpSubjectRegistrationCustom(models.Model):
    _inherit = "op.subject.registration"
    batch_id = fields.Many2one('op.batch', 'Term', required=True,
                               track_visibility='onchange')

    def action_approve(self):
        for record in self:
            subject_ids = []
            data = []

            for sub in record.elective_subject_ids:
                subject_ids.append(sub.id)
            course_id = self.env['op.student.course'].search([
                ('student_id', '=', record.student_id.id),
                ('batch_id', '=', record.batch_id.id),
                ('course_id', '=', record.course_id.id)
            ], limit=1)
            for sub in record.compulsory_subject_ids:
                val = {
                    'op_student_course_id': course_id.id,
                    'op_subject_id': sub.id,
                    'is_completed': False
                }
                data.append(val)
            print(course_id)
            if course_id:
                course_id.write({
                    'subject_ids': [[6, 0, list(set(subject_ids))]]
                })
                self.env['pm.student.course.subject'].create(data)
                record.state = 'approved'




# class PmTermOrder(models.Model):
#     _description = 'Terms Order'
#     _name = 'pm.term.order'
#     name = fields.Char('Term Order')
#     _sql_constraints = [
#         ('unique_name',
#          'unique(name)', 'Term Order must be unique')]

class OpBatch(models.Model):

    _inherit = "op.batch"
    _description = 'OpenEduCat Terms'


    # year_term = fields.Many2one('pm.term.order', string='Term Order')
    year_term = fields.Selection([("WI", "WI"),
                                 ("SP", "SP"),
                                 ("FA", "FA"),
                                 ("SU", "SU")], string='Term Order', required=True)
    semester_ids = fields.One2many('pm.semester', 'batch_id', 'Semester(s)')
    record_url = fields.Char('Link', compute="_compute_record_url", store=True)

    @api.depends('name')
    def _compute_record_url(self):
        for record in self:
            base_url = request.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=op.batch' % (record.id)
            record.record_url = base_url

    def batch_scheduler(self):
        all_terms = self.env['op.batch'].sudo().search(
            [('state', '=', 'active'),
             ('end_date', '!=', False)])
        today = fields.Date.today()
        for term in all_terms:
            d = timedelta(days=14)
            end_date = term.end_date
            remind_date = term.end_date - d


            if today == remind_date or today == end_date:
                print(term.name)
                ir_model_data = self.env['ir.model.data']
                try:
                    template_id = ir_model_data.get_object_reference('pm_general', 'term_ending_reminder')[1]
                    print(template_id)
                except ValueError:
                    template_id = False
                self.env['mail.template'].browse(template_id).send_mail(term.id, force_send=True)


    @api.constrains('course_id', 'year_term', 'start_date')
    def _check_term_order(self):
        all_batches = self.env['op.batch'].search([('course_id', '=', self.course_id.id)])
        print(all_batches)
        for batch in all_batches:
            if batch.id != self.id:
                year = batch.start_date.year
                order = batch.year_term
                if year == self.start_date.year and order == self.year_term:
                    msg = 'Term Order %s for %s has exist' % (
                        order,
                        year
                    )
                    raise ValidationError(msg)


    state = fields.Selection(
        [('pending', 'Pending'),
         ('active', 'Active'),
         ('finished', 'Finished')], 'Status',
        default="pending", required=True, track_visibility='onchange')

    active_count = fields.Integer(compute="_compute_batch_report_data", string='Active')
    postpone_count = fields.Integer(compute="_compute_batch_report_data", string='Postponed')
    withdrawn_count = fields.Integer(compute="_compute_batch_report_data", string='Withdrawn')
    dismissed_count = fields.Integer(compute="_compute_batch_report_data", string='Dismissed')
    graduated_count = fields.Integer(compute="_compute_batch_report_data", string='Graduated')
    student_count = fields.Integer(compute="_compute_batch_report_data", string='Student')
    semester_count = fields.Integer(compute="_compute_batch_report_data", string='Semester')
    active_semester_count = fields.Integer(compute="_compute_batch_report_data", string='Active')
    pending_semester_count = fields.Integer(compute="_compute_batch_report_data", string='Pending')
    finish_semester_count = fields.Integer(compute="_compute_batch_report_data", string='Finished')
    inactive_count = fields.Integer(compute="_compute_batch_report_data", string='Inactive')
    male_count = fields.Integer(compute="_compute_batch_report_data", string='Male')
    female_count = fields.Integer(compute="_compute_batch_report_data", string='Female')

    def action_draft(self):
        self.write({'state': 'pending'})


    def _compute_batch_report_data(self):
        for batch in self:
            studnet_list = self.env['op.student'].search(
                [('course_detail_ids.batch_id', 'in', [batch.id]),
                 ('course_detail_ids.p_active', 'in', [True])])

            #Count student genders by batch
            genders = studnet_list.mapped('gender')
            batch.male_count = genders.count('m')
            batch.female_count = genders.count('f')

            semesters = batch.semester_ids
            semester_state = semesters.mapped('state')
            status = []
            print('============Students============')
            print(studnet_list)
            for course in studnet_list.course_detail_ids:
                if course.batch_id.id == batch.id:
                    status.append(course.education_status)
            print('============Batch============')
            print(batch.name)
            print('============Status============')
            print(status)

            batch.student_count = len(studnet_list)
            batch.active_count = status.count('active')
            batch.postpone_count = status.count('postponed')
            batch.withdrawn_count = status.count('withdrawn')
            batch.dismissed_count = status.count('dismissed')
            batch.graduated_count = status.count('graduated')
            batch.semester_count = len(batch.semester_ids)
            batch.active_semester_count = semester_state.count('active')
            batch.pending_semester_count = semester_state.count('pending')
            batch.finish_semester_count = semester_state.count('finished')
            batch.inactive_count = status.count('postponed') + status.count('withdrawn') + status.count('dismissed') + status.count('graduated')

    def start_batch(self):
        for batch in self:
            semesters = batch.semester_ids
            if len(semesters) < 1:
                raise ValidationError('Please create semesters')
            semester_state = semesters.mapped('state')
            print(semester_state)
            if 'active' not in semester_state:
                fs = semesters.sorted(lambda r: r.semester_order, reverse = False)
                fs[0].state = 'active'
                #raise ValidationError('Please start the semester')
        self.write({'state': 'active'})

    def finish_batch(self):
        self.write({'state': 'finished'})


    # @api.constrains('state')
    # def validate_batch_active(self):
    #     print('hot constraint')
    #     for batch in self:
    #         course = batch.course_id
    #         semesters = batch.semester_ids
    #
    #         batch_list = self.env['op.batch'].search(
    #             [('course_id', 'in', [course.id])])
    #         states = batch_list.mapped('state')
    #         active_count = 0
    #         for state in states:
    #             if state == 'active':
    #                 active_count += 1
    #         print(active_count)
    #
    #         if active_count > 1:
    #             raise ValidationError('Multiple terms can not be active simultaneously')

    @api.onchange('course_id', 'start_date', 'year_term')
    def _onchange_code(self):
        self.code = ""
        if self.start_date:
            year = self.start_date.year
            short_year = str(year)[-2:]
            self.code += str(short_year or "")
        if self.year_term:
            year_term = self.year_term
            self.code += str(year_term or "")
        if self.course_id:
            course_code = self.course_id.code
            self.code += str(course_code or "")
            self.semester_ids.course_id = self.course_id
        for semester in self.semester_ids:
            semester.semester_code = self.code + semester.semester_code[-2:]

class OpFeesTermsLine(models.Model):
    _inherit = "op.fees.terms.line"
    product_id = fields.Many2one('product.product',
                                 'Product(s)',
                                 domain=[('type', '=', 'service')],
                                 required=True)
    total = fields.Float("Total", compute="_compute_fee_line_total")
    semester = fields.Selection([("basic", "Basic"),
                                 ("internship1", "Internship 1"),
                                 ("advance", "Advance"),
                                 ("internship2", "Internship 2"),
                                 ("basic_intern", "Basic + Internship 1"),
                                 ("advance_intern", "Advance + Internship 2")])

    @api.depends('fees_element_line')
    def _compute_fee_line_total(self):
        for fee_line in self:
            fee_element = fee_line.fees_element_line
            fee_element_prices = fee_element.mapped('price')
            print(fee_element_prices)
            fee_line.total = sum(fee_element_prices)

class OpFeesElementLineCustom(models.Model):
    _inherit = "op.fees.element"
    price = fields.Float('Price', related='product_id.lst_price', store=True)
    product_id = fields.Many2one('product.product',
                                 'Product(s)',
                                 domain=[('type', '=', 'service')],
                                 required=True)

class GenerateSession(models.TransientModel):
    _inherit = "generate.time.table"
    semester_id = fields.Many2one('pm.semester', 'Semester', required=True)




