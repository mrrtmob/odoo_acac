from odoo import models, api
from datetime import timedelta, date,datetime 
from dateutil.relativedelta import relativedelta

class RegistrarDashboard(models.AbstractModel):
    _name = 'registrar.dashboard'

    @api.model
    def get_student_enrollment(self):
        students = self.env['op.student']
        # horizontal barchart
        cambodian_students = students.search_count([('nationality.name', '=', 'Cambodian')])
        foreigners_students = students.search_count([('nationality.name', '!=', 'Cambodian')])
        scholarship_students = students.search_count([('is_scholarship', '=', 't')])
        h_barchart_data = {
            'cambodian': cambodian_students,
            'foreigners': foreigners_students,
            'scholarship': scholarship_students
        }

        data = {
            # 'students_by_gender': students_by_gender,
            'h_barchart_data': h_barchart_data
        }
        return data

    @api.model
    def get_student_graduated(self):
        students = self.env['op.student']

        # total
        total_graduated = students.search_count([('education_status', '=', 'graduated')])
        total_postponed = students.search_count([('education_status', '=', 'postponed')])
        total_dropout = students.search_count([('education_status', '=', 'withdrawn')])

        # current semester
        students = self.env['op.student']
        total_active = students.search_count([('education_status', '=', 'active')])
        if total_active + total_graduated > 0:
            retention_rate = ((total_active + total_graduated) / students.search_count([])) * 100
        else:
            retention_rate = 0

        # student by gender
        male_students = students.search_count([('gender', '=', 'm')])
        female_students = students.search_count([('gender', '=', 'f')])
        students_by_gender = {
            'males': male_students,
            'females': female_students
        }

        # semester = self.env['']

        data = {
            'total': {
                'graduated': total_graduated,
                'postponed': total_postponed,
                'dropout': total_dropout
            },
            'retention_rate':  "{:.2f}".format(retention_rate),
            'students_by_gender': students_by_gender
        }
        return data

    @api.model
    def get_term_semesters_absence_data(self):
        current_term = self.env['op.batch'].search([('state' , '=' , 'active')], order='start_date desc', limit=1)
        current_term_semesters = self.env['pm.semester'].search(
            [('batch_id', '=', current_term.id)],
            order='semester_order asc'
        )

        result = {
            'semesters': []
        }

        for current_term_semester in current_term_semesters:
            week_start_date = current_term_semester.start_date
            weeks = []
            w = 1

            while week_start_date < current_term_semester.end_date:
                week_end_date = week_start_date + timedelta(weeks=1)

                semester_weekly_absences_count = self.env['op.attendance.line'].search_count(
                    [('semester_id', '=', current_term_semester.id),
                     ('attendance_date', '>=', week_start_date),
                     ('attendance_date', '<', week_end_date),
                     ('present', '=', False)]
                )

                weeks.append({
                    'label': "W%d" % w,
                    'start_date': week_start_date,
                    'end_date': week_end_date,
                    'absences_count': semester_weekly_absences_count
                })

                week_start_date = week_end_date
                w += 1

            semester = {
                'id': current_term_semester.id,
                'name': current_term_semester.name,
                'start_date': current_term_semester.start_date,
                'end_date': current_term_semester.end_date,
                'weeks': weeks
            }

            result['semesters'].append(semester)

        return result

    @api.model
    def get_term_grade_data(self):
        current_term = self.env['op.batch'].search([('state' , '=' , 'active')], order='start_date desc', limit=1)
        current_term_semesters = self.env['pm.semester'].search(
            [('batch_id', '=', current_term.id)],
            order='semester_order asc'
        )

        result = {
            'semesters': []
        }

        for current_term_semester in current_term_semesters:
            semester_marksheet = self.env['pm.semester.marksheet.register'].search(
                [('semester_id', '=', current_term_semester.id)],
                order='generated_date desc',
                limit=1
            )

            semester_result = {
                'id': current_term_semester.id,
                'name': current_term_semester.name
            }

            if semester_marksheet:
                semester_result['rank_low'] = semester_marksheet.rank_low
                semester_result['rank_middle'] = semester_marksheet.rank_middle
                semester_result['rank_top'] = semester_marksheet.rank_top
            else:
                semester_result['rank_low'] = 0
                semester_result['rank_middle'] = 0
                semester_result['rank_top'] = 0

                semester_internships = self.env['op.placement.offer'].search(
                    [('semester_id', '=', current_term_semester.id)]
                )
                semester_internships_count = len(semester_internships)

                if semester_internships_count > 0:
                    rank_low_count = 0
                    rank_middle_count = 0
                    rank_top_count = 0

                    for semester_internship in semester_internships:
                        if semester_internship.p_grade < 60:
                            rank_low_count += 1
                        elif semester_internship.p_grade > 80:
                            rank_top_count += 1
                        else:
                            rank_middle_count += 1

                    semester_result['rank_low'] = rank_low_count / semester_internships_count * 100
                    semester_result['rank_middle'] = rank_middle_count / semester_internships_count * 100
                    semester_result['rank_top'] = rank_top_count / semester_internships_count * 100

            result['semesters'].append(semester_result)

        # NOTE: for debugging purpose
        print('=== get_term_grade_data ===')
        print(result)

        return result

    @api.model
    def get_current_semester_students_data(self):
       
        current_term = self.env['op.batch'].search([], order='create_date desc', limit=1)
        current_semester = self.env['pm.semester'].search(
            [('batch_id', '=', current_term.id), ('state', '=', 'active')],
            order='semester_order asc',
            limit=1
        )

        current_semester_students = self.env['op.student'].search(
            [('student_semester_detail.semester_id', '=', current_semester.id), ('student_semester_detail.state', 'in', ['ongoing', 'complete'])]
        )

        students_count = len(current_semester_students)
        male_students_count = len(current_semester_students.filtered(lambda r: r.gender == 'm'))
        female_students_count = len(current_semester_students.filtered(lambda r: r.gender == 'f'))
        scholarship_students_count = len(current_semester_students.filtered('is_scholarship'))
        graduated_students_count = len(current_semester_students.filtered(lambda r: r.education_status == 'graduated'))
        postponed_students_count = len(current_semester_students.filtered(lambda r: r.education_status == 'postponed'))
        withdrawn_students_count = len(current_semester_students.filtered(lambda r: r.education_status == 'withdrawn'))
        
        result = {
            'students_count': students_count,
            'male_students_count': male_students_count,
            'female_students_count': female_students_count,
            'scholarship_students_count': scholarship_students_count,
            'graduated_students_count': graduated_students_count,
            'postponed_students_count': postponed_students_count,
            'withdrawn_students_count': withdrawn_students_count
        }

        # NOTE: for debugging purpose
        print('=== get_current_semester_students_data ===')
        return result

    @api.model 
    def get_active_terms(self):
        result = {
            'terms': [],
            'totals': 0,
            'retention_rate': 0,
            'male': 0,
            'female': 0,
            'current_term' : '',
            'attendance': {
                'first_warning': 0,
                'second_warning': 0
            },
            'discipline': {
                'first_warning': 0,
                'second_warning': 0
            },
            'overdue_payment': 0,
            'alerts': []
        }
        active_terms = self.env['op.batch'].search([('state' , '=' , 'active')] , order='start_date desc')
        #current terms, semester
        if len(active_terms): 
            cbatch = active_terms[0]
            result['current_term'] = cbatch.name 
            result['attendance']['first_warning'] = self.env['pm.semester.attendance'].search_count(
                [('semester_id.batch_id', '=', cbatch.id), ('semester_id.state', '=', 'active'), ('state', '=', 'first_warning')]
            )
            result['attendance']['second_warning'] = self.env['pm.semester.attendance'].search_count(
                [('semester_id.batch_id', '=', cbatch.id), ('semester_id.state', '=', 'active'), ('state', '=', 'second_warning')]
            )
            result['discipline']['first_warning'] = self.env['pm.student.discipline'].search_count(
                [('semester_id.batch_id', '=', cbatch.id), ('semester_id.state', '=', 'active'), ('state', '=', 'first_warning')]
            )
            result['discipline']['second_warning'] = self.env['pm.student.discipline'].search_count(
                [('semester_id.batch_id', '=', cbatch.id), ('semester_id.state', '=', 'active'), ('state', '=', 'second_warning')]
            )

            result['overdue_payment'] = self.env['op.student.fees.details'].search_count(
                [('state', '=', 'invoice'), ('invoice_id', '=', False), ('date', '<', date.today())]
            )
             
            current_term_last_semester = self.env['pm.semester'].search(
                [('batch_id', '=', cbatch.id)],
                order='semester_order desc',
                limit=1
            )
            result['graduates'] = self.env['pm.student.semester.detail'].search_count(
                [('semester_id', '=', current_term_last_semester.id), ('state', 'in', ['ongoing', 'complete'])]
            )
            csemester = self.env['pm.semester'].search(
                [('batch_id', '=', cbatch.id) , ('state', '=' , 'active')],
                order='semester_order desc', limit=1
            )
             
            today = date.today()
            ed = date(cbatch.end_date.year, cbatch.end_date.month, cbatch.end_date.day)
            em = date(csemester.end_date.year, csemester.end_date.month, csemester.end_date.day)
            if cbatch.end_date < today: 
                term_end_alert = 'Term ' + cbatch.name + ' was supposed to end since ' + str(cbatch.end_date.strftime('%d/%m/%Y'))
                result['alerts'].append(term_end_alert)
            elif (ed - today).days <= 30:
                term_end_alert = 'Term ' + cbatch.name + ' is going to end in ' + str(cbatch.end_date.strftime('%d/%m/%Y'))
                result['alerts'].append(term_end_alert)

            if csemester.end_date < today:
                term_end_alert = 'Term ' + cbatch.name + ' ' + csemester.name + ' was supposed to end since ' + str(csemester.end_date.strftime('%d/%m/%Y'))
                result['alerts'].append(term_end_alert)
            elif (em - today).days <= 30: 
                term_end_alert = 'Term ' + cbatch.name + ' ' + csemester.name + ' is going to end in ' + str(csemester.end_date.strftime('%d/%m/%Y'))
                result['alerts'].append(term_end_alert)
            
        #all student data 
        students = self.env['op.student']
        total_graduated = students.search_count([('education_status', '=', 'graduated')])
        total_active = students.search_count([('education_status', '=', 'active')])

        if total_active + total_graduated > 0:
            rate = ((total_active + total_graduated) / students.search_count([])) * 100
            result['retention_date'] = "{:.2f}".format(round(rate, 2))
        else:
            result['retention_date'] = 0

        result['male'] = students.search_count([('gender', '=', 'm')]) 
        result['female'] = students.search_count([('gender', '=', 'f')]) 
        result['postponed'] = students.search_count([('education_status', '=', 'postponed')])
        result['dropout'] = students.search_count(['|',('education_status', '=', 'withdrawn') , ('education_status', '=', 'dismissed') ])
        result['graduated'] = total_graduated

        for at in active_terms:
            semester = self.env['pm.semester'].search(
                [('batch_id', '=', at.id) , ('state', '=' , 'active')],
                order='semester_order desc', limit=1
            )
            active = self.env['op.student'].search_count([('course_detail_ids.batch_id', '=', at.id) , ('course_detail_ids.education_status' , '=', 'active')])
            postponed = self.env['op.student'].search_count([('course_detail_ids.batch_id', '=', at.id) , ('course_detail_ids.education_status' , '=', 'postponed')])
            withdrawn = self.env['op.student'].search_count([('course_detail_ids.batch_id', '=', at.id) , ('course_detail_ids.education_status' , '=', 'withdrawn')])
            dismissed = self.env['op.student'].search_count([('course_detail_ids.batch_id', '=', at.id) , ('course_detail_ids.education_status' , '=', 'dismissed')])
            female = self.env['op.student'].search_count([('course_detail_ids.batch_id', '=', at.id) , ('gender' , '=', 'f')])
            male = self.env['op.student'].search_count([('course_detail_ids.batch_id', '=', at.id) , ('gender' , '=', 'm')])
            scholarship = self.env['op.student'].search_count([('course_detail_ids.batch_id', '=', at.id) , ('is_scholarship' , '=', True)])
            # ('course_detail_ids.batch_id','in',[active_id]),('course_detail_ids.education_status','in',['postponed'])
            obj = {
                'name': at.name,
                'code': at.code,
                'state': at.state,
                'semester': semester[0].name,
                'postponed': postponed,
                'dropout': withdrawn + dismissed,
                'active': active,
                'female': female,
                'male': male,
                'scholarship': scholarship
            }
            result['terms'].append(obj)

        return result

    @api.model
    def get_current_term_enrollment_data(self):
        current_term = self.env['op.batch'].search([('state' , '=' , 'active')], order='start_date desc', limit=1)
        current_term_semesters = self.env['pm.semester'].search(
            [('batch_id', '=', current_term.id), ('state', '=' , 'active')],
            order='semester_order asc'
        )

        result = {
            'semesters': []
        }

        for current_term_semester in current_term_semesters:
            semester = {
                'id': current_term_semester.id,
                'name': current_term_semester.name
            }

            semester_students = self.env['op.student'].search(
                [('student_semester_detail.semester_id', '=', current_term_semester.id),
                 ('student_semester_detail.state', 'in', ['ongoing', 'complete'])]
            )

            students_count = len(semester_students)
            male_students_count = len(semester_students.filtered(lambda r: r.gender == 'm'))
            female_students_count = len(semester_students.filtered(lambda r: r.gender == 'f'))
            scholarship_students_count = len(semester_students.filtered('is_scholarship'))

            semester['students_count'] = students_count
            semester['male_students_count'] = male_students_count
            semester['female_students_count'] = female_students_count
            semester['scholarship_students_count'] = scholarship_students_count

            result['semesters'].append(semester)

        # NOTE: for debugging purpose
        print('=== get_current_term_enrollment_data ===')
        print(result)

        return result

    @api.model
    def get_current_term_alert_data(self):
        current_term = self.env['op.batch'].search([], order='create_date desc', limit=1)

        current_term_first_warning_attendances_count = self.env['pm.semester.attendance'].search_count(
            [('semester_id.batch_id', '=', current_term.id), ('state', '=', 'first_warning')]
        )
        current_term_second_warning_attendances_count = self.env['pm.semester.attendance'].search_count(
            [('semester_id.batch_id', '=', current_term.id), ('state', '=', 'second_warning')]
        )

        current_term_first_warning_disciplines_count = self.env['pm.student.discipline'].search_count(
            [('semester_id.batch_id', '=', current_term.id), ('state', '=', 'first_warning')]
        )
        current_term_second_warning_disciplines_count = self.env['pm.student.discipline'].search_count(
            [('semester_id.batch_id', '=', current_term.id), ('state', '=', 'second_warning')]
        )

        overdue_payments_count = self.env['op.student.fees.details'].search_count(
            [('state', '=', 'invoice'), ('invoice_id', '=', False), ('date', '<', date.today())]
        )

        current_term_last_semester = self.env['pm.semester'].search(
            [('batch_id', '=', current_term.id)],
            order='semester_order desc',
            limit=1
        )
        current_term_last_semester_students_count = self.env['pm.student.semester.detail'].search_count(
            [('semester_id', '=', current_term_last_semester.id), ('state', 'in', ['ongoing', 'complete'])]
        )

        result = {
            'first_warning_attendances_count': current_term_first_warning_attendances_count,
            'second_warning_attendances_count': current_term_second_warning_attendances_count,
            'first_warning_disciplines_count': current_term_first_warning_disciplines_count,
            'second_warning_disciplines_count': current_term_second_warning_disciplines_count,
            'overdue_payments_count': overdue_payments_count,
            'last_semester_students_count': current_term_last_semester_students_count,
        }

        # NOTE: for debugging purpose
        print('=== get_current_term_alert_data ===')
        print(result)

        return result
