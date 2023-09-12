from odoo import fields, models, api
from datetime import datetime
import time


class ModelName(models.Model):
    _name = "report.pm_hr.interview_question_jop_position_report"
    _description = 'Description'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('docids: ', docids)
        job = self.env['hr.job'].browse(docids)
        questions = job['question_ids']
        #sorted_questions = sorted(questions, key=lambda x: x['sequence'])
        print('job: ', job)
        print('question_ids: ', job['question_ids'])
        # users = applicant['interviewer']
        # questions = applicant['question_ids']
        # sorted_questions = sorted(questions, key=lambda x: x['sequence'])
        # print('interview_question: ', applicant['question_ids'])
        # print('interview_question_id: ', applicant['question_ids']['interview_question_id'])
        # print('questions : ', sorted_questions)
        basic_questions = job['basic_question_ids']
        #basic_questions = sorted(basic_questions, key=lambda x: x['sequence'])

        personality_question = job['personality_question_ids']
        #personality_question = sorted(personality_question, key=lambda x: x['sequence'])

        motivation_question = job['motivation_question_ids']
        #motivation_question = sorted(motivation_question, key=lambda x: x['sequence'])

        docargs = {
            'doc_ids': self.ids,
            'time': time,
            'current_date': datetime.today(),
            'job': job,
            # 'interview_name': self._get_interviewer_name(users),
            'interview_questions': questions,
            'basic_questions': basic_questions,
            'personality_question': personality_question,
            'motivation_question': motivation_question,
            'technical_weight': job['technical_weight'],
            'personality_weight': job['personality_weight'],
            'motivation_weight': job['motivation_weight'],
            'basic_weight': job['basic_weight']
        }
        return docargs
