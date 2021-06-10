# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, models
from datetime import date,datetime


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_done(self):
        res = super(StockPicking, self).action_done()
        for lines in self.move_lines:
            uor_qty = lines.quantity_done * lines.product_id.supplier_qty_in_uor #Convert UOM to UOR first
            lines.product_id.qty_on_hand = lines.product_id.qty_on_hand + uor_qty
        journal_id = 2
        bill_obj = self.env['account.move'].with_context(default_journal_id=journal_id)
        move_line = self.move_ids_without_package
        purchase_order = move_line[0].purchase_line_id.order_id

        for purchase in purchase_order:

            analytic = purchase.expense_type
            if analytic == 'culinary':
                analytic = 'academic'
            analytic_account = self.env['account.analytic.account'].search([('code', '=', analytic)])

            bill_vals = {
                'type': 'in_invoice',
                'company_id': purchase.company_id.id,
                'purchase_id': purchase.id,
                'partner_id': purchase.partner_id.id,
                'partner_shipping_id': purchase.partner_id.id,
                'invoice_date_due': datetime.now(),
                'invoice_origin': purchase.partner_id.id,
                'purchase_order_id': purchase.id,
                'ref': purchase.partner_ref,
            }
            bill_objs = self.env['account.move']
            bill = bill_objs.create(bill_vals)
            account_line_data = []
            for line in purchase.order_line:
                taxes = [[6, False, line.taxes_id.mapped('id')]]
                print(taxes)
                invoice_val = {
                    'move_id': bill.id,
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'price_unit': line.price_unit,
                    'quantity': line.product_qty,
                    'uom': line.uom.id,
                    'purchase_line_id': line.id,
                    'analytic_account_id': analytic_account.id,
                    'account_id': line.product_id.property_account_expense_id.id,
                    'tax_ids': taxes,
                }
                account_line_data.append(invoice_val)

        print(account_line_data)
        MoveLine = self.env['account.move.line'].with_context(check_move_validity=False)
        MoveLine.create(account_line_data)

        return res


    @api.model
    def _purchase_request_picking_confirm_message_content(
        self, picking, request, request_dict
    ):
        if not request_dict:
            request_dict = {}
        title = _("Receipt confirmation %s for your Request %s") % (
            picking.name,
            request.name,
        )
        message = "<h3>%s</h3>" % title
        message += _(
            "The following requested items from Purchase Request %s "
            "have now been received in Incoming Shipment %s:"
        ) % (request.name, picking.name)
        message += "<ul>"
        for line in request_dict.values():
            message += _("<li><b>%s</b>: Received quantity %s %s</li>") % (
                line["name"],
                line["product_qty"],
                line["product_uom"],
            )
        message += "</ul>"
        return message

    # def action_done(self):
    #     super(StockPicking, self).action_done()
    #     request_obj = self.env["purchase.request"]
    #     for picking in self:
    #         requests_dict = {}
    #         if picking.picking_type_id.code != "incoming":
    #             continue
    #         for move in picking.move_lines:
    #             if move.purchase_line_id:
    #                 for (
    #                     request_line
    #                 ) in move.purchase_line_id.sudo().purchase_request_lines:
    #                     request_id = request_line.request_id.id
    #                     if request_id not in requests_dict:
    #                         requests_dict[request_id] = {}
    #                     data = {
    #                         "name": request_line.name,
    #                         "product_qty": move.product_qty,
    #                         "product_uom": move.product_uom.name,
    #                     }
    #                     requests_dict[request_id][request_line.id] = data
    #         for request_id in requests_dict:
    #             request = request_obj.sudo().browse(request_id)
    #             message = self._purchase_request_picking_confirm_message_content(
    #                 picking, request, requests_dict[request_id]
    #             )
    #             request.sudo().message_post(
    #                 body=message,
    #                 subtype="mail.mt_comment",
    #                 author_id=self.env.user.partner_id.id,
    #             )
