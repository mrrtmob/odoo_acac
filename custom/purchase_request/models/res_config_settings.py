from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    large_purchase_amount = fields.Float(config_parameter='purchase.large_purchase_amount')
