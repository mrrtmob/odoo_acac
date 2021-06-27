# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import datetime
from datetime import datetime, timedelta
from odoo.http import request

_STATES = [
    ("draft", "Draft"),
    ("quote_gathering", "Quote Gathering"),
    ("quote_submitted", "Quote Submitted"),
    ("to_approve", "Submitted"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("done", "Done"),
]


class PurchaseRequest(models.Model):

    _name = "purchase.request"
    _description = "Purchase Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"


    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("purchase.request")

    @api.model
    def _default_picking_type(self):
        type_obj = self.env["stock.picking.type"]
        company_id = self.env.context.get("company_id") or self.env.company.id
        types = type_obj.search(
            [("code", "=", "incoming"), ("warehouse_id.company_id", "=", company_id)]
        )
        if not types:
            types = type_obj.search(
                [("code", "=", "incoming"), ("warehouse_id", "=", False)]
            )
        return types[:1]

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ("to_approve", "approved", "rejected", "done"):
                rec.is_editable = False
            else:
                rec.is_editable = True

    record_url = fields.Char('Link', compute='_compute_record_url', store=True)
    name = fields.Char(
        string="Request Reference",
        required=True,
        default=_get_default_name,
        track_visibility="onchange",
    )
    is_food_item = fields.Boolean('Food Item')
    is_automated = fields.Boolean('Automated Purchase Request', default=False)
    request_type = fields.Selection([
        ('food', 'Food Item'),
        ('non-food', 'Non-Food Items'),
        ('other', 'Other'),
    ])
    total_amount = fields.Float('Total Amount',
                                currency_field="currency_id",
                                readonly=True,
                                compute="_compute_total_amount")
    approved_date = fields.Date('Approved Date', readonly=True)
    schedule_dish_id = fields.Many2one('pm.schedule', 'Related Schedule of Dish', readonly=True)
    event_date = fields.Datetime('Event Date', related='schedule_dish_id.event_date')
    origin = fields.Char(string="Source Document")
    date_start = fields.Date(
        string="Creation date",
        help="Date when the user initiated the request.",
        default=fields.Date.context_today,
        track_visibility="onchange",
    )
    delivery_date = fields.Date(
        string="Delivery date",
        default=fields.Date.context_today,
        track_visibility="onchange",
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        string="Requested by",
        required=False,
        copy=False,
        track_visibility="onchange",
        default=_get_default_requested_by,
        index=True,
    )
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
    description = fields.Text(string="Description")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=False,
        default=_company_get,
        track_visibility="onchange",
    )
    line_ids = fields.One2many(
        comodel_name="purchase.request.line",
        inverse_name="request_id",
        string="Products to Purchase",
        readonly=False,
        copy=True,
        track_visibility="onchange",
    )
    des_line_ids = fields.One2many(
        comodel_name="purchase.description.line",
        inverse_name="request_id",
        string="Products to Purchase",
        readonly=False,
        copy=True,
        track_visibility="onchange",
    )
    purchase_order_ids = fields.One2many(
        comodel_name='purchase.order',
        track_visibility="onchange",
        inverse_name="request_id",
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
        related="line_ids.product_id",
        string="Product",
        readonly=True,
    )
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        track_visibility="onchange",
        required=True,
        copy=False,
        default="draft",
    )
    is_editable = fields.Boolean(
        string="Is editable", compute="_compute_is_editable", readonly=True
    )
    to_approve_allowed = fields.Boolean(compute="_compute_to_approve_allowed")
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
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Picking Type",
        required=False,
        default=_default_picking_type,
    )
    group_id = fields.Many2one(
        comodel_name="procurement.group",
        string="Procurement Group",
        copy=False,
        index=True,
    )
    line_count = fields.Integer(
        string="Purchase Request Line count",
        compute="_compute_line_count",
        readonly=True,
    )
    move_count = fields.Integer(
        string="Stock Move count", compute="_compute_move_count", readonly=True
    )
    purchase_count = fields.Integer(
        string="Purchases count", compute="_compute_purchase_count", readonly=True
    )
    quote_count = fields.Integer(
        string="Quotes count", compute="_compute_quote_count", readonly=True
    )
    is_assignee = fields.Boolean('Approver', compute="compute_is_approver", readonly=True, default=False)
    can_create_quote = fields.Boolean('Allow Create Quote', compute="compute_allow_create_quote", default=False)
    can_select_quote = fields.Boolean('Allow Select Quote', compute="compute_allow_select_quote", default=False)
    approval_record_id = fields.Many2one('pm.approval')



    @api.depends('expense_type',
                 'procurement_type',
                 'is_assignee')
    def compute_allow_select_quote(self):
        for record in self:
            res = False
            print('I can not select quote for small marketing')
            if self.is_assignee:
                res = True
            if self.expense_type == 'marketing' and self.procurement_type == 'small' and self.env.user == self.requested_by:
                print('I can select quote for small marketing')
                res = True
            record.can_select_quote = res


    @api.depends('state','procurement_type')
    def compute_allow_create_quote(self):
        self.can_create_quote = False
        if self.procurement_type == 'small':
            self.can_create_quote = True
            print('I can create quote')
        elif self.procurement_type == 'medium' and self.state == 'request_approved':
            self.can_create_quote = True
        elif self.procurement_type == 'large' and self.state == 'request_approved':
            self.can_create_quote = True

    @api.depends('assigned_to')
    def compute_is_approver(self):
        self.is_assignee = False
        if self.state == 'request_approved' and self.env.user == self.requested_by:
            self.is_assignee = True
            print('I am dean')
            print(self.is_assignee)
            print(self.state)
            print(self.is_automated)
        elif self.env.user == self.assigned_to:
            self.is_assignee = True
            print('I am approver')
            print(self.state)
            print(self.is_automated)
        else:
            print('I am not approver')
            self.is_assignee = False

    @api.depends('total_amount', 'expense_type')
    def _compute_procurement_type(self):
        print('exe')
        for record in self:
            large = 1500
            medium = 250
            large_amount = float(self.env['ir.config_parameter'].sudo().get_param('purchase.large_purchase_amount'))
            if large_amount:
                large = large_amount
            if record.total_amount > large:
                record.procurement_type = 'large'
            else:
                record.procurement_type = 'small'
                if self.expense_type == 'other' and record.total_amount > medium:
                    record.procurement_type = 'medium'




    @api.depends('name')
    def _compute_record_url(self):
        for record in self:
            base_url = request.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=purchase.request' % (record.id)
            record.record_url = base_url

    @api.depends("line_ids")
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(x.estimated_cost for x in record.line_ids)

    @api.depends("purchase_order_ids")
    def _compute_purchase_count(self):
        # self.purchase_count = len(self.mapped("line_ids.purchase_lines.order_id"))
        self.purchase_count = self.env['purchase.order'].search_count([('request_id', '=', self.id),
                                                                       ('state', 'in', ['purchase', 'done'])])

    @api.depends("purchase_order_ids")
    def _compute_quote_count(self):
        self.quote_count = self.env['purchase.order'].search_count([('request_id', '=', self.id)])

    def action_view_purchase_order(self):
        action = self.env.ref("purchase.purchase_form_action").read()[0]
        lines = self.env['purchase.order'].search([('request_id', '=', self.id),
                                                   ('state', '=', 'done')])
        print(lines)
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = lines.id
        return action

    def action_view_quote(self):
        action = self.env.ref("purchase.purchase_rfq").read()[0]
        lines = self.env['purchase.order'].search([('request_id', '=', self.id),
                                                   ('state', '!=', 'done')])
        action["domain"] = [("id", "in", lines.ids)]
        return action

    @api.depends("line_ids")
    def _compute_move_count(self):
        self.move_count = len(
            self.mapped("line_ids.purchase_request_allocation_ids.stock_move_id")
        )

    def action_view_stock_move(self):
        action = self.env.ref("stock.stock_move_action").read()[0]
        # remove default filters
        action["context"] = {}
        lines = self.mapped("line_ids.purchase_request_allocation_ids.stock_move_id")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [(self.env.ref("stock.view_move_form").id, "form")]
            action["res_id"] = lines.id
        return action

    @api.depends("line_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.mapped("line_ids"))

    def action_view_purchase_request_line(self):
        action = self.env.ref(
            "purchase_request.purchase_request_line_form_action"
        ).read()[0]
        lines = self.mapped("line_ids")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase_request.purchase_request_line_form").id, "form")
            ]
            action["res_id"] = lines.ids[0]
        return action

    @api.depends("state", "line_ids.is_danger")
    def _compute_to_approve_allowed(self):
        allow = True
        for rec in self:
            for line in rec.line_ids:
                if line.qty_to_order <= 0 or line.cancelled:
                    allow = False
        rec.to_approve_allowed = allow

    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update({"state": "draft", "name": self._get_default_name()})
        return super(PurchaseRequest, self).copy(default)

    @api.model
    def _get_partner_id(self, request):
        user_id = request.assigned_to or self.env.user
        return user_id.partner_id.id

    @api.model
    def create(self, vals):
        request = super(PurchaseRequest, self).create(vals)
        if vals.get("assigned_to"):
            partner_id = self._get_partner_id(request)
            request.message_subscribe(partner_ids=[partner_id])
        return request

    def write(self, vals):
        res = super(PurchaseRequest, self).write(vals)
        for request in self:
            if vals.get("assigned_to"):
                partner_id = self._get_partner_id(request)
                request.message_subscribe(partner_ids=[partner_id])
        return res

    def _can_be_deleted(self):
        self.ensure_one()
        return self.state == "draft"

    def unlink(self):
        for request in self:
            if not request._can_be_deleted():
                raise UserError(
                    _("You cannot delete a purchase request which is not draft.")
                )
        return super(PurchaseRequest, self).unlink()

    def button_draft(self):
        # self.mapped("line_ids").do_uncancel()
        if self.approval_record_id:
            self.approval_record_id.unlink()
        return self.write({"state": "draft"})

    def button_submit_automated_request(self):
        self.to_approve_allowed_check()
        state = 'to_approve'
        approval_type = self.env['pm.approval.type'].search([('base_model', '=', 'purchase.request'),
                                                             ('type', '=', self.expense_type)])

        approval = self.env['pm.approval'].create({
            'approval_type_id': approval_type.id,
            'record_id': self.id,
            'procurement_type': self.procurement_type,
            'state': 'submitted',
        })


        self.message_subscribe(partner_ids=[approval.approve.partner_id.id])
        return self.write({"state": state, "assigned_to": approval.approve, 'approval_record_id': approval.id})


    def button_to_approve(self):
        self.to_approve_allowed_check()

        state = 'to_approve'

        if self.state == 'quote_gathering' and self.quote_count < 1:
            raise UserError(
                _(
                    "Please provide at least one quotes before submit"
                )
            )
        approval_type = self.env['pm.approval.type'].search([('base_model', '=', 'purchase.request'),
                                                             ('type', '=', self.expense_type)])
        approval = self.approval_record_id
        approval.write({'state': 'submitted'})

        self.message_subscribe(partner_ids=[approval.approve.partner_id.id])
        return self.write({"state": state, "assigned_to": approval.approve, 'approval_record_id': approval.id})

    def add_followers_by_group(self, group_name):
        all_user = self.env['res.users'].search([])
        user_ids = all_user.mapped('id')
        partners = []
        for user_id in user_ids:
            flag = self.env['res.users'].browse(user_id).has_group(group_name)
            if flag:
                user_record = self.env['res.users'].browse(user_id)
                partners.append(user_record.partner_id.id)
        return partners

    def button_request_quote(self):

        if self.expense_type in ['marketing', 'other'] and len(self.des_line_ids) < 1:
            raise UserError(
                _(
                    "Please provide at least one line item before request for quotations"
                )
            )
        if self.expense_type in ['culinary'] and len(self.line_ids) < 1:
            raise UserError(
                _(
                    "Please provide at least one product line before request for quotations"
                )
            )

        purchase_officers = self.add_followers_by_group('pm_culinary.group_acac_purchase_offcer')
        approval_type = self.env['pm.approval.type'].search([('base_model', '=', 'purchase.request'),
                                                             ('type', '=', self.expense_type)])
        approval = self.env['pm.approval'].create({
            'approval_type_id': approval_type.id,
            'record_id': self.id,
            'state': 'quote_gathering',
        })

        print('****************')
        print(approval)
        print(approval.id)

        self.message_subscribe(partner_ids=purchase_officers)
        self.write({
            'state': 'quote_gathering',
            'assigned_to': approval.approve,
            'approval_record_id': approval.id
        })


    def button_submit_quote(self):
        state = 'quote_submitted'
        if self.quote_count < 1:
            raise UserError(
                _(
                    "Please provide at least one quote before submit"
                )
            )
        approval = self.approval_record_id
        approval.state = state
        return self.write({"state": state,
                           'requested_by': self.env.user,
                           "assigned_to": approval.approve})


    def button_approved_quote(self):
        state = 'quote_approved'
        valid_quote = 0
        for quote in self.purchase_order_ids:
            if quote.valid_quote:
                valid_quote += 1
        if valid_quote != 1:
            raise UserError(
                _(
                    "Please select a quote"
                )
            )
        approval = self.approval_record_id
        approval.state = state

        return self.write({"state": state, 'requested_by': self.assigned_to, "assigned_to": approval.approve})


    def button_approved(self):

        followers = self.env['mail.followers'].sudo().search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id),
            ('partner_id', '!=', False),
        ]).mapped('partner_id')
        partners = followers.mapped('id')
        orders = self.purchase_order_ids

        # if there is quote, we convert quote to PO
        if orders:
            state = orders.mapped('valid_quote')
            print(state)
            if True not in state:
                raise UserError(
                    _(
                        "Please select a quote"
                    )
                )
            for line in orders:
                if line.quotation_state == 'rejected' and not line.valid_quote:
                    line.state = 'cancel'

                elif line.quotation_state == 'approved' and line.valid_quote:
                    line.message_subscribe(partner_ids=partners)
                    line.button_confirm()

        # if there is no quote, we generate PO by item lines
        else:
            self.generate_po()

        approval = self.approval_record_id
        if approval:
            approval.state = 'approved'

        return self.write({
            'state': 'approved',
        })

    def button_approved_auto(self):
        self.generate_po()
        approval = self.approval_record_id
        if approval:
            approval.state = 'approved'

        # # Send Mail To Requester
        # template_id = 68
        # print('sending.... PR mail')
        # self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

        return self.write({"state": "approved", "approved_date": str(datetime.now())})

    def generate_po(self):
        po_lines = {}
        if self.line_ids:
            for line in self.line_ids:
                supplier_id = line.supplier_id.id
                data = {
                    'product_id': line.product_id.id or line.product_id,
                    'name': line.product_id.name,
                    'product_uom': line.product_id.uom_id.id or False,
                    'product_qty': line.qty_to_order,
                    'price_unit': line.unit_price,
                    'date_planned': self.date_start,
                    'purchase_request_lines': [(4, line.id)]
                }
                if supplier_id not in po_lines:
                    po_lines[supplier_id] = [data]
                else:
                    po_lines[supplier_id].append(data)
            for supplier, value in po_lines.items():
                po = self.env['purchase.order'].create({
                    'partner_id': supplier,
                    'expense_type': self.expense_type,
                    'state': 'purchase',
                    'origin': self.origin,
                    'request_id': self.id,
                })
                for po_line in value:
                    po_line['order_id'] = po.id
                    self.env['purchase.order.line'].create(po_line)
        else:
            raise UserError(
                _(
                    "You need at least one item line to generate the PO"
                )
            )



    def button_rejected(self):
        # self.mapped("line_ids").do_cancel()
        state = 'rejected'

        user = self.env.user
        message = _(" %s has rejected %s ") % (
            user.name,
            self.name
        )
        self.message_post(body=message, subtype="mail.mt_comment")
        if self.approval_record_id:
            self.approval_record_id.state = 'rejected'

        print(state)
        return self.write({"state": state})

    def button_done(self):

        schedule_dish = self.schedule_dish_id;
        # Cut Stock From Used Ingredients in Schedule
        if schedule_dish:
            for record in schedule_dish:
                for menu_line in record.schedule_menu_ids:
                    for menu in menu_line.menu_id:
                        for recipe in menu.menu_line_ids.recipe_id:
                            for line in recipe.recipe_line_ids:
                                if line.sub_recipe_id:
                                    print('***********Sub Recipe***************')
                                    for sub_recipe in line.sub_recipe_id.recipe_line_ids:
                                        quantity = sub_recipe.quantity
                                        qty = sub_recipe.product_id.product_tmpl_id.qty_on_hand - quantity
                                        if qty > 0:
                                            sub_recipe.product_id.product_tmpl_id.qty_on_hand = qty
                                        else:
                                            sub_recipe.product_id.product_tmpl_id.qty_on_hand = 0
                                        print('Product:', sub_recipe.product_id.name)
                                        print('Quantity:', quantity)

                                else:
                                    print('***********Product***************')
                                    line.product_id.product_tmpl_id.qty_on_hand = line.product_id.product_tmpl_id.qty_on_hand - line.quantity
                                    print('Product:', line.product_id.name)
                                    print('Quantity:', line.quantity)

        #Create new stock from product line!!

        return self.write({"state": "done"})

    def check_auto_reject(self):
        """When all lines are cancelled the purchase request should be
        auto-rejected."""
        for pr in self:
            if not pr.line_ids.filtered(lambda l: l.cancelled is False):
                pr.write({"state": "rejected"})

    def to_approve_allowed_check(self):
        for rec in self:
            if not rec.to_approve_allowed:
                raise UserError(
                    _(
                        "You can't request an approval for a purchase request "
                        "which contains with QTY Order to order equal to 0. (%s)"
                    )
                    % rec.name
                )


