# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class StudentReturnWizard(models.TransientModel):

    _name = "student.return.wizard"
    _description = "Student Return"

    date = fields.Date('Date', required=True, default=lambda self: fields.Date.today())
    @api.model
    def _get_default_course(self):
        course = self.env['op.course'].search(
            ['|', ('code', '=', 'CUL'), ('name', '=', '2-Year Diploma in Culinary Art')], limit=1)
        return course.id

    course_id = fields.Many2one('op.course', 'Course', required=True, default=_get_default_course)
    batch_id = fields.Many2one(
        'op.batch', 'Term', required=True, track_visibility='onchange')
    class_id = fields.Many2one('op.classroom', 'Class')
    starting_semester_id = fields.Many2one('pm.semester', 'Starting Semester', required=True)
    class_ids = fields.Many2many('op.classroom')
    remarks = fields.Text()

    def confirm_return_student(self):
        print("Confirm")
        active_id = self.env.context.get('active_ids', []) or []
        student = self.env['op.student'].browse(active_id)
        student.enable_student_payment()
        course_id = self.course_id
        batch_id = self.batch_id
        class_ids = [[6, False, self.class_ids.ids]]
        semester_id = self.starting_semester_id

        student.course_detail_ids.p_active = False
        student.write({
            'course_detail_ids': [[0, False, {
                'course_id':
                    course_id and course_id.id or False,
                'batch_id':
                    batch_id and batch_id.id or False,
                'starting_semester_id':
                    semester_id and semester_id.id or False,
                'p_active': True,
                'class_ids' : class_ids,
                'remarks': self.remarks,
            }]],
        })

        student.get_subjects_for_students(course_id.id, batch_id.id ,student.id)

        # Store Student Progression detail in this case, the student return to new term
        progress_obj = self.env['pm.student.progress'].sudo()
        progress_obj.store_progression(student.id, course_id.id, batch_id.id, 'active', self.remarks)

        order = semester_id.semester_order
        semester_ids = batch_id.semester_ids
        semester_detail = student.student_semester_detail
        semester_discipline = student.semester_discipline
        semester_attendance = student.semester_attendance

        for new_sem in semester_ids:
            for old_sem in semester_detail:
                if old_sem.semester_id.semester_order == new_sem.semester_order:
                    if old_sem.state != 'complete':
                        old_sem.write({
                            'batch_id': batch_id,
                            'course_id': course_id,
                            'semester_id': new_sem.id,
                        })
                if old_sem.semester_id.semester_order == order:
                    old_sem.state = 'ongoing'


            for sem_discipline in semester_discipline:
                if sem_discipline.semester_id.semester_order == new_sem.semester_order:
                    sem_discipline.semester_id = new_sem.id

            for sem_attendance in semester_attendance:
                if sem_attendance.semester_id.semester_order == new_sem.semester_order:
                    sem_attendance.semester_id = new_sem.id

        student._compute_active_semester()

        # notification = {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': 'Student Migration',
        #         'message': 'Student has been transferred successfully',
        #         'type': 'success',  # types: success,warning,danger,info
        #         'sticky': False,  # True/False will display for few seconds if false
        #     },
        # }
        # return notification
