# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo.http import request, Response

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import QueryURL
from odoo.osv import expression
from collections import OrderedDict
from odoo.tools import groupby as groupbyelem
from operator import itemgetter


class Students(http.Controller):

    @http.route("/get_student_list", type="json", auth="user")
    def get_student_list(self):

        Student = request.env['op.student']
        student_list = []
        all_student = Student.search([])
        for student in all_student:
            vals = {
                'name': student.name,
                'student_id': student.student_app_id
            }
            student_list.append(vals)

        student_count = len(all_student)

        return {
            'total_student': student_count,
            'students': student_list,
        }







