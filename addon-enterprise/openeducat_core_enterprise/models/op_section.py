# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################
from odoo import models, fields


class OpSection(models.Model):
    _name = "op.section"
    _description = "Section"

    name = fields.Char(string='Name', required=True)
    course_ids = fields.Many2many('op.course', string='Course')
    batch_ids = fields.Many2many('op.batch',
                                 domain="[('course_id', '=', course_ids)]",
                                 string='Batch')
    subject_id = fields.Many2one('op.subject',
                                 domain="[('course_id', '=', course_ids)]",
                                 string='Subject')
    student_course_ids = fields.Many2many('op.student.course',
                                          string='Student')
