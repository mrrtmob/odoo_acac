# -*- coding: utf-8 -*-
# from odoo import http


# class PmApproval(http.Controller):
#     @http.route('/pm_approval/pm_approval/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pm_approval/pm_approval/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pm_approval.listing', {
#             'root': '/pm_approval/pm_approval',
#             'objects': http.request.env['pm_approval.pm_approval'].search([]),
#         })

#     @http.route('/pm_approval/pm_approval/objects/<model("pm_approval.pm_approval"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pm_approval.object', {
#             'object': obj
#         })
