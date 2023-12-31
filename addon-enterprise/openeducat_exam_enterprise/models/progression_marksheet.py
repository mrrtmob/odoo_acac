# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api


class StudentProgression(models.Model):
    _inherit = ["op.student.progression"]

    @api.depends("marksheet_lines")
    def _compute_calculate_total_marksheet_line(self):
        self.total_marksheet_line = len(self.marksheet_lines)

    marksheet_lines = fields.One2many(
        'op.marksheet.line',
        'progression_id',
        string='Progression Marksheet')
    total_marksheet_line = fields.Integer(
        'Total Marksheet',
        compute="_compute_calculate_total_marksheet_line",
        store=True)
