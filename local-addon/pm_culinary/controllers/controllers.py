# -*- coding: utf-8 -*-
from odoo import http


class PmCulinary(http.Controller):
    @http.route('/student/culinary', auth='public')
    def index(self, **kw):
        print('here')
        return "Hello, world"

    @http.route('/pm_culinary/pm_culinary/objects/', auth='public')
    def list(self, **kw):
        return http.request.render('pm_culinary.listing', {
            'root': '/pm_culinary/pm_culinary',
            'objects': http.request.env['pm_culinary.pm_culinary'].search([]),
        })

    @http.route('/pm_culinary/pm_culinary/objects/<model("pm_culinary.pm_culinary"):obj>/', auth='public')
    def object(self, obj, **kw):
        return http.request.render('pm_culinary.object', {
            'object': obj
        })
