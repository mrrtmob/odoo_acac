# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################


from odoo import models, fields, api


class ProgressMarksheetWiz(models.TransientModel):
    """ Progression Marksheet """
    _name = "marksheet.line.progress.wizard"
    _description = "Marksheet line Progress Wizard"

    @api.model
    def _get_default_student(self):
        ctx = self._context
        if ctx.get('active_model') == 'op.student.progression':
            obj = self.env['op.student.progression'].\
                browse(ctx.get('active_ids')[0])
            return obj.student_id

    student_id = fields.Many2one('op.student',
                                 string="Student Name",
                                 default=_get_default_student)
    marksheet_ids = fields.Many2many('op.marksheet.line',
                                     string='Marksheet')

    def Add_marksheet_line(self):
        core = self.env['op.student.progression'].\
            browse(self.env.context['active_ids'])
        for i in core:
            i.marksheet_lines = self.marksheet_ids
