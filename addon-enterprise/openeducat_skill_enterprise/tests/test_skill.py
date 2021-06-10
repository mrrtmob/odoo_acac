# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

import logging

from .test_skill_common import TestSkillCommon


class TestSkill(TestSkillCommon):

    def setUp(self):
        super(TestSkill, self).setUp()

    def test_case_skill(self):
        types = self.op_skill.search([])
        for skill in types:
            logging.info('Name : %s' % skill.name)
            logging.info('code : %s' % skill.code)
            logging.info('Skill Category : %s'
                         % skill.skill_category_type_id.name)


class TestSkillCategory(TestSkillCommon):

    def setUp(self):
        super(TestSkillCategory, self).setUp()

    def test_case_skill_category(self):
        types = self.op_skill_category.search([])
        for skill_category in types:
            logging.info('Name : %s' % skill_category.name)
            logging.info('code : %s' % skill_category.code)


class TestSkillLine(TestSkillCommon):

    def setUp(self):
        super(TestSkillLine, self).setUp()

    def test_case_skill_line(self):
        types = self.op_skill_line.search([])
        for skill_line in types:
            logging.info('Skill Type : %s' % skill_line.skill_type_id.name)
            logging.info('Name : %s' % skill_line.student_id.name)
            logging.info('Ratings : %s' % skill_line.rating)
