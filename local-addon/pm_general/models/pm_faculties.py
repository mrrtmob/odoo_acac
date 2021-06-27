from odoo import api, fields, models

class CustomFaculty(models.Model):
    _inherit = 'op.faculty'

    job_position = fields.Char('Job Position')