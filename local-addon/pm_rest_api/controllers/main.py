# -*- coding: utf-8 -*-
from _multiprocessing import sem_unlink

import logging
import requests
from werkzeug import exceptions
from odoo import http
from odoo.http import request
from odoo.addons.openeducat_rest.controllers.main import RESTController
from odoo.addons.openeducat_rest.controllers.main import check_token, check_params, ObjectEncoder
from odoo.addons.openeducat_core_enterprise.controllers.main import StudentPortal as Student
from odoo.http import Response
from datetime import datetime, timedelta
import pytz
from odoo.tools import html2plaintext, plaintext2html
from odoo.addons.pm_rest_api.controllers.aba_payway import ABAPayWay
import json




_logger = logging.getLogger(__name__)

NOT_FOUND = {
    'error': 'unknown_command',
}

DB_INVALID = {
    'error': 'invalid_db',
}

FORBIDDEN = {
    'error': 'token_invalid',
}

NO_API = {
    'error': 'rest_api_not_supported',
}

LOGIN_INVALID = {
    'error': 'invalid_login',
}




def abort(message, rollback=False, status=403):
    response = Response(json.dumps(message,
                                   sort_keys=True, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=status)
    if request._cr and rollback:
        request._cr.rollback()
    exceptions.abort(response)


class PathmazingApi(RESTController):

    def clear_notification(self, menu_name, student_id):
        menu_notification_obj = request.env['pm.menu.notification']
        menu_notification_obj.sudo().clear_notification(menu_name, student_id)


    def get_image(self, student_id):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        image_url_1920 = base_url + '/web/image?' + 'model=op.student&id=' + str(student_id) + '&field=image_1920'
        return image_url_1920

    @http.route('/api/v1/student',
                auth="user", type='http', token=None,  methods=['GET'], csrf=False)
    def get_student_profile(self, token=None, **kw):
        check_params({'token': token})
        check_token()
        student = Student.get_student(self)
        if student:
            student_img = ""
            if student.image_1920:
                student_img = self.get_image(student.id)
            payment_data = []
            items = {}
            address = {
                'street': student.street,
                'street2': student.street2,
                'city': student.city,
                'state_id': student.state_id.id,
                'state': student.state_id.name,
                'country_id': student.country_id.id,
                'country': student.country_id.name,
            }
            payments = request.env['op.student.fees.details'].sudo().search(
                [('student_id', '=', student.id)])
            if payments:
                for payment in payments:
                    val = {
                        'amount': payment.amount,
                        'status': payment.invoice_id.state,
                        'due_date': payment.date,
                    }
                    payment_data.append(val)
            menu_item_obj = request.env['pm.menu.notification']

            item_records = menu_item_obj.sudo().search([('student_id', '=', student.id),
                                                        ('is_seen', '=', False)])
            announcement = menu_item_obj.sudo().search_count([
                ('menu_name', '=', 'announcement'),
                ('student_id', '=', student.id),
                ('is_seen', '=', False),
            ])

            if announcement:
                items['announcement'] = announcement

            if item_records:
                for rec in item_records:
                    items[rec.menu_name] = rec.record_count
            response = {
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'student_app_id': student.student_app_id,
                'gender': student.gender,
                'image': student_img,
                'email': student.user_id.login,
                'birth_date': student.birth_date,
                'nationality': student.nationality.name,
                'mobile': student.mobile,
                'address': address,
                'payments': payment_data,
                'menu_item': items
            }

            return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)


    @http.route('/api/v1/student/update/address',
                auth="user", type='http', new_street=None, new_street2=None, new_city=None, new_state_id=None,
                new_country_id=None, token=None, methods=['PUT'], csrf=False)
    def update_student_address(self, new_street=None, new_street2=None, new_city=None, new_state_id=None,
                               new_country_id=None, token=None, **kw):
        check_params({'token': token})
        check_token()
        student = Student.get_student(self)
        if not student:
            response = {
                'message': 'Invalid student not found'
            }
            return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=404)
        if student:
            val = {
                'street': new_street,
                'street2': new_street2,
                'city': new_city,
                'state_id': int(new_state_id),
                'country_id': int(new_country_id)
            }
            student.write(val)
            return Response(json.dumps({'message': 'ok'}, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/v1/student/update/mobile',
                auth="user", type='http', new_mobile=None, token=None, methods=['PUT'], csrf=False)
    def update_student_mobile(self, new_mobile=None, token=None, **kw):
        check_params({'token': token})
        check_token()
        student = Student.get_student(self)
        if not student:
            response = {
                'message': 'Invalid student not found'
            }
            return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=404)
        if student:
            student.write({'mobile': new_mobile})
            return Response(json.dumps({'message': 'ok'}, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/v1/student/update/password',
                auth="user", type='http', db=None, old_password=None, new_password=None, confirm_new_password=None,
                token=None, methods=['PUT'], csrf=False)
    def update_student_password(self, db=None, old_password=None, new_password=None,  token=None, **kw):
        check_params({'token': token})
        check_token()
        student = Student.get_student(self)
        if student:
            uid = request.session.authenticate(db, student.user_id.login, old_password)
            if not uid:
                return Response(
                    json.dumps({'message': 'Please enter the correct old password'}, indent=4, cls=ObjectEncoder),
                    content_type='application/json;charset=utf-8', status=404)

            student.user_id.write({'password': new_password})
            return Response(json.dumps({'message': 'ok'}, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)


    @http.route('/api/v1/country',
                auth="user", type='http', token=None, methods=['GET'], csrf=False)
    def get_country(self, token=None, **kw):
        check_params({'token': token})
        check_token()
        country_data = []
        domain = []
        countries = request.env['res.country'].sudo().search(domain)
        response = {}
        if countries:
            for country in countries:
                val = {
                    'id': country.id,
                    'name': country.name
                }
                country_data.append(val)
            response = {
                'data': country_data
            }
        return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/v1/state/',
                auth="user", type='http', country_id=None, token=None, methods=['GET'], csrf=False)
    def get_state(self, token=None, country_id=None, **kw):
        check_params({'token': token})
        check_token()
        state_data = []
        domain = []
        response = {}
        if country_id:
            domain.append(('country_id', '=', int(country_id)))
            states = request.env['res.country.state'].sudo().search(domain)
        else:
            states = request.env['res.country.state'].sudo().search(domain)
        if states:
            for state in states:
                val = {
                    'id': state.id,
                    'name': state.name,
                    'country_id': state.country_id.id,
                    'country': state.country_id.name
                }
                state_data.append(val)
            response = {
                'data': state_data
            }
        return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route(['/api/v1/announcement',
                 '/api/v1/announcement/<int:announcement_id>'],
                auth="user", type='http', token=None, methods=['GET'], csrf=False)
    def get_student_announcement(self, announcement_id=None, token=None, **kw):
        check_params({'token': token})
        check_token()
        student = Student.get_student(self)
        response = {}
        if student:
            self.clear_notification('announcement', student.id)
            if announcement_id:
                domain = [('id', '=', announcement_id)]
                announcement_detail = request.env['hr.announcement'].sudo().search(domain)
                if announcement_detail:
                    announcement_id = announcement_detail.id
                    name = announcement_detail.announcement_reason
                    date_start = announcement_detail.date_start.strftime('%d, %B %Y')
                    status = announcement_detail.status
                    announcement_desc = html2plaintext(announcement_detail.announcement)
                    response = {
                        'id': announcement_id,
                        'name': name,
                        'date': date_start,
                        'status': status,
                        'announcement': announcement_desc,
                    }
            else:
                announcement_data = []
                domain = [('is_stu_announcement', '=', True), ('state', '=', 'confirmed')]
                announcements = request.env['hr.announcement'].sudo().search(domain)
                if announcements:
                    for announcement in announcements:
                        announcement_id = announcement.id
                        name = html2plaintext(announcement.announcement_reason)
                        date_start = announcement.date_start.strftime('%d, %B %Y')
                        status = announcement.status
                        announcement_desc = html2plaintext(announcement.announcement)
                        stu_batch_id = student.batch_id
                        stu_class_id = student.class_id.id
                        ann_batch_id = announcement.batch_id.id
                        ann_class_id = announcement.class_id.id
                        val = {
                            'id': announcement_id,
                            'name': name,
                            'date': date_start,
                            'status': status,
                            'announcement': announcement_desc,
                        }
                        if announcement.is_all_stu_announcement:
                            announcement_data.append(val)
                        else:
                            if ann_class_id and ann_batch_id:
                                if stu_class_id == ann_class_id and ann_batch_id == stu_batch_id:
                                    announcement_data.append(val)
                            elif ann_batch_id and ann_class_id is False:
                                if ann_batch_id == stu_batch_id:
                                    announcement_data.append(val)
                    response = {
                        'data': announcement_data
                    }
        return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route(['/api/v1/discipline',
                 '/api/v1/discipline/<int:discipline_id>'],
                auth="user", type='http', token=None, methods=['GET'], csrf=False)
    def get_student_discipline_semester(self, discipline_id=None, token=None, **kw):
        check_params({'token': token})
        check_token()
        student = Student.get_student(self)
        response = {}
        if student:
            self.clear_notification('discipline', student.id)
            domain = [('student_id', '=', student.id)]
            if discipline_id:
                domain.append(('id', '=', discipline_id))
                discipline = request.env['pm.student.discipline'].sudo().search(domain)
                if discipline:
                    domain_detail = [('student_discipline_id', '=', discipline.id), ('student_id', '=', student.id)]
                    discipline_detail_data = []
                    discipline_details = request.env['op.discipline'].sudo().search(domain_detail)
                    if discipline_details:
                        for discipline_detail in discipline_details:
                            val = {
                                'date': discipline_detail.date,
                                'misbehaviour': discipline_detail.misbehaviour_category_id.name,
                                'demerit': discipline_detail.misbehaviour_category_id.p_demerit_points,
                            }
                            discipline_detail_data.append(val)
                        response = {
                            'semester_name': discipline.semester_id.name,
                            'point': discipline.discipline_point,
                            'status': discipline.state,
                            'discipline_details': discipline_detail_data
                        }
            else:
                disciplines_data = []
                disciplines = request.env['pm.student.discipline'].sudo().search(domain)
                if disciplines:
                    for discipline in disciplines:
                        val = {
                            'id': discipline.id,
                            'semester_name': discipline.semester_id.name,
                            'point': discipline.discipline_point,
                            'status': discipline.state,
                        }
                        disciplines_data.append(val)
                    response = {
                        'data': disciplines_data
                    }
        return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route(['/api/v1/student/attendance',
                 '/api/v1/student/attendance/<int:attendance_id>'],
                auth="user", type='http', token=None, methods=['GET'], csrf=False)
    def get_attendance(self, attendance_id=None, token=None, **kw):
        check_params({'token': token})
        check_token()
        student = Student.get_student(self)
        response = {}
        if student:
            self.clear_notification('attendance', student.id)
            domain = [('student_id', '=', student.id)]
            if attendance_id:
                domain.append(('id', '=', attendance_id))
                attendance = request.env['pm.semester.attendance'].sudo().search(domain)
                if attendance:
                    attendance_detail_data = []
                    domain_detail = [('semester_attendance_id', '=', attendance.id)]
                    attendance_details = request.env['pm.subject.total.absence'].sudo().search(domain_detail)
                    if attendance_details:
                        for attendance_detail in attendance_details:
                            subject = attendance_detail.subject_id.name
                            absent = attendance_detail.total_absent_hour
                            percentage = round(attendance_detail.total_absent_percent)
                            val = {
                                'subject': subject,
                                'absent': absent,
                                'percentage': percentage,
                            }
                            attendance_detail_data.append(val)
                        pin = student.pin
                        semester = attendance.semester_id.name
                        state = attendance.state
                        hours = attendance.total_hours
                        response = {
                            'pin': pin,
                            'semester': semester,
                            'state': state,
                            'hours': hours,
                            'attendance_detail': attendance_detail_data,
                        }
            else:
                attendance_data = []
                attendances = request.env['pm.semester.attendance'].sudo().search(domain)
                if attendances:
                    for attendance in attendances:
                        attendance_id = attendance.id
                        pin = student.pin
                        semester = attendance.semester_id.name
                        state = attendance.state
                        hours = attendance.total_hours
                        val = {
                            'id': attendance_id,
                            'pin': pin,
                            'semester': semester,
                            'state': state,
                            'hours': hours,
                        }
                        attendance_data.append(val)
                    response = {
                        'data': attendance_data
                    }
        return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/v1/student/exam/filter',
                auth="user", type='http', semester_id=None, token=None, methods=['GET'], csrf=False)
    def get_subject(self, token=None, semester_id=None, **kw):
        check_params({'token': token})
        check_token()
        student = Student.get_student(self)
        response = {}
        if student:
            self.clear_notification('exam', student.id)
            semester_data = []
            domain = [('batch_id', '=', int(student.batch_id))]
            if semester_id:
                domain.append(('id', '=', semester_id))
                semesters = request.env['pm.semester'].sudo().search(domain)
            else:
                semesters = request.env['pm.semester'].sudo().search(domain)
            if semesters:
                for semester in semesters:
                    subjects = semester.get_semester_subject()
                    subject_data = []
                    semester_id = semester.id
                    semester_name = semester.name
                    if subjects:
                        for subject in subjects:
                            subject_id = subject.id
                            subject_name = subject.name
                            val = {
                                'id': subject_id,
                                'name': subject_name,
                                'semester_id': semester_id
                            }
                            subject_data.append(val)
                        val = {
                            'id': semester_id,
                            'name': semester_name,
                            'subject': subject_data,
                        }
                    semester_data.append(val)
                response = {
                    'data': semester_data,
                }
        return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/v1/student/exam/upcoming',
                auth="user", type='http', token=None, methods=['GET'], csrf=False)
    def get_upcoming_exam(self, token=None, **kw):
        check_params({'token': token})
        check_token()
        student = Student.get_student(self)
        response = {}
        if student:
            today = datetime.now()
            domain = [('batch_id', '=', int(student.batch_id)), ('class_id', '=', int(student.class_id)), ('start_time', '>=', today)]
            next_two_week = today + timedelta(days=+today.weekday(), weeks=2)
            upcoming_exam_data = []
            upcoming_exams = request.env['pm.class.exam'].sudo().search(domain, order='start_time')
            if upcoming_exams:
                for upcoming_exam in upcoming_exams:
                    name = upcoming_exam.exam_id.name
                    subject = upcoming_exam.subject_id.name
                    semester = upcoming_exam.semester_id.name
                    exam_date = upcoming_exam.start_time.astimezone(pytz.timezone("Asia/Phnom_Penh"))
                    exam_time = upcoming_exam.start_time.astimezone(pytz.timezone("Asia/Phnom_Penh")).strftime('%d, %B %Y %I:%M%p')
                    end_date = upcoming_exam.end_time.astimezone(pytz.timezone("Asia/Phnom_Penh"))
                    duration = end_date.hour - exam_date.hour
                    if duration <= 1:
                        duration = str(duration) + ' Hour'
                    else:
                        duration = str(duration) + ' Hours'
                    exam_type = upcoming_exam.exam_id.exam_type
                    exam_type = str.split(exam_type, '_')
                    if len(exam_type) > 1:
                        exam_type = str.capitalize(exam_type[0]) + ' ' + str.capitalize(exam_type[1])
                    else:
                        exam_type = str.split(exam_type[0], '-')
                        if len(exam_type) > 1:
                            exam_type = str.capitalize(exam_type[0]) + ' ' + str.capitalize(exam_type[1])
                        else:
                            exam_type = str.capitalize(exam_type[0])
                    val = {
                        'name': name,
                        'subject': subject,
                        'semester': semester,
                        'exam_type': exam_type,
                        'exam_time': exam_time,
                        'duration': duration,
                    }
                    if next_two_week.date() >= exam_date.date():
                        upcoming_exam_data.append(val)
                if upcoming_exam_data:
                    response = {
                        'data': upcoming_exam_data,
                    }
        return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/v1/student/exam',
                auth="user", type='http', semester_id=None, subject_ids=None, date_filter=None,
                token=None, methods=['GET'], csrf=False)
    def get_exam(self, semester_id=None, subject_ids=None, date_filter=None, token=None, **kw):
        check_params({'token': token})
        check_token()
        student = Student.get_student(self)
        response = {}
        if student:
            domain = [('student_id', '=', student.id)]
            if subject_ids:
                array_subject_id = str.split(subject_ids, ', ')
                int_array_subject_ids = [int(subject_id) for subject_id in array_subject_id]
                domain.append(('exam_id.subject_id.id', 'in', int_array_subject_ids))
            if semester_id:
                domain.append(('marksheet_line_id.semester_id.id', '=', semester_id))
            histories = request.env['op.result.line'].sudo().search(domain)
            today = datetime.now().today()
            history_data = []
            if histories:
                for history in histories:
                    semester = history.marksheet_line_id.semester_id.name
                    subject = history.exam_id.subject_id.name
                    grade = history.marks
                    status = str.capitalize(history.status)
                    exam_date = history.exam_id.session_id.start_date
                    exam_type = history.exam_id.exam_type
                    exam_type = str.split(exam_type, '_')
                    if len(exam_type) > 1:
                        exam_type = str.capitalize(exam_type[0]) + ' ' + str.capitalize(exam_type[1])
                    else:
                        exam_type = str.split(exam_type[0], '-')
                        if len(exam_type) > 1:
                            exam_type = str.capitalize(exam_type[0]) + ' ' + str.capitalize(exam_type[1])
                        else:
                            exam_type = str.capitalize(exam_type[0])
                    val = {
                        'semester': semester,
                        'subject': subject,
                        'exam_type': exam_type,
                        'grade': grade,
                        'exam_date': str(exam_date),
                        'status': status
                    }
                    if date_filter:
                        if date_filter == 'today' and exam_date == today:
                            history_data.append(val)
                        elif history_data == 'this month' and exam_date.month == today.month and exam_date.year == today.year:
                            history_data.append(val)
                        elif date_filter == 'this year' and exam_date.year == today.year:
                            history_data.append(val)
                    else:
                        history_data.append(val)
                history_data = sorted(history_data, key=lambda x: datetime.strptime(x['exam_date'], '%Y-%m-%d'))
                if history_data:
                    response = {
                        'data': history_data
                    }
        return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route(['/api/v1/student/grade',
                 '/api/v1/student/grade/<int:grade_id>'],
                auth="user", type='http', token=None, methods=['GET'], csrf=False)
    def get_grade(self, grade_id=None, token=None, **kw):
        check_params({'token': token})
        check_token()
        student = Student.get_student(self)
        response = {}
        if student:
            self.clear_notification('grade', student.id)
            if grade_id:
                semester_results = request.env['pm.semester.result'].sudo().browse(grade_id)
                if semester_results:
                    for semester_result in semester_results:
                        semester = semester_result.semester_id.name
                        status = semester_result.status
                        total_gpa = semester_result.gpa
                        domain_detail = [('semester_result_id', '=', grade_id)]
                        semester_result_lines = request.env['pm.semester.result.line'].sudo().search(domain_detail)
                        semester_result_line_data = []
                        if semester_result_lines:
                            for semester_result_line in semester_result_lines:
                                subject_id = semester_result_line.subject_id.id
                                subject = semester_result_line.subject_id.name
                                latter_grade = semester_result_line.grade
                                domain_gpa = [('result', '=', latter_grade)]
                                get_gpa = request.env['op.grade.configuration'].sudo().search(
                                    domain_gpa)
                                if get_gpa:
                                    for gpa in get_gpa:
                                        gpa = gpa.grade_point
                                grade = semester_result_line.total_score

                                result_lines = request.env['op.result.line'].sudo().search([
                                    ('exam_id.subject_id', '=', subject_id),
                                    ('marksheet_line_id.marksheet_reg_id.state', '=', 'validated'),
                                    ('student_id', '=', student.id)
                                ])
                                exam_details = []
                                if result_lines:
                                    for result in result_lines:
                                        exam_details.append(
                                            {
                                                'exam': result.exam_id.name,
                                                'mark': result.marks,
                                                'status': result.status,
                                                'exam_weight': result.grade_weightage,
                                            }
                                        )

                                val = {
                                    'subject': subject,
                                    'latter_grade': latter_grade,
                                    'gpa': gpa,
                                    'grade': grade,
                                    'exam_detail': exam_details,
                                }
                                semester_result_line_data.append(val)
                    response = {
                        'semester': semester,
                        'status': status,
                        'total_gpa': total_gpa,
                        'grade_detail': semester_result_line_data,
                    }
            else:
                domain = [('student_id', '=', student.id), ('semester_mark_sheet_id.state', '=', 'validated')]
                semester_result_data = []
                semester_results = request.env['pm.semester.result'].sudo().search(domain)
                if semester_results:
                    for semester_result in semester_results:
                        semester_result_id = semester_result.id
                        semester = semester_result.semester_id.name
                        status = semester_result.status
                        gpa = semester_result.gpa
                        val = {
                            'id': semester_result_id,
                            'semester': semester,
                            'state': status,
                            'gpa': gpa,
                        }
                        semester_result_data.append(val)
                    response = {
                            'data': semester_result_data,
                    }
        return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/v1/student/grade/interpretation',
                auth="user", type='http', token=None, methods=['GET'], csrf=False)
    def get_grade_interpretation(self, token=None, **kw):
        check_params({'token': token})
        check_token()
        student = Student.get_student(self)
        response = {}
        if student:
            domain = []
            grade_interpretation_data = []
            grade_interpretations = request.env['op.grade.configuration'].sudo().search(domain)
            if grade_interpretations:
                for grade_interpretation in grade_interpretations:
                    val = {
                        'grade_letter': grade_interpretation.result,
                        'grade': str(grade_interpretation.min_per) + '-' + str(grade_interpretation.max_per),
                        'gpa': grade_interpretation.grade_point,
                    }
                    grade_interpretation_data.append(val)
                response = {
                    'data': grade_interpretation_data,
                }
        return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/v1/student/internship',
                auth="user", type='http', token=None, methods=['GET'], csrf=False)
    def get_internship(self, token=None, **kw):
        check_params({'token': token})
        check_token()
        student = Student.get_student(self)
        response = {}
        if student:
            self.clear_notification('internship', student.id)
            domain = [('student_id', '=', student.id), ('state', '=', 'join')]
            internship_data = []
            internships = request.env['op.placement.offer'].sudo().search(domain)
            if internships:
                location = ''
                for internship in internships:
                    company_name = internship.name
                    country = internship.p_country_id.name
                    state = internship.p_state_id.name
                    status = internship.state
                    is_completed = internship.p_completed
                    if is_completed is not True:
                        status = 'completed'
                    semester = internship.semester_id.name
                    if country and state:
                        location = state + ', ' + country
                    elif country and state is None:
                        location = country
                    elif country is None and state:
                        location = country
                    elif country is None and state is None:
                        location = country
                    start_date = internship.join_date
                    end_date = internship.p_end_date
                    absent_hours = internship.p_absences
                    contact_person = internship.p_contact1.name
                    contact_phone = internship.p_contact1.phone
                    position = internship.p_contact1.function
                    portfolio = internship.p_portfolio
                    email = internship.p_contact1.email
                    project1_deadline = internship.p_project1_deadline
                    project2_deadline = internship.p_project2_deadline
                    val = {
                        'company_name': company_name,
                        'semester': semester,
                        'contact_person': contact_person,
                        'contact_phone': contact_phone,
                        'position': position,
                        'email': email,
                        'location': location,
                        'status': status,
                        'start_at': start_date,
                        'end_at': end_date,
                        'absent_hours': absent_hours,
                        'project1_deadline': project1_deadline,
                        'project2_deadline': project2_deadline,
                        'portfolio_score': portfolio,
                    }
                    internship_data.append(val)
                response = {
                    'data': internship_data,
                }
        return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/v1/student/class',
                auth="user", type='http', day_name=None, check_date=None, token=None, methods=['GET'], csrf=False)
    def get_class_schedule(self, day_name=None, check_date=None, token=None, **kw):
        check_params({'token': token})
        check_token()
        student = Student.get_student(self)
        response = {}
        if student:
            self.clear_notification('class_schedule', student.id)
            session_in_monday = []
            session_in_tuesday = []
            session_in_wednesday = []
            session_in_thursday = []
            session_in_friday = []
            session_in_saturday = []
            session_in_sunday = []
            today = datetime.today()
            monday = today - timedelta(days=today.weekday())
            sunday = monday + timedelta(days=6)
            if check_date:
                check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
                monday = check_date + timedelta(days=-check_date.weekday())
                sunday = monday + timedelta(days=6)
                print(monday)
                print(sunday)
            domain = [('batch_id', '=', int(student.batch_id)), ('classroom_id', 'in', student.course_detail_ids.class_ids.ids),
                      ('start_datetime', '>=', monday), ('start_datetime', '<=', sunday)]
            print(domain)
            sessions = request.env['op.session'].sudo().search(domain, order='start_datetime')
            print(sessions)
            display_date = monday.strftime('%d, %b %Y') + ' - ' + sunday.strftime('%d, %b %Y')
            response = {
                'display_date': display_date,
                'Monday': session_in_monday,
                'Tuesday': session_in_tuesday,
                'Wednesday': session_in_wednesday,
                'Thursday': session_in_thursday,
                'Friday': session_in_friday,
                'Saturday': session_in_saturday,
                'Sunday': session_in_sunday,
            }
            if sessions:
                for session in sessions:
                    subject = session.subject_id.name
                    duration = session.timing_id.name
                    class_room = session.classroom_id.code
                    professor = session.faculty_id.name
                    start_date = session.start_datetime.astimezone(pytz.timezone("Asia/Phnom_Penh"))
                    end_date = session.end_datetime.astimezone(pytz.timezone("Asia/Phnom_Penh"))
                    start_time = start_date.strftime('%I:%M %p')
                    end_time = end_date.strftime('%I:%M %p')
                    day_name = session.type
                    display_date = monday.strftime('%d, %b %Y') + ' - ' + sunday.strftime('%d, %b %Y')
                    val = {
                        'subject': subject,
                        'professor': professor,
                        'classroom': class_room,
                        'date': start_date.date(),
                        'time': str(start_time) + ' - ' + str(end_time),
                        'duration': duration
                    }
                    if day_name == '0':
                        session_in_monday.append(val)
                    if day_name == '1':
                        session_in_tuesday.append(val)
                    if day_name == '2':
                        session_in_wednesday.append(val)
                    if day_name == '3':
                        session_in_thursday.append(val)
                    if day_name == '4':
                        session_in_friday.append(val)
                    if day_name == '5':
                        session_in_saturday.append(val)
                    if day_name == '6':
                        session_in_sunday.append(val)
                response = {
                    'display_date': display_date,
                    'Monday': session_in_monday,
                    'Tuesday': session_in_tuesday,
                    'Wednesday': session_in_wednesday,
                    'Thursday': session_in_thursday,
                    'Friday': session_in_friday,
                    'Saturday': session_in_saturday,
                    'Sunday': session_in_sunday,
                }
        return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/v1/student/payment',
                auth="user", type='http', token=None, methods=['GET'], csrf=False)
    def get_payment_schedule(self, token=None, **kw):
        check_params({'token': token})
        check_token()
        student = Student.get_student(self)
        response = {}
        if student:
            domain = [('student_id', '=', student.id), ('state', '!=', 'cancel')]
            self.clear_notification('payment_schedule', student.id)
            today = datetime.today().date()
            payment_data = []
            payments = request.env['op.student.fees.details'].sudo().search(domain, order='date')
            print(payments)
            if payments:
                for payment in payments:
                    invoice_state = payment.invoice_id.state
                    payment_option = payment.payment_option
                    if payment.state in ['invoice', 'installment'] and invoice_state != 'posted':
                        if payment_option == 'installment':
                            for installment in payment.installments:
                                payment_id = payment.id
                                payment_date = installment.due_date
                                amount = installment.amount
                                state = installment.state
                                expired = (payment_date - today).days
                                reminding = ''
                                if expired > 0:
                                    reminding = 'due in ' + str(expired) + ' days'
                                elif expired == 0:
                                    reminding = 'today'
                                else:
                                    reminding = 'late ' + str(abs(expired)) + ' days'
                                val = {
                                    'id': installment.id,
                                    'payment_date': payment_date,
                                    'amount': amount,
                                    'state': state,
                                    'invoice_state': installment.invoice_state,
                                    'reminding': reminding,
                                    'type': payment_option
                                }
                                payment_data.append(val)
                        elif payment_option == 'normal':
                            payment_id = payment.id
                            payment_date = payment.date
                            expired = (payment_date - today).days
                            amount = payment.amount
                            state = payment.state
                            invoice_id = payment.invoice_id.id

                            print(expired)
                            reminding = ''
                            if expired > 0:
                                reminding = 'due in ' + str(expired) + ' days'
                            elif expired == 0:
                                reminding = 'today'
                            else:
                                reminding = 'late ' + str(abs(expired)) + ' days'
                            val = {
                                'id': payment_id,
                                'payment_date': payment_date,
                                'amount': amount,
                                'state': state,
                                'invoice_state': invoice_state,
                                'reminding': reminding,
                                'type': payment_option
                            }
                            payment_data.append(val)
                    response = {
                        'data': payment_data,
                    }
        return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/v1/student/payment/history',
                auth="user", type='http', token=None, methods=['GET'], csrf=False)
    def get_payment_history(self, token=None, **kw):
        check_params({'token': token})
        check_token()
        student = Student.get_student(self)
        response = {}
        if student:
            domain = [('student_id', '=', student.id), ('invoice_id.state', '=', 'posted')]
            payment_data = []
            payments = request.env['op.student.fees.details'].sudo().search(domain, order='date')
            if payments:
                for payment in payments:
                    payment_id = payment.id
                    payment_date = payment.invoice_id.date
                    amount = payment.amount
                    state = payment.state
                    invoice_state = payment.invoice_id.state
                    val = {
                        'id': payment_id,
                        'payment_date': payment_date,
                        'amount': amount,
                        'state': state,
                        'invoice_state': invoice_state
                    }
                    payment_data.append(val)
                response = {
                    'data': payment_data,
                }
        return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route(['/api/v1/password/reset'],
                auth="none", type='http', token=None, methods=['POST'], csrf=False)
    def password_reset(self, login=None, **kw):
        check_params({'login': login})

        user = request.env['res.users'].sudo().search([('login', '=', login)])

        if not user:
            user = request.env['res.users'].sudo().search([('email', '=', login)])
        if len(user) != 1:
            response = {
                'error': 'user not found',
            }
            return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=404)
        try:
            user.action_reset_password()
        except Exception as error:
            _logger.error(error)
        response = {
            'message': 'An email has been sent with credentials to reset your password',
        }
        return Response(json.dumps(response, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)
