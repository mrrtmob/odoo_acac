# -*- coding: utf-8 -*-
# from odoo import http


# class PmAdmission(http.Controller):
#     @http.route('/pm_admission/pm_admission/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pm_admission/pm_admission/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pm_admission.listing', {
#             'root': '/pm_admission/pm_admission',
#             'objects': http.request.env['pm_admission.pm_admission'].search([]),
#         })

#     @http.route('/pm_admission/pm_admission/objects/<model("pm_admission.pm_admission"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pm_admission.object', {
#             'object': obj
#         })
