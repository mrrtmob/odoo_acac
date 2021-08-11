# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).get_birth_place
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

import time

from odoo import models, api


class StudentTranscriptReport(models.AbstractModel):
    _name = "report.pm_students.student_transcript"
    _description = "Transcript Report"

    def get_student_name(self, data):
        student = self.env['op.student'].browse(data['student_id'])
        if student:
            return student.name
    
    def get_student_id(self, data):
        student = self.env['op.student'].browse(data['student_id'])
        if student:
            return student.student_app_id

    def get_student_nationality(self, data):
        student = self.env['op.student'].browse(data['student_id'])
        if student:
            return student.nationality.name
    
    def get_student_bod(self, data): 
        student = self.env['op.student'].browse(data['student_id'])
        if student:
            return student.birth_date.strftime('%d/%m/%Y')

    def get_birth_place(self, data):
        student = self.env['op.student'].browse(data['student_id']) 
        if student: 
            return student.birth_place.name
    
    def is_final(self, data): 
        return data['is_final'] 

    def get_semester_order(self, data):
        return data['semester_order']
    
    def get_semester_start_date(self, data):
        return data['semester_start_date']
    
    def get_semester_end_date(self, data):
        return data['semester_end_date']

    def get_data(self, data):
        lst = []
        gpa = 0
        absence = 0
        semester_average =0
        # get student course

        student_courses = self.env['op.student.course'].search([('course_id', '=', data['course_id']),
                                                                ('student_id', '=', data['student_id'])])
        # get student Exempted Subjects 
        ex_subjects = []
        # get student discipline points 

        student = self.env['op.student'].browse(data['student_id'])
        discipline_points = 10
        student_discipline = self.env['pm.student.discipline'].search([('student_id', '=', data['student_id'])])
        student_results = student.semester_result
        student_attendance = student.semester_attendance

        for sc in student_courses:
            ex_subjects.append(sc.p_e_subject_ids)

        semesters = self.env['pm.semester'].search([('batch_id', '=', data['batch_id'])])
        total_course_credit = sum(x.total_credit for x in semesters)
        if data['is_final']:
            wiegh_average_gpa = 0
            ex_count = 0
            gpa = 0
            sub_count = 0

            if student_discipline:
                total_point = 0
                count = len(student_discipline)
                if count > 0:
                    for sd in student_discipline:
                        total_point += sd.discipline_point
                discipline_points = total_point / count

            if student_attendance:
                for sa in student_attendance:
                    absence += sa.total_hours

            for res in student_results:
                semester_credit = res.semester_id.total_credit
                wiegh_average_gpa += res.gpa * semester_credit
                for srl in res.semester_res_line:
                    if srl.exam_state != 'covered':
                        subject = srl.subject_id
                        grade = ''
                        if subject in ex_subjects:
                            grade = 'E'
                            ex_count += 1
                        else:
                            grade = srl.grade
                        sub_count += 1
                        dic = {
                            'code': subject.code,
                            'name': subject.name,
                            'credits': subject.p_credits,
                            'grade': grade,
                            'score': srl.total_score
                        }
                        lst.append(dic)

            placement = self.env['op.placement.offer'].search(
                [('student_id', '=', data['student_id']), ('batch_id', '=', data['batch_id']),
                 ('p_completed', '=', True)], order='join_date')
            for pl in placement:
                grade = 'F'
                print('hit placement')
                intership_grade_point = pl.gpa * pl.subject_id.p_credits
                wiegh_average_gpa += intership_grade_point
                absence += pl.p_absences
                if pl.p_status == 'passed':
                    grade = 'P'
                dic = {
                    'code': pl.subject_id.code,
                    'name': pl.subject_id.name,
                    'credits': pl.subject_id.p_credits,
                    'grade': grade
                }
                lst.append(dic)
            gpa = round(wiegh_average_gpa / total_course_credit, 1)


        # Transcript for one semester
        else:
            semester = self.env['pm.semester'].browse(data['semester_id'])
            total_course_credit = 0

            if student_discipline:
                total_point = 0
                count = len(student_discipline)
                if count > 0:
                    for sd in student_discipline:
                        if sd.semester_id.id == data['semester_id']:
                            discipline_points = sd.discipline_point

            if student_attendance:
                for sa in student_attendance:
                    if sa.semester_id.id == data['semester_id']:
                        absence += sa.total_hours

            # get all subjects from a semester
            if semester.is_internship:
                placement = self.env['op.placement.offer'].search([('student_id', '=', data['student_id']) , ('semester_id', '=', data['semester_id']) , ('p_completed' , '=' , True)])
                for pl in placement:
                    grade = 'F'
                    total_course_credit += pl.subject_id.p_credits
                    if pl.p_status == 'passed':
                        grade = 'P'
                        absence = pl.p_absences
                    dic = {
                        'code': pl.subject_id.code,
                        'name': pl.subject_id.name,
                        'credits': pl.subject_id.p_credits,
                        'grade': grade,

                    }

                    lst.append(dic)
            else:
                total_course_credit = semester.total_credit
                ex_count = 0
                sub_count = 0
                for res in student_results:
                    semester_average = res.result
                    print('1', res.semester_id.id)
                    print('2', data['semester_id'])
                    if res.semester_id.id == data['semester_id']:
                        print('hit coni')
                        gpa = res.gpa
                        for srl in res.semester_res_line:
                            if srl.exam_state != 'covered':
                                subject = srl.subject_id
                                grade = ''
                                if subject in ex_subjects:
                                    grade = 'E'
                                    ex_count += 1
                                else:
                                    grade = srl.grade
                                sub_count += 1
                                dic = {
                                    'code': subject.code,
                                    'name': subject.name,
                                    'credits': subject.p_credits,
                                    'grade': grade,
                                    'score': srl.total_score
                                }
                                lst.append(dic)
                            else:
                                continue

        return [{'subjects': lst,
                 'absence': absence,
                'gpa': gpa,
                'semester_average': semester_average,
                'total_course_credit': total_course_credit,
                'discipline_points': discipline_points,
                'total_credit': total_course_credit}]
       

    @api.model
    def _get_report_values(self, docids, data=None):
        print ('_get_report_values')
     
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'time': time,
            'get_student_name': self.get_student_name(data),
            'get_student_nationality': self.get_student_nationality(data),
            'get_student_bod': self.get_student_bod(data),
            'get_data': self.get_data(data),
            'get_semester_order': self.get_semester_order(data),
            'is_final': self.is_final(data),
            'get_birth_place': self.get_birth_place(data),
            'get_semester_start_date': self.get_semester_start_date(data),
            'get_semester_end_date': self.get_semester_end_date(data),
            'get_student_id': self.get_student_id(data)
        }
        return docargs

