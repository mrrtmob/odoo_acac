# -*- coding: utf-8 -*-
# from odoo import http


# class PmStudents(http.Controller):
#     @http.route('/pm_students/pm_students/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pm_students/pm_students/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pm_students.listing', {
#             'root': '/pm_students/pm_students',
#             'objects': http.request.env['pm_students.pm_students'].search([]),
#         })

#     @http.route('/pm_students/pm_students/objects/<model("pm_students.pm_students"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pm_students.object', {
#             'object': obj
#         })
