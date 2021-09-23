
from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError


class OpClassroomCustom(models.Model):
    _inherit = "op.classroom"
    name = fields.Char('Name', size=255, required=True)
    batch_id = fields.Many2one('op.batch', 'Term')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self.env.context.get('get_parent_class', False):
            lst = []
            lst.append(self.env.context.get('batch_id'))
            print(lst)
            class_room = self.env['op.classroom'].search([('batch_id', 'in', lst)])
            return class_room.name_get()
        return super(OpClassroomCustom, self).name_search(
            name, args, operator=operator, limit=limit)

class PmExamClassSchedule(models.Model):
    _name = 'pm.class.exam'
    _inherit = "mail.thread"
    _description = "Class Exam"
    name = fields.Char('Name', size=256, required=True)
    class_id = fields.Many2one('op.classroom', 'Class')
    exam_session_id = fields.Many2one("op.exam.session", 'Exam Schedule')
    exam_id = fields.Many2one('op.exam', 'Exam',
                                 domain=[('state', 'not in',
                                          ['cancel', 'done'])])
    class_code = fields.Char('Class Code', size=16, required=False)
    semester_id = fields.Many2one('pm.semester', 'Semester', related='exam_session_id.semester_id', store=True)
    batch_id = fields.Many2one('op.batch', 'Term', related='semester_id.batch_id', store=True)
    subject_id = fields.Many2one('op.subject', 'Subject', related='exam_session_id.subject_id', store=True)
    attendees_line = fields.One2many(
        'op.exam.attendees', 'class_exam_id', 'Attendees')
    start_time = fields.Datetime('Start Time', required=True)
    end_time = fields.Datetime('End Time', required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('schedule', 'Scheduled'),
         ('submitted', 'Submitted'),
         ('cancel', 'Cancelled'), ('done', 'Done')], 'State',
        readonly=True, default='draft', track_visibility='onchange')
    note = fields.Text('Note')
    responsible_id = fields.Many2many('op.faculty', string='Responsible')
    active = fields.Boolean(default=True)
    faculty_id = fields.Many2one('op.faculty', 'Faculty', related='exam_session_id.faculty_id', store=True)
    absence_count = fields.Integer(compute="compute_attendance")
    present_count = fields.Integer(compute="compute_attendance")

    # @api.model
    # def create(self, val):
    #     res = super(PmExamClassSchedule, self).create(val)
    #
    #     domain = [('course_detail_ids.batch_id', '=', batch_id),
    #               ('course_detail_ids.class_id', '=', class_id)
    #               ]







    def compute_attendance(self):
        for rec in self:
            lines = rec.attendees_line
            rec.absence_count = len(lines.filtered(lambda line: line.status != 'absent'))
            rec.present_count = len(lines.filtered(lambda line: line.status == 'present'))



    def act_submit(self):
        registrar = self.add_followers_by_group('pm_leads.group_acac_registrar')
        self.message_subscribe(partner_ids=registrar)
        self.write({
            'state': 'submitted',
        })

    def add_followers_by_group(self, group_name):
        all_user = self.env['res.users'].search([])
        user_ids = all_user.mapped('id')
        partners = []
        for user_id in user_ids:
            flag = self.env['res.users'].browse(user_id).has_group(group_name)
            if flag:
                user_record = self.env['res.users'].browse(user_id)
                partners.append(user_record.partner_id.id)
        return partners

    def act_done(self):
        self.state = 'done'

    def act_draft(self):
        self.state = 'draft'

    def act_cancel(self):
        self.state = 'cancel'

class OpExamAttendeesCustom(models.Model):
    _inherit = "op.exam.attendees"
    semester_id = fields.Many2one("pm.semester", "Semester")
    class_id = fields.Many2one('op.classroom', 'Class')
    class_exam_id = fields.Many2one('pm.class.exam', 'Class Exam',  ondelete="cascade")
    show_student = fields.Boolean(compute='_compute_show_student', store=True, default=True)
    # exam_id = fields.Many2one('op.exam', 'Exam', required=False, related='class_exam_id.exam_id', store=True)
    exam_id = fields.Many2one(
        'op.exam', 'Exam', required=False, ondelete="cascade")
    session_id = fields.Many2one('op.exam.session', related='exam_id.session_id', store=True)

    def set_present(self):
        self.status = 'present'

    def set_absent(self):
        self.status = 'absent'

    @api.depends('exam_id.exam_type', 'exam_id.session_id.state')
    def _compute_show_student(self):
        for record in self:
            session = record.exam_id.session_id
            exam_type = record.exam_id.exam_type
            if exam_type == 'final_exam':
                if session.state != 'validated':
                    record.show_student = False




    def write(self, val):
        exam_state = self.class_exam_id.state
        if exam_state == 'submitted' or exam_state == 'done':
            registrar = self.env.user.has_group('openeducat_core.group_op_back_office')
            if not registrar:
                raise UserError(_('Attendees marks can not be modified once have submitted the result, Please contact registrar department'))

        res = super(OpExamAttendeesCustom, self).write(val)
        return res