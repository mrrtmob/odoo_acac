from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'
    rate = fields.Integer('Exchange Rate', compute="_compute_rate", store=True)
    currency_name = fields.Char(related='currency_id.name')
    purchase_order_id = fields.Many2one('purchase.order')
    identification_number = fields.Char("Identification Number")

    @api.depends('invoice_date')
    def _compute_rate(self):
        for record in self:
            khmer_currency_rel = self.env['res.currency'].search([('name', '=', 'KHR')])
            exchange_rate_invoice_date = self.env['res.currency.rate'].search(
                [('name', '=', record.invoice_date), ('currency_id', '=', khmer_currency_rel.id)])
            if exchange_rate_invoice_date:
                record.rate = exchange_rate_invoice_date.rate
            else:
                record.rate = self.env['res.currency.rate'].search([('currency_id', '=', khmer_currency_rel.id)], limit=1,
                                                            order='create_date desc').rate

    @api.onchange('invoice_date', 'currency_id')
    def _onchange_currency_id(self):
        rate = 1

        exchange_rate_invoice_date = self.env['res.currency.rate'].search(
            [('name', '=', self.invoice_date), ('currency_id', '=', self.currency_id.id)]
        )

        if exchange_rate_invoice_date:
            rate = exchange_rate_invoice_date.rate
        else:
            matched_exchange_rate = self.env['res.currency.rate'].search(
                [('name', '<', self.invoice_date), ('currency_id', '=', self.currency_id.id)],
                limit=1,
                order='name desc'
            )

            if matched_exchange_rate:
                rate = matched_exchange_rate.rate
            else:
                latest_exchange_rate = self.env['res.currency.rate'].search(
                    [('currency_id', '=', self.currency_id.id)],
                    limit=1,
                    order='name desc'
                )

                if latest_exchange_rate:
                    rate = latest_exchange_rate.rate

        self.rate = rate

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    uom = fields.Many2one('pm.product.uom')

class AccountJournal(models.Model):
  _inherit = "account.journal"

  suspense_account_id = fields.Many2one(
        comodel_name='account.account', check_company=True, ondelete='restrict', readonly=False, store=True,
        compute='_compute_suspense_account_id',
        help="Bank statements transactions will be posted on the suspense account until the final reconciliation "
             "allowing finding the right account.", string='Suspense Account',
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id)]")