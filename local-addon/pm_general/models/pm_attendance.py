from odoo.exceptions import ValidationError
from odoo import models, fields,api
from datetime import datetime

_DAY = [('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday '),
        ('3', 'Thursday'),
        ('4', 'Friday '),
        ('5', 'Saturday'),
        ('6', 'Sunday ')]

class PmSemesterAttendance(models.Model):
    _name = "pm.semester.attendance"
    _description = "Semester Attendance"
    student_id = fields.Many2one('op.student', 'Student')
    semester_id = fields.Many2one('pm.semester', 'Semester')
    total_hours = fields.Float('Total Missing Hours', default=0, compute='_compute_total_absent', readonly=True, store=True)
    state = fields.Selection(
        [   ('default', 'Default Points'),
            ('okay', 'Okay'),
            ('first_warning', 'First Warning'),
            ('second_warning', 'Second Warning'),
            ('dismissed', 'Dismissed')], 'State', track_visibility='onchange', default='default')
    subject_attendance_ids = fields.One2many(
        'pm.subject.attendance', 'semester_attendance_id', 'Subject Absence(s)')
    subject_total_absent_ids = fields.One2many(
        'pm.subject.total.absence', 'semester_attendance_id', 'Subject Total Absence(s)')
    no_permission_absence = fields.Integer('Absence Without Permission', compute='_compute_no_permission_absence', store=True)

    @api.depends('subject_total_absent_ids.no_permission_absencse')
    def _compute_no_permission_absence(self):
        print('hitooooo')
        for record in self:
            total = sum(x.no_permission_absencse for x in record.subject_total_absent_ids)
            print(total)
            record.no_permission_absence = total
            misbehavior_id = 0

            if total == 1:
                misbehavior_id = 39
            if total == 2:
                misbehavior_id = 24
            elif total == 3:
                misbehavior_id = 27
            elif total > 3:
                misbehavior_id = 34

            misbehaviour_category = self.env['op.misbehaviour.category'].browse(misbehavior_id)
            if misbehaviour_category:
                student_id = record.student_id.id
                misbehaviour_type = misbehaviour_category.misbehaviour_type
                semester = record.semester_id
                batch = semester.batch_id
                course = batch.course_id
                now = datetime.now()
                date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                note = 'Automatically generated on:' + date_time
                discipline = self.env['op.discipline'].create({
                    'student_id': student_id,
                    'misbehaviour_type': misbehaviour_type,
                    'misbehaviour_category_id': misbehaviour_category.id,
                    'course_id': course.id,
                    'batch_id': batch.id,
                    'semester_id': semester.id,
                    'note': note
                })
                print(discipline.state)
                discipline.act_approve()
            else:
                print('category not found')

    @api.depends('subject_total_absent_ids.total_absent_hour')
    def _compute_total_absent(self):
        for record in self:
            total = sum(x.total_absent_hour for x in record.subject_total_absent_ids)
            record.total_hours = total
            first_warning = 38
            second_warning = 43
            dismissed = 48
            ir_model_data = self.env['ir.model.data']

            if total >= first_warning and total < first_warning:
                record.state = 'okay'

            if total >= first_warning:
                record.state = 'first_warning'
                try:
                    template_id = ir_model_data.get_object_reference('pm_general', 'semester_absent_1st_warning')[1]
                except ValueError:
                    template_id = False
                self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)
            elif total >= second_warning and total < dismissed:
                record.state = 'second_warning'
                try:
                    template_id = ir_model_data.get_object_reference('pm_general', 'semester_absent_2nd_warning')[1]
                except ValueError:
                    template_id = False
                self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)
            elif total >= dismissed:
                record.student_id.education_status = 'dismissed'
                try:
                    template_id = ir_model_data.get_object_reference('pm_general', 'semester_absent_dismiss')[1]
                except ValueError:
                    template_id = False
                self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)


