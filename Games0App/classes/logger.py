from flask import request
from Games0App.extensions import db
from Games0App.models.log import Log
from datetime import datetime
import os


class Logger:


    def log_event(self, json_log, function_name, log_type):
        if 'user_id' in json_log:
            user_id_ = json_log['user_id']
            json_log.pop('user_id')
        else:
            user_id_ = 0
        unique_id_ = 'S' + os.urandom(4).hex().upper()
        try:
            ip_address_ = request.remote_addr
        except:
            ip_address_ = 'unknown'
        log = Log(
            unique_id=unique_id_,
            user_id=user_id_,
            ip_address=ip_address_,
            function_name=function_name,
            log_type=log_type,
            timestamp=datetime.utcnow(),
            data=json_log
        )
        db.session.add(log)
        db.session.commit()

        return unique_id_
