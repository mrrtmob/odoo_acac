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

    @api.depends("discipline_lines")
    def _compute_total_discipline(self):
        self.total_discipline = len(self.discipline_lines)

    discipline_lines = fields.One2many('op.discipline',
                                       'progression_id',
                                       string='Progression Discipline')
    total_discipline = fields.Integer('Total Discipline',
                                      compute="_compute_total_discipline",
                                      store=True)
