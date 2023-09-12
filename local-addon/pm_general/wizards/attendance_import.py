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

from odoo import models, fields


class OpAllStudentWizard(models.TransientModel):
    _name = "op.all.student"
    _description = "All Student Wizard"

    course_id = fields.Many2one(
        'op.course', 'Course',
        default=lambda self: self.env['op.attendance.sheet'].browse(
            self.env.context['active_id']).register_id.course_id.id or False,
        readonly=True)
    batch_id = fields.Many2one(
        'op.batch', 'Term',
        default=lambda self: self.env['op.attendance.sheet'].browse(
            self.env.context['active_id']).register_id.batch_id.id or False,
        readonly=True)

    subject_id = fields.Many2one(
        'op.subject', 'Subject',
        default=lambda self: self.env['op.attendance.sheet'].browse(
            self.env.context['active_id']).session_id.subject_id.id or False,
        readonly=True)

    class_ids = fields.Many2many(
        'op.classroom', string='Class (s)',
        default=lambda self: self.env['op.attendance.sheet'].browse(
            self.env.context['active_id']).class_ids.ids or False,
        readonly=True)

    student_ids = fields.Many2many('op.student', string='Add Student(s)')

    def confirm_student(self):
        for record in self:
            for sheet in self.env.context.get('active_ids', []):
                sheet_browse = self.env['op.attendance.sheet'].browse(sheet)
                subject_id = sheet_browse.session_id.subject_id.id
                absent_list = [
                    x.student_id for x in sheet_browse.attendance_line]
                all_student_search = self.env['op.student'].search(
                    [('course_detail_ids.course_id', '=',
                      sheet_browse.register_id.course_id.id),
                     ('course_detail_ids.batch_id', '=',
                      sheet_browse.register_id.batch_id.id),
                     ('course_detail_ids.class_ids', 'in',
                      sheet_browse.session_id.class_ids.ids),
                     ('course_detail_ids.p_e_subject_ids', '!=', subject_id)])
                print(all_student_search)

                all_student_search = list(
                    set(all_student_search) - set(absent_list))

                for student_data in all_student_search:
                    vals = {'student_id': student_data.id, 'present': True,
                            'attendance_id': sheet}
                    if student_data.id in record.student_ids.ids:
                        vals.update({'present': False, 'absent': True})
                    self.env['op.attendance.line'].create(vals)
