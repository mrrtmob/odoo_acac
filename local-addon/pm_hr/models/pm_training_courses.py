from odoo import fields, models, api


class PmTrainingCourses(models.Model):
    _name = 'pm.training.courses'
    _description = 'Description'

    name = fields.Char('Name', required=True)
    description = fields.Char('Description')
