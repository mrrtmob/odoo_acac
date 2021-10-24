from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class StudentTranscript(models.TransientModel):
    _name = "student.transcript"
    _description = "Student Transcript"
    from_date = fields.Date(
        'From Date', required=True, default=lambda self: fields.Date.today())
    to_date = fields.Date(
        'To Date', required=True, default=lambda self: fields.Date.today())
    course_id = fields.Many2one('op.course', 'Course', required=True, default=lambda self: self._get_default_course())
    batch_id = fields.Many2one(
        'op.batch', 'Term', required=True, default=lambda self: self._get_default_batch())
    semester_id = fields.Many2one('pm.semester', 'Semester')
    final = fields.Boolean('Final Transcript')


    def _get_default_batch(self):
        student_id = self.env.context.get('active_id', False)
        student_course = self.env['op.student.course'].search([('student_id', '=', student_id),
                                                               ('p_active', '=', True)], limit=1)
        return student_course.batch_id.id

    def _get_default_course(self):
        student_id = self.env.context.get('active_id', False)
        student_course = self.env['op.student.course'].search([('student_id', '=', student_id),
                                                               ('p_active', '=', True)], limit=1)
        return student_course.course_id.id



    def print_report(self):
        student_id = self.env.context.get('active_id', False)
        order = self.semester_id.semester_order
        is_internship = self.semester_id.is_internship
        if self.semester_id:
            print("self.semester_id.start_date")
            semester_start_date = self.semester_id.start_date.strftime('%d/%m/%Y')
            semester_end_date = self.semester_id.end_date.strftime('%d/%m/%Y')
        else:
            semester_start_date = ''
            semester_end_date = ''

        res = {
            "student_id": student_id,
            "semester_order": order,
            "semester_start_date": semester_start_date,
            "semester_end_date": semester_end_date,
            "course_id": self.course_id.id,
            "batch_id": self.batch_id.id,
            "semester_id": self.semester_id.id,
            "is_final": self.final
        }
        if self.final:
            print("check validation")
            internship_semester_count = self.env['pm.semester'].search_count([('batch_id', '=', self.batch_id.id),
                                                                              ('is_internship', '=', True)])

            normal_semester_count = self.env['pm.semester'].search_count([('batch_id', '=', self.batch_id.id),
                                                                          ('is_internship', '=', False)])

            student_internship_count = self.env['op.placement.offer'].search_count([('student_id', '=', student_id),
                                                                                    ('batch_id', '=', self.batch_id.id),
                                                                                    ('p_completed', '=', True)])

            mark_sheets_count = self.env['pm.semester.marksheet.register'].search_count(
                [('batch_id', '=', self.batch_id.id),
                 ('state', '=', 'validated')])

            _logger.info("---------------*****************************---------------")
            _logger.info('internship_semester_count %s', internship_semester_count)
            _logger.info('normal_semester_count %s', normal_semester_count)
            _logger.info('student_internship_count %s', student_internship_count)
            _logger.info('mark_sheets_count %s', mark_sheets_count)

            if internship_semester_count != student_internship_count:
                raise ValidationError(
                    "Internship hasn't finished yet. Please completed before generating transcript")

            if normal_semester_count != mark_sheets_count:
                raise ValidationError("Please validate semester result before generating transcript")

            return self.env.ref(
                'pm_students.action_get_report_transcript') \
                .report_action(self, data=res)

        elif is_internship:
            print('internshpip')
            count = self.env['op.placement.offer'].search_count(
                [('student_id', '=', student_id), ('semester_id', '=', self.semester_id.id),
                 ('p_completed', '=', True)])
            if count <= 0:
                raise ValidationError("Internship hasn't finised yet. Please completed before generating transcript")
            else:
                return self.env.ref(
                    'pm_students.action_get_report_transcript') \
                    .report_action(self, data=res)
        else:
            print("check validation")
            count = self.env['pm.semester.marksheet.register'].search_count(
                [('semester_id', '=', self.semester_id.id), ('state', '=', 'validated')])
            if count <= 0:
                raise ValidationError("Please validate semester result before generating transcript")
            else:
                return self.env.ref(
                    'pm_students.action_get_report_transcript') \
                    .report_action(self, data=res)
