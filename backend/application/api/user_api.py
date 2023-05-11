from flask_restful import Resource, fields, marshal_with, reqparse
from ..models import User, Board, List
from datetime import datetime
from .validations import *
from application.database import db
from flask_security import auth_required, current_user, hash_password

user_parser = reqparse.RequestParser()
user_parser.add_argument('email')
user_parser.add_argument('username')
user_parser.add_argument('password')

settings_parser = reqparse.RequestParser()
settings_parser.add_argument('monthly_report_format')
settings_parser.add_argument('daily_reminders')


user_output_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'username': fields.String,
    'created': fields.DateTime(dt_format='iso8601'),
    'monthly_report_format': fields.String,
    'send_daily_reminders': fields.Boolean
}

class UserAPI(Resource):
    @auth_required('token')
    @marshal_with(user_output_fields)
    def get(self):
        return current_user, 200

class SettingsAPI(Resource):
    @auth_required('token')
    def post(self):
        args = settings_parser.parse_args()
        report_pref = args.get('monthly_report_format')
        daily_r = validate_bool(args.get('daily_reminders'), 400, "Value must be the strings 'True' or 'False'.")
        if report_pref:
            current_user.monthly_report_format = report_pref
        if daily_r is not None:
            current_user.send_daily_reminders = daily_r
        db.session.commit()
        return {"status_code": 200, "message": "Successfully updated preferences!"}, 200