class PmSubjectTotalAbsence(models.Model):
    _name = "pm.subject.total.absence"
    _description = "Subject Total Absense"
    subject_attendance_ids = fields.One2many(
        'pm.subject.attendance', 'subject_total_absent_id', 'Subject Absence(s)')
    student_id = fields.Many2one('op.student', 'Student')
    subject_id = fields.Many2one('op.subject', 'Subject')
    total_absent_percent = fields.Float('Absence Percentage', compute='_compute_total_percent', store=True, readonly=True, default=0)
    total_absent_hour = fields.Float('Absence Hours', compute='_compute_total_hour', store=True, readonly=True, default=0)
    semester_attendance_id = fields.Many2one('pm.semester.attendance', 'Semester Absence')
    state = fields.Selection(
        [('default', 'Default Absence'),
         ('okay', 'Okay'),
         ('first_warning', 'First Warning'),
         ('second_warning', 'Second Warning'),
         ('dismissed', 'Dismissed')], 'State', track_visibility='onchange', default='default')
    no_permission_absencse = fields.Integer('Absence Without Permission', compute='_compute_no_permission_absencse',
                                            store=True)

    @api.depends('subject_attendance_ids.missing_hours')
    def _compute_no_permission_absencse(self):
        print('hit gogo')
        for record in self:
            count = 0
            for line in record.subject_attendance_ids.attendance_line:
                if not line.present and not line.excused and not line.remark:
                    count += 1
            record.no_permission_absencse = count

    @api.depends('subject_attendance_ids.missing_hours')
    def _compute_total_hour(self):
        for record in self:
            total_absent_hours = sum(x.missing_hours for x in record.subject_attendance_ids)
            record.total_absent_hour = total_absent_hours

    @api.depends('total_absent_hour')
    def _compute_total_percent(self):
        for record in self:
            first_warning = 0
            second_warning = 0
            dismissed = 0
            total_absent_hours = record.total_absent_hour
            total_subject_hours = record.subject_id.p_hours
            subject_type = record.subject_id.type
            absent_percentage = total_absent_hours / total_subject_hours * 100
            record.total_absent_percent = absent_percentage

            if subject_type == 'practical':
                first_warning = 5
                dismissed = 10
            else:
                first_warning = 15
                dismissed = 25

            if absent_percentage > 0 and absent_percentage < first_warning:
                record.state = 'okay'

            if absent_percentage >= first_warning:
                template_id = 46
                print('sending first warning....')
                record.state = 'first_warning'
                # self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

            if absent_percentage >= first_warning:
                template_id = 46
                print('sending first warning....')
                record.state = 'first_warning'
                # self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

            elif absent_percentage >= dismissed:
                template_id = 46
                print('sending dismissed letter....')
                record.state = 'dismissed'
                record.student_id.education_status = 'dismissed'
                # self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

class PmSubjectAttendance(models.Model):
    _name = "pm.subject.attendance"
    _description = "Subject Attendance"
    semester_attendance_id = fields.Many2one('pm.semester.attendance', 'Semester Absence')
    subject_total_absent_id = fields.Many2one('pm.subject.total.absence', 'Total Absence')
    student_id = fields.Many2one('op.student', 'Student')
    attendance_sheet_id = fields.Many2one(
        'op.attendance.sheet', 'Attendance Sheet', required=True,
        track_visibility="onchange", ondelete="cascade")
    subject_id = fields.Many2one('op.subject', 'Subject')
    attendance_line = fields.One2many(
        'op.attendance.line', 'subject_attendance_id', 'Attendance Line')
    missing_hours = fields.Float('Missing Hours')



class OpAttendanceRegister(models.Model):
    _inherit = "op.attendance.register"
    batch_id = fields.Many2one(
        'op.batch', 'Term', required=True, track_visibility='onchange')
    semester_id = fields.Many2one('pm.semester', 'Semester', required=True, track_visibility='onchange')
    auto_create = fields.Boolean('Auto Create', default=True)
    auto_create_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')], 'Auto create sheet duration' , default='daily')
    auto_create_if_session = fields.Boolean('Auto Create If Session', default=True)


class OpAttendanceSheetCustom(models.Model):
    _inherit = "op.attendance.sheet"
    classroom_id = fields.Many2one('op.classroom', related='session_id.classroom_id', store=True)
    sheet_start_time = fields.Datetime('Session Start Time')
    faculty_id = fields.Many2one('op.faculty', 'Faculty', related='session_id.faculty_id', store=True)

    def attendance_start(self):
        self.sheet_start_time = datetime.now()
        self.state = 'start'

    def attendance_done(self):

        for line in self.attendance_line:
            if not line.present:
                semester_id = self.register_id.semester_id.id
                student_id = line.student_id.id
                missing_hour = self.session_id.timing_id.duration
                subject_id = self.session_id.subject_id.id

                semester_attendance = self.env['pm.semester.attendance'].search([('semester_id', '=', semester_id),
                                                                                       ('student_id', '=', student_id)])
                subject_total_absent = self.env['pm.subject.total.absence'].search([('subject_id', '=', subject_id),
                                                                                       ('student_id', '=', student_id)])
                if not semester_attendance:
                    semester_attendance = self.env['pm.semester.attendance'].create({
                        'semester_id': semester_id,
                        'student_id': student_id,
                    })
                if not subject_total_absent:
                    subject_total_absent = self.env['pm.subject.total.absence'].create({
                        'semester_attendance_id': semester_attendance.id,
                        'subject_id': subject_id,
                        'student_id': student_id,
                    })

                subject_attendance = self.env['pm.subject.attendance'].create({
                    'semester_attendance_id': semester_attendance.id,
                    'subject_total_absent_id': subject_total_absent.id,
                    'subject_id': subject_id,
                    'student_id': student_id,
                    'missing_hours': missing_hour,
                    'attendance_sheet_id': self.id
                })
                line.subject_attendance_id = subject_attendance.id

                #Create New Record for Mobile notification
                notification_obj = self.env['pm.menu.notification']
                notification_obj.update_notification('attendance', student_id)

        self.state = 'done'

    @api.constrains('attendance_line')
    def _check_attendance_sheet_status(self):
        for record in self:
            if record.state == 'done':
                raise ValidationError("Attendance sheet has already been taken, can not be modified")

    # def write(self, val):
    #     print(self.state)
    #     if self.state == 'done':
    #         raise ValidationError("Attendance sheet has already been taken, can not be modified")
    #     res = super(OpAttendanceSheetCustom, self).write(val)
    #     return res

