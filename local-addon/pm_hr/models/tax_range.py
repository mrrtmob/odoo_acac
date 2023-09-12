from odoo import models, fields


class PMSalaryTax(models.Model):
    _name = 'pm.tax.configuration'
    _description = 'Salary Tax Range Configuration'
    min_salary = fields.Float('Minimum Salary')
    max_salary = fields.Float('Maximum Salary')
    tax_rate = fields.Float('Tax Rate')



