# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, exceptions, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    is_assignee = fields.Boolean('Approver', compute="compute_is_approver", readonly=True, default=False)

    procurement_type = fields.Selection([
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ], compute="_compute_procurement_type", store=True, readonly=True)

    expense_type = fields.Selection([
        ('culinary', 'Culinary'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    ], 'Budget Account', required=True)

    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Assigned to",
        track_visibility="onchange",
        readonly=True,
        domain=lambda self: [
            (
                "groups_id",
                "in",
                self.env.ref("purchase_request.group_purchase_request_manager").id,
            )
        ],
        index=True,
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('to_approve_first', 'First Approval'),
        ('to approve', 'Final Approval'),
        ('purchase', 'Purchase Order'),
        ('done', 'Done'),
        ('rejected', 'Rejected'),
        ('cancel', 'Cancelled'),
        ('product_received', 'Product Received')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    valid_quote = fields.Boolean(default=False)
    remarks = fields.Char('Remarks')
    approval_record_id = fields.Many2one('pm.approval')
    pr_state = fields.Selection([
        ("draft", "Draft"),
        ("quote_gathering", "Quote Gathering"),
        ("quote_submitted", "Quote Submitted"),
        ("to_approve", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("done", "Done"),
    ], related='request_id.state')

    quotation_state = fields.Selection(
        [('approved', 'Approved'),
         ('rejected', 'Rejected'),
         ]
    )
    request_id = fields.Many2one(
        comodel_name="purchase.request",
        string="Purchase Request",
        readonly=False,
    )
    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    requested_by = fields.Many2one(
        comodel_name="res.users",
        string="Requested by",
        required=False,
        readonly=True,
        copy=False,
        track_visibility="onchange",
        default=_get_default_requested_by,
        index=True,
    )



    def get_emails(self, follower_ids):
        email_ids = ''
        for user in follower_ids:
            if email_ids:
                email_ids = email_ids + ',' + str(user.sudo().partner_id.email)
            else:
                email_ids = str(user.sudo().partner_id.email)
        return email_ids

    @api.depends('assigned_to')
    def compute_is_approver(self):
        self.is_assignee = False
        print(self.env.user)
        print(self.assigned_to)

        if self.env.user == self.assigned_to:
            self.is_assignee = True
            print('I am approver')
        else:
            print(self.is_assignee)
            print('I am not approver')

    def button_approve_first(self):
        state = 'to approve'
        approval = self.approval_record_id
        approval.write({'state': state})
        self.write({'state': state, 'assigned_to': approval.approve})

    def button_rejected(self):
        user = self.env.user
        message = _("PR %s has been rejected by %s ") % (
            self.name,
            user.name
        )
        self.message_post(body=message, subtype="mail.mt_comment")

        self.write({'state': 'rejected'})


    def action_approve_quote(self):
        pr = self.request_id
        if self.valid_quote == False:
            valid_pr = self.env['purchase.order'].search([('request_id', '=', pr.id),
                                                          ('valid_quote', '=', True)])
            if valid_pr:
                print('old:', valid_pr.name)
                print('new:', self.name)
                print('sending email')
                message = _("Selected quote on PR %s has been changed") % (
                    pr.name,
                )
                pr.message_post(body=message, subtype="mail.mt_comment")
            else:
                print('I am newly selected quote')

        for po_line in pr.purchase_order_ids:
            if po_line.id != self.id:
                po_line.quotation_state = 'rejected'
                po_line.valid_quote = False

        return self.write({
            'quotation_state': 'approved',
            'valid_quote': True
        })

    def action_remove_quote(self):
        self.button_cancel()
        self.unlink()


    def _purchase_request_confirm_message_content(self, request, request_dict=None):
        self.ensure_one()
        if not request_dict:
            request_dict = {}
        title = _("Order confirmation %s for your Request %s") % (
            self.name,
            request.name,
        )
        message = "<h3>%s</h3><ul>" % title
        message += _(
            "The following requested items from Purchase Request %s "
            "have now been confirmed in Purchase Order %s:"
        ) % (request.name, self.name)

        print(request_dict.values())
        for line in request_dict.values():

            message += _(
                "<li><b>%s</b>: Ordered quantity %s %s, Planned date %s</li>"
            ) % (
                line["name"],
                line["product_qty"],
                line["product_uom"],
                line["date_planned"],
            )
        message += "</ul>"
        return message

    # def action_view_picking(self):
    #     print('hit recieve product')
    #     return


    def _purchase_request_confirm_message(self):
        request_obj = self.env["purchase.request"]
        for po in self:
            requests_dict = {}
            for line in po.order_line:
                for request_line in line.sudo().purchase_request_lines:
                    request_id = request_line.request_id.id
                    if request_id not in requests_dict:
                        requests_dict[request_id] = {}
                    date_planned = "%s" % line.date_planned
                    data = {
                        "name": line.product_id.name,
                        "product_qty": line.product_qty,
                        "product_uom": line.product_uom.name,
                        "date_planned": date_planned,
                    }
                    requests_dict[request_id][request_line.id] = data
            for request_id in requests_dict:
                request = request_obj.sudo().browse(request_id)
                message = po._purchase_request_confirm_message_content(
                    request, requests_dict[request_id]
                )
                request.message_post(body=message, subtype="mail.mt_comment")
        return True

    def _purchase_request_line_check(self):
        for po in self:
            for line in po.order_line:
                for request_line in line.purchase_request_lines:
                    if request_line.sudo().purchase_state == "done":
                        raise exceptions.UserError(
                            _("Purchase Request %s has already been completed")
                            % request_line.request_id.name
                        )
        return True

    def button_approve(self):
        self.approval_record_id.write({
            'state': 'approved'
        })
        res = super(PurchaseOrder, self).button_approve()
        self._purchase_request_confirm_message()
        return res

    def button_confirm(self):
        self._purchase_request_line_check()

        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()

            if order.procurement_type == 'large' and order.user_has_groups('pm_leads.group_acac_ceo') \
                or order.expense_type == 'culinary':
                print('hit me please !!')
                order.button_approve()
                order.write(
                    {
                        "assigned_to": self.env.user,
                        "requested_by": self.request_id.requested_by,
                    }
                )
            else:
                if self.procurement_type == 'large' and not order.user_has_groups('pm_leads.group_acac_dean'):
                    print('Hit Me XD')
                    state = 'to_approve_first'
                else:
                    state = 'to approve'
                approval_type = self.env['pm.approval.type'].search([('base_model', '=', 'purchase.order'),
                                                                    ('type', '=', self.expense_type)], limit=1)
                approval = self.env['pm.approval'].create({
                    'approval_type_id': approval_type.id,
                    'record_id': self.id,
                    'procurement_type': self.procurement_type,
                    'state': state,
                })
                order.write({
                    "state": state,
                    "assigned_to": approval.approve,
                    "requested_by": self.env.user,
                    'approval_record_id': approval.id})

        return True

    def unlink(self):
        self.button_cancel()

        alloc_to_unlink = self.env["purchase.request.allocation"]
        for rec in self:
            for alloc in (
                rec.order_line.mapped("purchase_request_lines")
                .mapped("purchase_request_allocation_ids")
                .filtered(lambda alloc: alloc.purchase_line_id.order_id.id == rec.id)
            ):
                alloc_to_unlink += alloc
        res = super().unlink()
        alloc_to_unlink.unlink()
        return res

    @api.depends('amount_total')
    def _compute_procurement_type(self):
        for record in self:
            large = 1500
            large_amount = float(self.env['ir.config_parameter'].sudo().get_param('purchase.large_purchase_amount'))
            if large_amount:
                large = large_amount
            if record.amount_total > large:
                record.procurement_type = 'large'
            else:
                record.procurement_type = 'small'


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    uom = fields.Many2one('pm.product.uom', 'UoM', store=True, related='product_id.supplier_product_uom_id',
                                  tracking=True, readonly=True)

    purchase_request_lines = fields.Many2many(
        comodel_name="purchase.request.line",
        relation="purchase_request_purchase_order_line_rel",
        column1="purchase_order_line_id",
        column2="purchase_request_line_id",
        string="Purchase Request Lines",
        readonly=True,
        copy=False,
    )

    purchase_request_allocation_ids = fields.One2many(
        comodel_name="purchase.request.allocation",
        inverse_name="purchase_line_id",
        string="Purchase Request Allocation",
        copy=False,
    )

    @api.depends('product_uom', 'product_qty', 'product_id.uom_id')
    def _compute_product_uom_qty(self):
        for line in self:
            line.product_uom_qty = line.product_qty

    def action_openRequestLineTreeView(self):
        """
        :return dict: dictionary value for created view
        """
        request_line_ids = []
        for line in self:
            request_line_ids += line.purchase_request_lines.ids

        domain = [("id", "in", request_line_ids)]

        return {
            "name": _("Purchase Request Lines"),
            "type": "ir.actions.act_window",
            "res_model": "purchase.request.line",
            "view_mode": "tree,form",
            "domain": domain,
        }


    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        val = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        val[0]['estimated_cost'] = self.price_unit
        val[0]['actual_cost'] = self.price_unit

        all_list = []
        for v in val:
            all_ids = self.env["purchase.request.allocation"].search(
                [("purchase_line_id", "=", v["purchase_line_id"])]
            )
            for all_id in all_ids:
                all_list.append((4, all_id.id))
            v["purchase_request_allocation_ids"] = all_list
        print(val)
        return val

    def update_service_allocations(self, prev_qty_received):
        for rec in self:
            allocation = self.env["purchase.request.allocation"].search(
                [
                    ("purchase_line_id", "=", rec.id),
                    ("purchase_line_id.product_id.type", "=", "service"),
                ]
            )
            if not allocation:
                return
            qty_left = rec.qty_received - prev_qty_received
            for alloc in allocation:
                allocated_product_qty = alloc.allocated_product_qty
                if not qty_left:
                    alloc.purchase_request_line_id._compute_qty()
                    break
                if alloc.open_product_qty <= qty_left:
                    allocated_product_qty += alloc.open_product_qty
                    qty_left -= alloc.open_product_qty
                    alloc._notify_allocation(alloc.open_product_qty)
                else:
                    allocated_product_qty += qty_left
                    alloc._notify_allocation(qty_left)
                    qty_left = 0
                alloc.write({"allocated_product_qty": allocated_product_qty})

                message_data = self._prepare_request_message_data(
                    alloc, alloc.purchase_request_line_id, allocated_product_qty
                )
                message = self._purchase_request_confirm_done_message_content(
                    message_data
                )
                alloc.purchase_request_line_id.request_id.message_post(
                    body=message, subtype="mail.mt_comment"
                )

                alloc.purchase_request_line_id._compute_qty()
        return True

    @api.model
    def _purchase_request_confirm_done_message_content(self, message_data):
        title = _("Service confirmation for Request %s") % (
            message_data["request_name"]
        )
        message = "<h3>%s</h3>" % title
        message += _(
            "The following requested services from Purchase"
            " Request %s requested by %s "
            "have now been received:"
        ) % (message_data["request_name"], message_data["requestor"])
        message += "<ul>"
        message += _("<li><b>%s</b>: Received quantity %s %s</li>") % (
            message_data["product_name"],
            message_data["product_qty"],
            message_data["product_uom"],
        )
        message += "</ul>"
        return message

    def _prepare_request_message_data(self, alloc, request_line, allocated_qty):
        return {
            "request_name": request_line.request_id.name,
            "product_name": request_line.product_id.name,
            "product_qty": allocated_qty,
            "product_uom": alloc.product_uom_id.name,
            "requestor": request_line.request_id.requested_by.partner_id.name,
        }

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        print('I am Fake')
        # if not self.product_id:
        #     return
        # params = {'order_id': self.order_id}
        # seller = self.product_id._select_seller(
        #     partner_id=self.partner_id,
        #     quantity=self.product_qty,
        #     date=self.order_id.date_order and self.order_id.date_order.date(),
        #     uom_id=self.product_uom,
        #     params=params)
        # print(self)
        # print(self.price_unit)

        # if seller or not self.date_planned:
        #     self.date_planned = self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        # if not seller:
        #     if self.product_id.seller_ids.filtered(lambda s: s.name.id == self.partner_id.id):
        #         self.price_unit = 0.0
        #     return

        # price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price,
        #                                                                      self.product_id.supplier_taxes_id,
        #                                                                      self.taxes_id,
        #                                                                      self.company_id) if seller else 0.0
        # if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
        #     print(1)
        #     price_unit = seller.currency_id._convert(
        #         price_unit, self.order_id.currency_id, self.order_id.company_id, self.date_order or fields.Date.today())
        #
        # if seller and self.product_uom and seller.product_uom != self.product_uom:
        #     print(2)
        #     price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)
        #
        # print('price:', price_unit)
        #
        # self.price_unit = price_unit

    def write(self, vals):
        #  As services do not generate stock move this tweak is required
        #  to allocate them.
        prev_qty_received = {}
        if vals.get("qty_received", False):
            service_lines = self.filtered(lambda l: l.product_id.type == "service")
            for line in service_lines:
                prev_qty_received[line.id] = line.qty_received
        res = super(PurchaseOrderLine, self).write(vals)
        if prev_qty_received:
            for line in service_lines:
                line.update_service_allocations(prev_qty_received[line.id])
        return res
