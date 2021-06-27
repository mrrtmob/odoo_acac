# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

#Overided

from odoo import models, api, fields, exceptions, _


class OpRoomDistribution(models.TransientModel):
    """ Exam Room Distribution """
    _name = "op.room.distribution"
    _description = "Room Distribution"

    @api.depends('student_ids')
    def _compute_get_total_student(self):
        for record in self:
            total_student = 0
            if record.student_ids:
                total_student = len(record.student_ids)
            record.total_student = total_student

    @api.depends('room_ids', 'room_ids.capacity')
    def _compute_get_room_capacity(self):
        for record in self:
            room_capacity = 0
            if record.room_ids:
                for room in record.room_ids:
                    room_capacity += (room.capacity or 0)
            record.room_capacity = room_capacity

    exam_id = fields.Many2one('op.exam', 'Exam(s)')
    subject_id = fields.Many2one('op.subject', 'Subject',
                                 related="exam_id.subject_id")
    name = fields.Char("Exam")
    start_time = fields.Datetime("Start Time")
    end_time = fields.Datetime("End Time")
    exam_session = fields.Many2one("op.exam.session", 'Exam Session')
    course_id = fields.Many2one("op.course", 'Course')
    batch_id = fields.Many2one("op.batch", 'Batch')
    total_student = fields.Integer(
        "Total Student", compute="_compute_get_total_student")
    room_capacity = fields.Integer(
        "Room Capacity", compute="_compute_get_room_capacity")
    room_ids = fields.Many2many("op.exam.room", string="Exam Rooms")
    class_id = fields.Many2one('op.classroom', 'Class')
    class_exam_id = fields.Many2one('pm.class.exam', 'Class Exam')
    student_ids = fields.Many2many("op.student", String='Student')

    @api.model
    def default_get(self, fields):
        res = super(OpRoomDistribution, self).default_get(fields)
        active_id = self.env.context.get('active_id', False)
        class_exam = self.env['pm.class.exam'].browse(active_id)
        exam = class_exam.exam_id
        session = exam.session_id
        term = session.batch_id
        class_room = class_exam.class_id
        reg_ids = self.env['op.student.course'].search(
            [('class_id', '=', class_room.id), ('batch_id', '=', term.id)])
        student_ids = []
        for reg in reg_ids:
            subjects_list = []
            exempted_subject = reg.p_e_subject_ids
            subject_id = session.subject_id.id
            for ex in exempted_subject:
                subjects_list.append(ex.id)
            if subject_id in subjects_list:
                continue
            else:
                student_ids.append(reg.student_id.id)

        student_ids = list(set(student_ids))
        total_student = len(student_ids)
        res.update({
            'exam_id': exam.id,
            'name': exam.name,
            'start_time': class_exam.start_time,
            'end_time': class_exam.end_time,
            'exam_session': session.id,
            'course_id': session.course_id.id,
            'batch_id': session.batch_id.id,
            'class_id': class_room.id,
            'class_exam_id': active_id,
            'total_student': total_student,
            'student_ids': [(6, 0, student_ids)],
        })
        return res

    def schedule_exam(self):
        attendance = self.env['op.exam.attendees']
        for exam_class in self:
            if exam_class.total_student > exam_class.room_capacity:
                raise exceptions.AccessError(
                    _("Room capacity must be greater than total number \
                      of student"))
            print(exam_class)
            student_ids = exam_class.student_ids.ids

            for stu_id in student_ids:
                notification_obj = self.env['pm.menu.notification']
                notification_obj.update_notification('exam', stu_id)

            exam = exam_class.exam_id
            for room in exam_class.room_ids:
                for i in range(room.capacity):
                    if not student_ids:
                        continue
                    attendance.create({
                        'exam_id': exam.id,
                        'student_id': student_ids[0],
                        'status': 'present',
                        'class_id': exam_class.class_id.id,
                        'class_exam_id': exam_class.class_exam_id.id,
                        'course_id': exam.course_id.id,
                        'batch_id': exam.batch_id.id,
                        'room_id': room.id
                    })
                    student_ids.remove(student_ids[0])
            exam_class.class_exam_id.state = 'schedule'
            return True
