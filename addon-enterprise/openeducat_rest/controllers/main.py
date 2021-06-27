# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

import os
import re
import json
import base64
import inspect
import logging
import tempfile
import datetime
import traceback

from werkzeug import exceptions

import odoo
from odoo import _
from odoo import api
from odoo import tools
from odoo import http
from odoo import models
from odoo import release
from odoo.http import request
from odoo.http import Response
from odoo.tools.misc import str2bool

_logger = logging.getLogger(__name__)

REST_VERSION = {
    'server_version': release.version,
    'server_version_info': release.version_info,
    'server_serie': release.serie,
    'api_version': 2,
}

NOT_FOUND = {
    'error': 'unknown_command',
}

DB_INVALID = {
    'error': 'invalid_db',
}

FORBIDDEN = {
    'error': 'token_invalid',
}

NO_API = {
    'error': 'rest_api_not_supported',
}

LOGIN_INVALID = {
    'error': 'invalid_login',
}

DBNAME_PATTERN = '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'


def abort(message, rollback=False, status=403):
    response = Response(json.dumps(message,
                                   sort_keys=True, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=status)
    if request._cr and rollback:
        request._cr.rollback()
    exceptions.abort(response)


def check_token():
    token = request.params.get('token') and request.params.get('token').strip()
    if not token:
        abort(FORBIDDEN)
    env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
    uid = env['openeducat_rest.token'].check_token(token)
    if not uid:
        abort(FORBIDDEN)
    request._uid = uid
    request._env = api.Environment(request.cr, uid, request.session.context or {})


def ensure_db():
    db = request.params.get('db') and request.params.get('db').strip()
    if db and db not in http.db_filter([db]):
        db = None
    if not db and request.session.db and http.db_filter([request.session.db]):
        db = request.session.db
    if not db:
        db = http.db_monodb(request.httprequest)
    if not db:
        abort(DB_INVALID, status=404)
    if db != request.session.db:
        request.session.logout()
    request.session.db = db
    try:
        env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
        module = env['ir.module.module'].search(
            [['name', '=', "openeducat_rest"]], limit=1)
        if module.state != 'installed':
            abort(NO_API, status=500)
    except Exception as error:
        _logger.error(error)
        abort(DB_INVALID, status=404)


def check_params(params):
    missing = []
    for key, value in params.items():
        if not value:
            missing.append(key)
    if missing:
        abort({'error': "arguments_missing %s" % str(missing)}, status=400)


class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        def encode(item):
            if isinstance(item, models.BaseModel):
                vals = {}
                for name, field in item._fields.items():
                    if name in item:
                        if isinstance(item[name], models.BaseModel):
                            records = item[name]
                            if len(records) == 1:
                                vals[name] = (records.id, records.sudo().display_name)
                            else:
                                val = []
                                for record in records:
                                    val.append((record.id, record.sudo().display_name))
                                vals[name] = val
                        else:
                            try:
                                vals[name] = item[name].decode()
                            except UnicodeDecodeError:
                                vals[name] = item[name].decode('latin-1')
                            except AttributeError:
                                vals[name] = item[name]
                    else:
                        vals[name] = None
                return vals
            if inspect.isclass(item):
                return item.__dict__
            if isinstance(item, datetime.datetime):
                return item.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
            if isinstance(item, datetime.date):
                return item.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
            if isinstance(item, (bytes, bytearray)):
                return item.decode()
            try:
                return json.JSONEncoder.default(self, item)
            except TypeError:
                return "error"

        try:
            try:
                result = {}
                if not isinstance(obj, list):
                    item = obj
                if not isinstance(obj, bytes):
                    for key, value in obj.items():
                        result[key] = encode(item)
                    return result
                if isinstance(obj, bytes):
                    return encode(item)
            except AttributeError:
                result = []
                for item in obj:
                    result.append(encode(item))
                return result
        except TypeError:
            return encode(item)


class RESTController(http.Controller):

    # ----------------------------------------------------------
    # General
    # ----------------------------------------------------------

    @http.route('/api/<path:path>', auth="none", type='http', csrf=False)
    def api_catch(self, **kw):
        return Response(json.dumps(NOT_FOUND,
                                   sort_keys=True, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=404)

    @http.route('/api', auth="none", type='http')
    def api_version(self, **kw):
        return Response(json.dumps(REST_VERSION,
                                   sort_keys=True, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/change_master_password',
                auth="none", type='http', methods=['POST'], csrf=False)
    def api_change_password(self, password_old="admin", password_new=None, **kw):
        check_params({'password_new': password_new})
        try:
            http.dispatch_rpc('db', 'change_admin_password', [
                password_old,
                password_new])
            return Response(json.dumps(True,
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, status=400)

    # ----------------------------------------------------------
    # Database
    # ----------------------------------------------------------

    @http.route('/api/database/list', auth="none", type='http', csrf=False)
    def api_database_list(self, **kw):
        databases = []
        incompatible_databases = []
        try:
            databases = http.db_list()
            incompatible_databases = odoo.service.db.list_db_incompatible(databases)
        except odoo.exceptions.AccessDenied:
            monodb = http.db_monodb()
            if monodb:
                databases = [monodb]
        info = {
            'databases': databases,
            'incompatible_databases': incompatible_databases}
        return Response(json.dumps(info,
                                   sort_keys=True, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/database/create',
                auth="none", type='http', methods=['POST'], csrf=False)
    def api_database_create(self, master_password="admin", lang="en_US",
                            database_name=None, admin_login=None,
                            admin_password=None, **kw):
        check_params({
            'database_name': database_name,
            'admin_login': admin_login,
            'admin_password': admin_password})
        try:
            if not re.match(DBNAME_PATTERN, database_name):
                raise Exception(_('Invalid database name.'))
            http.dispatch_rpc('db', 'create_database', [
                master_password,
                database_name,
                bool(kw.get('demo')),
                lang,
                admin_password,
                admin_login,
                kw.get('country_code') or False])
            return Response(json.dumps(True,
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, status=400)

    @http.route('/api/database/duplicate',
                auth="none", type='http', methods=['POST'], csrf=False)
    def api_database_duplicate(self, master_password="admin",
                               database_old=None, database_new=None, **kw):
        check_params({
            'database_old': database_old,
            'database_new': database_new})
        try:
            if not re.match(DBNAME_PATTERN, database_new):
                raise Exception(_('Invalid database name.'))
            http.dispatch_rpc('db', 'duplicate_database', [
                master_password,
                database_old,
                database_new])
            return Response(json.dumps(True,
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, status=400)

    @http.route('/api/database/drop',
                auth="none", type='http', methods=['POST'], csrf=False)
    def api_database_drop(self, master_password="admin", database_name=None, **kw):
        check_params({'database_name': database_name})
        try:
            http.dispatch_rpc('db', 'drop', [
                master_password,
                database_name])
            request._cr = None
            return Response(json.dumps(True,
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, status=400)

    # ----------------------------------------------------------
    # Backup & Restore
    # ----------------------------------------------------------

    @http.route('/api/database/backup',
                auth="none", type='http', methods=['POST'], csrf=False)
    def api_database_backup(self, master_password="admin",
                            database_name=None, backup_format='zip', **kw):
        check_params({'database_name': database_name})
        try:
            odoo.service.db.check_super(master_password)
            ts = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
            filename = "%s_%s.%s" % (database_name, ts, backup_format)
            headers = [
                ('Content-Type', 'application/octet-stream; charset=binary'),
                ('Content-Disposition', http.content_disposition(filename)),
            ]
            dump_stream = odoo.service.db.dump_db(database_name, None, backup_format)
            return Response(dump_stream, headers=headers, direct_passthrough=True)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, status=400)

    @http.route('/api/database/restore',
                auth="none", type='http', methods=['POST'], csrf=False)
    def api_restore(self, master_password="admin", backup_file=None,
                    database_name=None, copy=False, **kw):
        check_params({'backup_file': backup_file, 'database_name': database_name})
        try:
            with tempfile.NamedTemporaryFile(delete=False) as data_file:
                backup_file.save(data_file)
            odoo.service.db.restore_db(database_name, data_file.name, str2bool(copy))
            return Response(json.dumps(True,
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, status=400)
        finally:
            os.unlink(data_file.name)

    # ----------------------------------------------------------
    # Token Authentication
    # ----------------------------------------------------------

    @http.route('/api/authenticate',
                auth="none", type='http', methods=['POST'], csrf=False)
    def api_authenticate(self, db=None, login=None, password=None, **kw):
        check_params({'db': db, 'login': login, 'password': password})
        ensure_db()
        uid = request.session.authenticate(db, login, password)
        if uid:
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            token = env['openeducat_rest.token'].generate_token(uid)
            return Response(json.dumps({'token': token.token,
                                        'token_id': token.id,
                                        'lifetime': token.lifetime,
                                        'user_id': token.user.id},
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        else:
            abort(LOGIN_INVALID, status=401)

    @http.route(['/api/usergroup',
                 '/api/usergroup/<int:user_id>'],
                auth="none", type='http', methods=['POST'], csrf=False)
    def get_user_group(self, user_id, token=None, **kw):

        check_params({'token': token})
        ensure_db()
        check_token()
        user = request.env['res.users'].search([('id', '=', user_id)])

        resp = {'is_student': 0, 'is_parent': 0, 'is_faculty': 0}
        resp['is_student'] = user.partner_id.is_student
        resp['is_parent'] = user.partner_id.is_parent
        resp['is_faculty'] = user.user_has_groups('openeducat_core.group_op_faculty')
        resp.update({
            'logo': user.partner_id.company_id.logo,
            'user_name': user.name,
            'user_iamge': user.partner_id.image_1920,
            'language': user.lang
        })
        return Response(json.dumps(resp, sort_keys=True, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8',
                        status=200)

    @http.route('/api/refresh', auth="none", type='http', methods=['POST'], csrf=False)
    def api_refresh(self, token=None, **kw):
        check_params({'token': token})
        ensure_db()
        check_token()
        env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
        result = env['openeducat_rest.token'].refresh_token(token)
        return Response(json.dumps(result,
                                   sort_keys=True, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route([
        '/api/life',
        '/api/life/<string:token>'], auth="none", type='http', csrf=False)
    def api_life(self, token=None, **kw):
        check_params({'token': token})
        ensure_db()
        check_token()
        env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
        result = env['openeducat_rest.token'].lifetime_token(token)
        return Response(json.dumps(result,
                                   sort_keys=True, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/close', auth="none", type='http', methods=['POST'], csrf=False)
    def api_close(self, token=None, **kw):
        check_params({'token': token})
        ensure_db()
        check_token()
        env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
        result = env['openeducat_rest.token'].delete_token(token)
        return Response(json.dumps(result,
                                   sort_keys=True, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=200)

        # ----------------------------------------------------------

    # System
    # ----------------------------------------------------------

    @http.route([
        '/api/search',
        '/api/search/<string:model>',
        '/api/search/<string:model>/<int:id>',
        '/api/search/<string:model>/<int:id>/<int:limit>',
        '/api/search/<string:model>/<int:id>/<int:limit>/<int:offset>'],
        auth="none", type='http', csrf=False)
    def api_search(self, model='res.partner', search_id=None, domain=None,
                   context=None, count=False, limit=80, offset=0,
                   order=None, token=None, **kw):
        check_params({'token': token})
        ensure_db()
        check_token()
        try:
            args = domain and json.loads(domain) or []
            if search_id:
                args.append(['id', '=', search_id])
            context = context and json.loads(context) or {}
            default = request.session.context.copy()
            default.update(context)
            count = count and bool(count) or None
            limit = limit and int(limit) or None
            offset = offset and int(offset) or None
            model = request.env[model].with_context(default)
            result = model.sudo().search(args, offset=offset,
                                         limit=limit, order=order, count=count)
            return Response(json.dumps(result,
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    @http.route([
        '/api/read',
        '/api/read/<string:model>',
        '/api/read/<string:model>/<int:id>',
        '/api/read/<string:model>/<int:id>/<int:limit>',
        '/api/read/<string:model>/<int:id>/<int:limit>/<int:offset>'],
        auth="none", type='http', csrf=False)
    def api_read(self, model='res.partner', read_id=None, fields=None, domain=None,
                 context=None, limit=80, offset=0, order=None, token=None, **kw):
        check_params({'token': token})
        ensure_db()
        check_token()
        try:
            fields = fields and json.loads(fields) or None
            args = domain and json.loads(domain) or []
            if read_id:
                args.append(['id', '=', read_id])
            context = context and json.loads(context) or {}
            default = request.session.context.copy()
            default.update(context)
            limit = limit and int(limit) or None
            offset = offset and int(offset) or None
            model = request.env[model].with_context(default)
            result = model.sudo().search_read(domain=args, fields=fields,
                                              offset=offset, limit=limit, order=order)
            return Response(json.dumps(result,
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    @http.route('/api/create', auth="none", type='http', methods=['POST'], csrf=False)
    def api_create(self, model='res.partner', values=None,
                   context=None, token=None, **kw):
        check_params({'token': token})
        ensure_db()
        check_token()
        try:
            values = values and json.loads(values) or {}
            context = context and json.loads(context) or {}
            default = request.session.context.copy()
            default.update(context)
            model = request.env[model].with_context(default)
            result = model.sudo().create(values)
            return Response(json.dumps(result,
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    @http.route('/api/write', auth="none", type='http', methods=['PUT'], csrf=False)
    def api_write(self, model='res.partner', ids=None,
                  values=None, context=None, token=None, **kw):
        check_params({'ids': ids, 'token': token})
        ensure_db()
        check_token()
        try:
            ids = ids and json.loads(ids) or []
            values = values and json.loads(values) or {}
            context = context and json.loads(context) or {}
            default = request.session.context.copy()
            default.update(context)
            model = request.env[model].with_context(default)
            records = model.browse(ids)
            result = records.sudo().write(values)
            return Response(json.dumps(result,
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    @http.route('/api/unlink', auth="none", type='http', methods=['DELETE'], csrf=False)
    def api_unlink(self, model='res.partner', ids=None, context=None, token=None, **kw):
        check_params({'ids': ids, 'token': token})
        ensure_db()
        check_token()
        try:
            ids = ids and json.loads(ids) or []
            context = context and json.loads(context) or {}
            default = request.session.context.copy()
            default.update(context)
            model = request.env[model].with_context(default)
            records = model.browse(ids)
            result = records.sudo().unlink()
            return Response(json.dumps(result,
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    @http.route('/api/call', auth="none", type='http', methods=['POST'], csrf=False)
    def api_call(self, model='res.partner', method=None, ids=None, context=None,
                 args=None, kwargs=None, token=None, **kw):
        check_params({'method': method, 'token': token})
        ensure_db()
        check_token()
        try:
            ids = ids and json.loads(ids) or []
            args = args and json.loads(args) or []
            kwargs = kwargs and json.loads(kwargs) or {}
            context = context and json.loads(context) or {}
            default = request.session.context.copy()
            default.update(context)
            model = request.env[model].with_context(default)
            records = model.browse(ids)
            result = getattr(records, method)(*args, **kwargs)
            return Response(json.dumps(result,
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    @http.route([
        '/api/report',
        '/api/report/<string:model>',
        '/api/report/<string:model>/<string:report>',
    ], auth="none", type='http', csrf=False)
    def api_report(self, model='res.partner', report=None, ids=None, Type="pdf",
                   context=None, args=None, kwargs=None, token=None, **kw):
        check_params({'report': report, 'ids': ids, 'token': token})
        ensure_db()
        check_token()
        try:
            ids = ids and json.loads(ids) or []
            args = args and json.loads(args) or []
            kwargs = kwargs and json.loads(kwargs) or {}
            context = context and json.loads(context) or {}
            default = request.session.context.copy()
            default.update(context)
            model = request.env[model].with_context(default)
            if Type == "html":
                data = request.env.ref(report).render_qweb_html(ids)[0]
                headers = [
                    ('Content-Type', 'text/html'),
                    ('Content-Length', len(data)),
                ]
                return request.make_response(data, headers=headers)
            else:
                data = request.env.ref(report).render_qweb_pdf(ids)[0]
                headers = [
                    ('Content-Type', 'application/pdf'),
                    ('Content-Length', len(data)),
                ]
                return request.make_response(data, headers=headers)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    @http.route([
        '/api/binary',
        '/api/binary/<string:xmlid>',
        '/api/binary/<string:xmlid>/<string:filename>',
        '/api/binary/<int:id>',
        '/api/binary/<int:id>/<string:filename>',
        '/api/binary/<int:id>-<string:unique>',
        '/api/binary/<int:id>-<string:unique>/<string:filename>',
        '/api/binary/<string:model>/<int:id>/<string:field>',
        '/api/binary/<string:model>/<int:id>/<string:field>/<string:filename>'],
        auth="none", type='http', csrf=False)
    def api_binary(self, token=None, xmlid=None, model='ir.attachment', binary_id=None,
                   field='datas', filename=None, filename_field='datas_fname',
                   unique=None, mimetype=None, **kw):
        ensure_db()
        check_token()
        try:
            status, headers, content = request.registry['ir.http'].binary_content(
                xmlid=xmlid, model=model, id=binary_id, field=field, unique=unique,
                filename=filename, filename_field=filename_field,
                mimetype=mimetype, download=True)
            if status == 200:
                content_base64 = base64.b64decode(content)
                headers.append(('Content-Length', len(content_base64)))
                return request.make_response(content_base64, headers=headers)
            else:
                abort({'error': status}, status=status)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)
