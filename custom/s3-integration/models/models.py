# -*- coding: utf-8 -*-
"""
    s3-storage.models
    ~~~~~~~~~~~~~~~~~

    Use s3 as file storage mechanism

    :copyright: (c) 2017 by Marc Lijour, brolycjw.
    :license: MIT License, see LICENSE for more details.
"""

import hashlib
import base64

from odoo import models, fields, api

import boto3
from . import s3_helper


class S3Attachment(models.Model):
    """Extends ir.attachment to implement the S3 storage engine
    """
    _inherit = "ir.attachment"
    is_in_s3 = fields.Boolean()

    def _connect_to_S3_bucket(self, s3, bucket_name):
        s3_bucket = s3.Bucket(bucket_name)
        exists = s3_helper.bucket_exists(s3, bucket_name)

        if not exists:
            s3_bucket = s3.create_bucket(Bucket=bucket_name)
        return s3_bucket


    # def _file_read(self, fname):
    #     print('*****In S3******')
    #     storage = self._storage()
    #     if storage[:5] == 's3://':
    #         access_key_id, secret_key, bucket_name, encryption_enabled = s3_helper.parse_bucket_url(storage)
    #         s3 = s3_helper.get_resource(access_key_id, secret_key)
    #         s3_bucket = self._connect_to_S3_bucket(s3, bucket_name)
    #         if s3_bucket:
    #             print('*****Connected******')
    #         file_exists = s3_helper.object_exists(s3, s3_bucket.name, fname)
    #         if not file_exists:
    #             print("*****************File Not Exist S3 *******************")
    #             try:
    #                 read = super(S3Attachment, self)._file_read(fname, bin_size=False)
    #             except Exception:
    #                 return False
    #         else:
    #             print("*****************File Exist in S3*******************")
    #             s3_key = s3.Object(s3_bucket.name, fname)
    #             read = base64.b64encode(s3_key.get()['Body'].read())
    #     else:
    #         read = super(S3Attachment, self)._file_read(fname)
    #
    #     return read

    # @api.depends('store_fname', 'db_datas')
    # def _compute_datas(self):
    #     print("** Fake")
    #     bin_size = self._context.get('bin_size')
    #     for attach in self:
    #         print('S3S3',attach.is_in_s3)
    #         if attach.is_in_s3:
    #             print("*****************Read From S3*******************")
    #             attach.datas = self._file_read_s3(attach.store_fname)
    #         elif attach.store_fname and not attach.is_in_s3:
    #             print("*****************Read From Storage*******************")
    #             attach.datas = self._file_read(attach.store_fname)
    #         else:
    #             attach.datas = attach.db_datas

    # def _file_read(self, fname, bin_size=False):
    #     s3client = boto3.client(
    #         's3',
    #         region_name='us-east-1'
    #     )
    #     storage = self._storage()
    #     if storage[:5] == 's3://':
    #         access_key_id, secret_key, bucket_name, encryption_enabled = s3_helper.parse_bucket_url(storage)
    #         s3 = s3_helper.get_resource(access_key_id, secret_key)
    #         s3_bucket = self._connect_to_S3_bucket(s3, bucket_name)
    #         s3_key = s3.Object(s3_bucket.name, 'dev14/' + fname)
    #         print(s3_key)
    #         # data = s3_key.get()
    #         read = s3_key.get()['Body'].read()
    #
    #         # body = obj.get()['Body'].read()
    #         # print(s3_key)
    #         return read
    #         # return base64.b64encode(b"".join(s3_key.get()['Body'].read()))

    def _file_write(self, value, checksum):
        print("Hit here Write to S3")
        storage = self._storage()
        if storage[:5] == 's3://':
            access_key_id, secret_key, bucket_name, encryption_enabled = s3_helper.parse_bucket_url(storage)
            s3 = s3_helper.get_resource(access_key_id, secret_key)
            s3_bucket = self._connect_to_S3_bucket(s3, bucket_name)
            bin_value = base64.b64decode(value)
            fname = hashlib.sha1(bin_value).hexdigest()
            if encryption_enabled:
                s3.Object(s3_bucket.name, fname).put(Body=bin_value, ServerSideEncryption='AES256')
            else:
                s3.Object(s3_bucket.name, fname).put(Body=bin_value)

        else: # falling back on Odoo's local filestore
            fname = super(S3Attachment, self)._file_write(value, checksum)

        return fname

    # def _get_datas_related_values(self, data, mimetype):
    #     # compute the fields that depend on datas
    #     bin_data = base64.b64decode(data) if data else b''
    #     values = {
    #         'file_size': len(bin_data),
    #         'checksum': self._compute_checksum(bin_data),
    #         'index_content': self._index(bin_data, mimetype),
    #         'store_fname': False,
    #         'db_datas': data,
    #     }
    #     if data and self._storage() != 'db':
    #
    #         if self.res_model not in ['ir.ui.menu', 'ir.ui.view', 'ir.module.module']:
    #             print('****Store TO S3 ******')
    #             values['store_fname'] = self._file_write_s3(data, values['checksum'])
    #             values['is_in_s3'] = True
    #             values['db_datas'] = False
    #         else:
    #             print('****Store TO Local ******')
    #             values['store_fname'] = self._file_write(data, values['checksum'])
    #
    #     return values







