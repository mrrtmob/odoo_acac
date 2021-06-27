# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from logging import info
import time

from .test_discipline_common import TestDisciplineCommon


class TestDiscipline(TestDisciplineCommon):

    def setUp(self):
        super(TestDiscipline, self).setUp()

    def test_case_discipline_1(self):
        discipline = self.op_discipline.search([])
        if not discipline:
            raise AssertionError(
                'Error in data, please check for reference ')
        for record in discipline:
            info('      Progression No : %s' % record.progression_id.name)
            info('      Student : %s' % record.student_id.name)
            info('      Misbehaviour Category  : %s' %
                 record.misbehaviour_category_id.name)
            info('      Misbehaviour Type : %s' % record.misbehaviour_type)
            info('      Meeting Date Time : %s' % record.meeting_datetime)
            info('      Company : %s' % record.company_id.name)
            record._compute_get_student_class()
            record.onchange_student_discipline_progrssion()
            record.check_dates()
            record.send_email()
            record.submit_apology_letter()
            record.apologies_letter()
            record.meeting_awaiting()


class TestMisbehaveCategory(TestDisciplineCommon):

    def setUp(self):
        super(TestMisbehaveCategory, self).setUp()

    def test_case_1_misbehave_category_1(self):
        misbehave = self.op_misbehave_category.search([])
        misbehave_category = self.op_misbehave_category.create({
            'name': "Cheat in exam",
            'misbehaviour_type': 'major',
            'misbehaviour_template_id':
                self.env.ref('openeducat_discipline.'
                             'email_cheating_in_the_exam_template').id
        })
        return misbehave
        return misbehave_category


class TestMailComposeMessage(TestDisciplineCommon):

    def setUp(self):
        super(TestMailComposeMessage, self).setUp()

    def test_case_1_test_mail_compose_message(self):
        mail_compose = self.op_mail_compose_message
        mail_compose.send_mail()


class TestElearningRules(TestDisciplineCommon):

    def setUp(self):
        super(TestElearningRules, self).setUp()

    def test_case_1_elearning(self):
        elearning = self.op_elearning_rule.create({
            'id': 1,
            'name': "rule 1",
            'rules_action': "suspend for 4 days"
        })
        if not elearning:
            raise AssertionError(
                'Error in data, please check for Assets')


class TestStudentWiseWizard(TestDisciplineCommon):

    def setUp(self):
        super(TestStudentWiseWizard, self).setUp()

    def test_case_1_student_wise_wizard(self):
        student_wise = self.op_student_wise_wizard.create({
            'student_id': self.env.ref('openeducat_core.op_student_1').id,
        })
        student_wise.print_report()


class TestMisbehaviourTypeWizard(TestDisciplineCommon):

    def setUp(self):
        super(TestMisbehaviourTypeWizard, self).setUp()

    def test_case_1_misbehaviour_type_wizard(self):
        misbehave_type = self.op_misbehaviour_type_wizard.create({
            'misbehaviour_type': 'minor',
        })
        misbehave_type.print_report()


class TestTakeActionWizard(TestDisciplineCommon):

    def setUp(self):
        super(TestTakeActionWizard, self).setUp()

    def test_case_1_take_action_wizard(self):
        take_action1 = self.op_take_action_wizard.create({
            'discipline_id': self.env.ref('openeducat_core.op_student_1').id,
            'suspend': True,
            'suspend_from_date': time.strftime('%Y-%m-01'),
            "suspend_to_date": time.strftime('%Y-%m-01'),
        })
        take_action1.take_action()


class TestProgressionWizard(TestDisciplineCommon):

    def setUp(self):
        super(TestProgressionWizard, self).setUp()

    def test_case_1_progression_wizard(self):
        progression = self.op_progression_wizard.create({
            'student_id': self.env.ref('openeducat_core.op_student_1').id,
        })
        progression._get_default_student()
