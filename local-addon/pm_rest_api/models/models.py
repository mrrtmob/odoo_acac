from odoo import models, fields


class PmTransactions(models.Model):
    _name = 'pm.aba.transaction'
    _description = 'ABA Transaction'
    transaction_number = fields.Char()
    status = fields.Char()
