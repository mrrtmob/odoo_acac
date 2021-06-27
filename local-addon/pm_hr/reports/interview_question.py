from odoo import fields, models, api
from datetime import datetime
import time


class ModelName(models.AbstractModel):
    _name = "report.pm_hr.interview_question_report"
    _description = 'Description'

    def _get_interviewer_name(self, users):
        users_name = ''
        for user in users:
            if users_name:
                users_name = users_name + '/ ' + user['name']
            else:
                users_name = user['name']
        return users_name

    def _get_interview_question_list(self, questions):
        score = [i for i in questions if i['score']]
        no_score = [i for i in questions if not i['score']]
        return score + no_score


    @api.model
    def _get_report_values(self, docids, data=None):
        applicant = self.env['hr.applicant'].browse(docids)
        users = applicant['interviewer']
        
        questions = applicant['question_ids']
        #sorted_questions = sorted(questions, key=lambda x: x['sequence'])
        #print('interview_question: ', applicant['question_ids'])
        #print('interview_question_id: ', applicant['question_ids']['interview_question_id'])
        #print('questions : ', sorted_questions)
        basic_questions = applicant['administrative_ids']
        #basic_questions = sorted(basic_questions, key=lambda x: x['sequence'])

        personality_question = applicant['personality_ids']
        #personality_question = sorted(personality_question, key=lambda x: x['sequence'])

        motivation_question = applicant['motivation_ids']
        #motivation_question = sorted(motivation_question, key=lambda x: x['sequence'])
        job = applicant.job_id
        
        docargs = {
            'doc_ids': self.ids,
            # 'doc_model': model,
            # 'docs': docs,
            'time': time,
            'current_date': datetime.today(),
            'applicant': applicant,
            'interview_name': self._get_interviewer_name(users),
            # 'interview_questions': self._get_interview_question_list(questions),
            'interview_questions': questions,
            'basic_questions': basic_questions,
            'personality_question': personality_question,
            'motivation_question': motivation_question,
            'technical_weight': job['technical_weight'],
            'personality_weight': job['personality_weight'],
            'motivation_weight': job['motivation_weight'],
            'basic_weight': job['basic_weight']
        }
        print("I am here")
        print(docargs)
        return docargs
