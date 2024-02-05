from flask import request
from Games0App.extensions import db
from Games0App.models.log import Log
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os


class Logger:


    def log_event(self, json_log, function_name, log_type):

        if 'user_id' in json_log:
            user_id_ = json_log['user_id']
            json_log.pop('user_id')
        else:
            user_id_ = 0

        if 'issue_id' in json_log:
            issue_id_ = json_log['issue_id']
            json_log.pop('issue_id')
            prefix = 'R'
        else:
            issue_id_ = ''
            prefix = 'S'

        log_ip = ['max_auth_password_attempts', 'max_login_password_attempts', 'account_created',
                'successful_login', 'init_change_email', 'email_changed', 'init_change_password',
                'password_changed', 'init_delete_account', 'account_deleted', 'reset_password_email_sent',
                'password_reset', 'max_reset_password_email_attempts']
        if log_type in log_ip or 'init_reset_password' in log_type:
            try:
                ip_address_ = request.remote_addr
            except:
                ip_address_ = 'unknown'
        else:
            ip_address_ = ''

        count = 0
        while count < 10:
            unique_id_ = prefix + os.urandom(4).hex().upper()
            try:
                log = Log(
                    unique_id=unique_id_,
                    user_id=user_id_,
                    ip_address=ip_address_,
                    function_name=function_name,
                    log_type=log_type,
                    timestamp=datetime.utcnow(),
                    data=json_log,
                    issue_id=issue_id_
                )
                db.session.add(log)
                db.session.commit()
                break
            except IntegrityError:
                db.session.rollback()
                count += 1

        return unique_id_


    def get_log_by_unique_id(self, unique_id):
        log = Log.query.filter_by(unique_id=unique_id).first()
        return log


logger = Logger()
