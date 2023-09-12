
import time

from odoo import models, api

class ComercialInvoice(models.AbstractModel):
    _name = "report.pm_accounting.report_commercial_invoice"
    _description = "Commercial Invoice"

    def get_customer_name(self, invoice_id):
        invoice = self.env['account.move'].search([('id', '=', invoice_id)])
        return invoice.partner_id.name

    def get_company_name(self, invoice_id):
        invoice = self.env['account.move'].search([('id', '=', invoice_id)])
        return invoice.partner_id.company_id.name


    def get_invoice_data(self, invoice_id):
        sub_total = 0.0
        n = 1
        line = []
        invoice = self.env['account.move'].search([('id', '=', invoice_id)])
        for inv in invoice:
            rate = invoice.rate
            for inv_line_id in inv.invoice_line_ids:
                sub_total += inv_line_id.price_subtotal
                line.append({
                    'number': n,
                    'name': inv_line_id.name,
                    'qty': inv_line_id.quantity,
                    'unit_price': '${:,.2f}'.format(inv_line_id.price_unit),
                    'total': '${:,.2f}'.format(inv_line_id.price_subtotal),
                    'total_kh': '៛{:,.2f}'.format(inv_line_id.price_subtotal * rate),
                })
                n += 1
        sub_total_kh = sub_total * rate
        tax = sub_total * 0.1
        tax_kh = tax * rate
        grand_total = sub_total + tax
        grand_total_kh = grand_total * rate

        data = [{'item_lines': line,
                 'sub_total': '{:,.2f}'.format(sub_total),
                 'sub_total_kh': '{:,.2f}'.format(sub_total_kh),
                 'rate': rate,
                 'tax': '{:,.2f}'.format(tax),
                 'tax_kh': '{:,.2f}'.format(tax_kh),
                 'grand_total': '{:,.2f}'.format(grand_total),
                 'grand_total_kh': '{:,.2f}'.format(grand_total_kh)}]
        return data

    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('module.pm_accounting.report_commercial_invoice')
        docs = self.env['account.move'].search([('id', '=', docids)])
        print(docs)
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': docs,
            'get_invoice_data': self.get_invoice_data(docids),
            'get_company_name': self.get_company_name(docids),
        }

        return docargs