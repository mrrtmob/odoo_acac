# -*- coding: utf-8 -*-
# from odoo import http


# class PmLeads(http.Controller):
#     @http.route('/pm_leads/pm_leads/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pm_leads/pm_leads/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pm_leads.listing', {
#             'root': '/pm_leads/pm_leads',
#             'objects': http.request.env['pm_leads.pm_leads'].search([]),
#         })

#     @http.route('/pm_leads/pm_leads/objects/<model("pm_leads.pm_leads"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pm_leads.object', {
#             'object': obj
#         })
