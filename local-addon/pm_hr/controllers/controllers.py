# -*- coding: utf-8 -*-
# from odoo import http


# class PmHr(http.Controller):
#     @http.route('/pm_hr/pm_hr/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pm_hr/pm_hr/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pm_hr.listing', {
#             'root': '/pm_hr/pm_hr',
#             'objects': http.request.env['pm_hr.pm_hr'].search([]),
#         })

#     @http.route('/pm_hr/pm_hr/objects/<model("pm_hr.pm_hr"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pm_hr.object', {
#             'object': obj
#         })