class OpAttendanceLineCustom(models.Model):
    _inherit = "op.attendance.line"

    student_id = fields.Many2one(
        'op.student',
        'Student',
        required=True,
        track_visibility="onchange")

    batch_id = fields.Many2one(
        'op.batch', 'Term',
        related='attendance_id.register_id.batch_id', store=True,
        readonly=True)

    classroom_id = fields.Many2one(
        'op.classroom', 'Term',
        related='attendance_id.classroom_id', store=True,
        readonly=True)

    semester_id = fields.Many2one('pm.semester', 'Semester', related='attendance_id.register_id.semester_id',
                                  store=True, readonly=True)
    subject_attendance_id = fields.Many2one('pm.subject.attendance', 'Subject Attendance', required=False)
    absent_hour = fields.Float('Missing hours')
    is_late = fields.Boolean('Late ?')
    late_duration = fields.Integer('Late Duration (Minutes)')

    def create(self, val):
        if isinstance(val, dict):
            # Using Student Import & Kiosk Mode
            item = val
            print(item)
            if 'check_in' in item:
                start_time = self.env['op.attendance.sheet'].browse(item['attendance_id']).session_id.start_datetime
                print(start_time)
                late = item['check_in'] - start_time
                seconds = late.total_seconds()
                minutes = (seconds % 3600) // 60
                print(minutes)
                if minutes >= 5:
                    val['present'] = False
                    val['late'] = True
                    val['late_duration'] = minutes
                print('I checked at', item['check_in'])
            else:
                if not item['present']:
                    print('I am absent', item['student_id'])
                else:
                    print('I am Present', item['student_id'])
        print("XDXD")
        print(val)
        res = super(OpAttendanceLineCustom, self).create(val)
        return res

    # def write(self, val):
    #     if self.attendance_id.state == 'done':
    #         raise ValidationError("Attendance sheet has already been taken, can not be modified")
    #     res = super(OpAttendanceLineCustom, self).write(val)
    #     return res

    def write(self, val):
        if self.attendance_id.state == 'done':
            raise ValidationError("Attendance sheet has already been taken, can not be modified")
        return super(OpAttendanceLineCustom, self).write(val)

class OpSessionCustom(models.Model):
    _inherit = "op.session"
    semester_id = fields.Many2one('pm.semester', 'Semester', required=True)
    day_sequence = fields.Integer()
    meeting_id = fields.Many2one('calendar.event', string='Meeting', copy=False)
    type = fields.Selection(_DAY, compute='_compute_day', string='Day', store=True)

    def lecture_confirm(self):
        print("confirm")
        meeting_values = self._prepare_holidays_meeting_values()
        meetings = self.env['calendar.event'].with_context(
            no_mail_to_attendees=True,
            active_model=self._name
        ).create(meeting_values)
        self.meeting_id = meetings.id
        self.state = 'confirm'

    def _prepare_holidays_meeting_values(self):
        result = []
        for session in self:
            meeting_values = {
                'name': session.name,
                'duration': session.timing_id.duration,
                'user_id': session.faculty_id.emp_id.user_id.id,
                'start': session.start_datetime,
                'stop': session.end_datetime,
                'allday': False,
                'privacy': 'confidential',
                'event_tz': session.faculty_id.emp_id.user_id.tz,
                'activity_ids': [(5, 0, 0)],
            }
            # Add the partner_id (if exist) as an attendee
            if session.faculty_id.emp_id.user_id and session.faculty_id.emp_id.user_id.partner_id:
                meeting_values['partner_ids'] = [
                    (4, session.faculty_id.emp_id.user_id.partner_id.id)]
            result.append(meeting_values)
        return result

    @api.depends('start_datetime')
    def _compute_day(self):
        for record in self:
            record.type = str(record.start_datetime.weekday())
            # record.day_sequence =


