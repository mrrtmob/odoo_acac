# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PmInterviewQuestion(models.Model):
    _name = 'pm.interview.question'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    name = fields.Text(required=True, string='Question')
    point = fields.Float()
    read_only = fields.Boolean(compute="compute_read_only", default=True)
    department_id = fields.Many2one('hr.department', 'Department')
    is_hr_user = fields.Boolean('Approver', compute="compute_is_hr_user", readonly=True, default=False)
    job_position_id = fields.Many2one('hr.job', 'Job Position',
                                      domain="[('department_id', '=', department_id)]")

    def compute_is_hr_user(self):
        self.is_hr_user = False
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr_recruitment.group_hr_recruitment_manager'):
            self.is_hr_user = True

    @api.depends('is_hr_user')
    def compute_read_only(self):
        self.read_only = True
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr_recruitment.group_hr_recruitment_manager'):
            self.read_only = False

    @api.model
    def get_default_type(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr_recruitment.group_hr_recruitment_manager'):
            return 'basic'
        else:
            return 'technical'

    type = fields.Selection([
        ('basic', 'Basic/Administrative'),
        ('technical', 'Specific Functional'),
        ('personality', 'Characteristic/Personality'),
        ('motivation', 'Motivational/Working Related'),
    ], string='Question Type', track_visibility="onchange")
    expected_answer = fields.Html('Scoring Criteria', track_visibility="onchange")
    question_weight = fields.Float('Weight')
    no_scoring = fields.Boolean('No Scoring',track_visibility="onchange")

    @api.onchange('department_id')
    def onchange_department(self):
        self.job_position_id = False

    @api.onchange('no_scoring')
    def onchange_department(self):
        self.point = 0

