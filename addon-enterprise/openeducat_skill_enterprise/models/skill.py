# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields


class Opskill(models.Model):
    _name = "op.skill"
    _description = "Skills Creation"

    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('Code', size=64, required=True)
    skill_category_type_id = fields.Many2one(
        'op.skill.category', string='Skill Type', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)


class Opskillline(models.Model):
    _name = "op.skill.line"
    _description = "Skill Lines Creation Creation"

    skill_type_id = fields.Many2one('op.skill', string='Skill', required=True)
    student_id = fields.Many2one('op.student', string='student')
    rating = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')], 'Rating', default='1', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)


class OpStudent(models.Model):
    _inherit = "op.student"

    skill_line = fields.One2many(
        'op.skill.line', 'student_id', 'Skills Details')
    skill_count = fields.Integer(compute='_compute_count_skill')

    def get_skill(self):
        action = self.env.ref('openeducat_skill_enterprise.'
                              'act_open_op_skill_line_view').read()[0]
        action['domain'] = [('student_id', 'in', self.ids)]
        return action

    def _compute_count_skill(self):
        for record in self:
            record.skill_count = self.env['op.skill.line'].search_count(
                [('student_id', 'in', self.ids)])
