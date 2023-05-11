from flask_restful import Resource, fields, marshal_with, reqparse
from flask_security import auth_required, current_user
from datetime import datetime, timedelta

from ..models import User, Board, List
from .validations import *
from application.database import db
from application.database_queries import get_list_by_id

EC = {
    'S01': '{start_date} is required and must be in the format "yyyy-mm-dd"',
    'S02': '{end_date} is required and must be in the format "yyyy-mm-dd"',
    'S03': 'Date range cannot be greater than 84 days'
}

breakdown_output_fields = {
    'completed': fields.Integer,
    'pending': fields.Integer,
    'overdue': fields.Integer
}

timeline_output_fields = {
    'dates': fields.List(fields.String),
    'completed': fields.List(fields.Integer)
}

stats_parser = reqparse.RequestParser()
stats_parser.add_argument('user_id')
stats_parser.add_argument('list_id')
stats_parser.add_argument('start_date')
stats_parser.add_argument('end_date')

class BreakdownAPI(Resource):
    @auth_required('token')
    @marshal_with(breakdown_output_fields)
    def post(self):
        args = stats_parser.parse_args()
        uid = int(args.get('user_id'))
        lid = int(args.get('list_id'))
        out = {
            "completed": 0,
            "pending": 0,
            "overdue": 0
        }
        if lid == -1:
            user = User.query.get(uid)
            if not user:
                raise NotFoundError('User')
            for board in user.boards:
                for l in board.lists:
                    for card in l.cards:
                        if card.completed:
                            out['completed'] += 1
                        elif card.deadline and datetime.now() > card.deadline:
                            out['overdue'] += 1
                        else:
                            out['pending'] += 1
            return out, 200
        else:
            lst = get_list_by_id(lid)
            if not lst:
                raise NotFoundError('List')
            else:
                for card in lst.cards:
                    if card.completed:
                        out['completed'] += 1
                    elif card.deadline and datetime.now() > card.deadline:
                        out['overdue'] += 1
                    else:
                        out['pending'] += 1
            return out, 200

class TimelineAPI(Resource):
    @auth_required('token')
    @marshal_with(timeline_output_fields)
    def post(self):
        args = stats_parser.parse_args()
        uid = int(args.get('user_id'))
        user = User.query.get(uid)
        if user != current_user:
            raise UnauthorizedError({'message':'You cannot access statistics for other users.'})
        if not user:
            raise NotFoundError('User')
        args = stats_parser.parse_args()
        start_date = validate_date(args.get('start_date'), ecode='S01', emsg=EC['S01'])
        end_date = validate_date(args.get('end_date'), ecode='S02', emsg=EC['S02'])

        numdays = (end_date - start_date).days + 1
        if numdays > 84:
            raise BusinessValidationError(400, 'S03', EC['S03'])
        date_dict = {f'{start_date + timedelta(days=x)}': 0 for x in range(numdays)}
        for board in user.boards:
            for l in board.lists:
                for card in l.cards:
                    if card.completed and f'{card.completed_datetime.date()}' in date_dict:
                        date_dict[f'{card.completed_datetime.date()}'] += 1
        out = {
            'dates': [f'{start_date + timedelta(days=x)}' for x in range(numdays)],
            'completed': [date_dict[date] for date in [f'{start_date + timedelta(days=x)}' for x in range(numdays)]]
            }
        return out, 200