# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo.http import request
import collections
from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal


class StudentSkillPortal(CustomerPortal):

    @http.route(['/student/skill',
                 '/student/skill/page/<int:page>'],
                type='http', auth="user", website=True)
    def enterprise_portal_student_skill(self, **kw):

        partner_id = request.env.user.partner_id
        student_id = request.env['op.student'].sudo().search(
            [('partner_id', '=', partner_id.id)])
        skill_id = request.env['op.skill'].sudo().search([])
        rating_id = request.env['op.skill.line']._fields['rating'].selection
        rating_dict = collections.OrderedDict(dict(rating_id))
        rating = [key for key in sorted(rating_dict.keys())]

        return request.render(
            "openeducat_skill_enterprise.enterprise_add_student_skill_portal",
            {'skill_ids': skill_id,
             'rating_ids': rating,
             'user': student_id,
             'page_name': 'student_skill_form'
             })

    @http.route(['/student/skill/submit',
                 '/student/skill/submit/page/<int:page>'],
                type='http', auth="user", website=True)
    def enterprise_portal_add_student_skill(self, **kw):
        vals = {
            'student_id': kw['student_id'],
            'skill_type_id': kw['skill_type_id'],
            'rating': kw['rating']
        }
        partner_id = request.env.user.partner_id
        student_id = request.env['op.student'].sudo().search(
            [('partner_id', '=', partner_id.id)])

        student_id.skill_line.sudo().create(vals)

        return request.redirect('/student/profile')
