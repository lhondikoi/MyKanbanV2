import marshal
from flask_restful import Resource, fields, marshal_with, reqparse
from ..models import User, Board, List, Card
from datetime import datetime
from .validations import *
from application.database import db
from application.cache import cache
from application.database_queries import get_card_by_id, get_list_by_id, get_card_user, get_card_board, get_card_list, get_list_board, get_list_user
from flask_security import auth_required, current_user
from time import perf_counter_ns

EC = {
    'C01': '{list_id} is required and must be an integer',
    'C02': '{title} is required and must be a non-empty string between 4 and 50 characters',
    'C03': '{title} must be non-empty string between 4 and 50 characters',
    'C04': '{deadline} should be in the format "yyyy-mm-ddThh:mm:ss"',
    'C05': '{deadline} cannot be lesser than the current time',
    'C06': '{completed} must be boolean (true/false)',
    'C07': 'Card is already in this list',
    'C08': 'List belongs to a different board'
}

card_output_fields = {
    'card_id':              fields.Integer,
    'title':                fields.String,
    'content':              fields.String,
    'completed':            fields.Boolean,
    'created':              fields.DateTime(dt_format='iso8601'), # rfc822, .strftime('%Y-%m-%d %H:%M:%S')
    'updated':              fields.DateTime(dt_format='iso8601'),
    'deadline':             fields.DateTime(dt_format='iso8601'),
    'completed_datetime':   fields.DateTime(dt_format='iso8601')
}

card_parser = reqparse.RequestParser()
card_parser.add_argument('list_id')
card_parser.add_argument('card_id')
card_parser.add_argument('title')
card_parser.add_argument('content')
card_parser.add_argument('deadline')
card_parser.add_argument('completed')

class CardAPI(Resource):
    @auth_required('token')
    @marshal_with(card_output_fields)
    def post(self):
        args = card_parser.parse_args()
        lid = validate_int(args.get('list_id'), 'C01', EC['C01'])
        ctitle = validate_str(args.get('title'), 'C02', EC['C02'])
        ccontent = args.get('content')
        cdeadline = validate_dt(args.get('deadline'), 'C04', EC['C04'])
        lst = get_list_by_id(lid)
        if not lst:
            raise NotFoundError(entity='List')
        
        if get_list_user(lid) != current_user:
            raise UnauthorizedError('You cannot add a card to a list you didn\'t create.')
        
        if cdeadline:
            if datetime.now() >= cdeadline:
                raise BusinessValidationError(  status_code=400,
                                                error_code='C05',
                                                error_message=EC['C05'])
        try:
            new_card = Card(list_id=lid, title=ctitle, content=ccontent, deadline=cdeadline)
            db.session.add(new_card)
        except:
            db.session.rollback()
            raise InternalServerError()
        else:
            db.session.commit()
            return get_card_by_id(new_card.card_id), 201
    
    @auth_required('token')
    @marshal_with(card_output_fields)
    def put(self, card_id):
        card = get_card_by_id(card_id)
        
        if not card:
            raise NotFoundError(entity='Card')
        
        if get_card_user(card_id) != current_user:
            raise UnauthorizedError('You cannot update a card that doesn\'t belong to you.')

        args = card_parser.parse_args()
        new_title = validate_str(args.get('title'), 'C03', EC['C03'], req='NE')
        new_content = args.get('content')
        new_deadline = validate_dt(args.get('deadline'), 'C04', EC['C04'])
        completed = validate_bool(args.get('completed'), 'C06', EC['C06'])
        
        if new_deadline and new_deadline != card.deadline:
            if datetime.now() >= new_deadline:
                raise BusinessValidationError(  status_code=400,
                                                error_code='C05',
                                                error_message=EC['C05'])
        try:
            if new_title is not None:
                card.title = new_title
            if new_content is not None:
                if new_content == '':
                    card.content = None
                else:
                    card.content = new_content
            if new_deadline is not None:
                card.deadline = new_deadline
        except:
            db.session.rollback()
            raise InternalServerError()
        else:
            cache.delete_memoized(get_card_by_id)
            db.session.commit()
            return get_card_by_id(card_id), 200

    @auth_required('token')
    @marshal_with(card_output_fields)
    def get(self, card_id):
        card = get_card_by_id(card_id)
        if card:
            if get_card_user(card_id) == current_user:
                return card, 200
            else:
                raise UnauthorizedError(message='You cannot access a card that doesn\'t belong to you.')
        else:
            raise NotFoundError(entity='Card')
    
    @auth_required('token')
    def delete(self, card_id):
        card = get_card_by_id(card_id)
        if not card:
            raise NotFoundError(entity='Card')
        
        if get_card_user(card_id) != current_user:
            raise UnauthorizedError('You cannot delete a card that doesn\'t belong to you.')
        
        else:
            try:
                db.session.delete(card)
            except:
                db.session.rollback()
            else:
                cache.delete_memoized(get_card_by_id)
                db.session.commit()
                return 'Successfully deleted', 200

class CardMoveAPI(Resource):
    @auth_required('token')
    @marshal_with(card_output_fields)
    def put(self, card_id, list_id):
        card = get_card_by_id(card_id)
        mlist = get_list_by_id(list_id)

        if not card:
            raise NotFoundError('Card')
        if not mlist:
            raise NotFoundError('List')

        if get_card_user(card_id) != current_user:
            raise UnauthorizedError('You cannot move a card that doesn\'t belong to you.')
        
        if get_list_user(list_id) != current_user:
            raise UnauthorizedError('You cannot move a card to a list that doesn\'t belong to you.')

        if get_card_list(card_id) == mlist:
            raise BusinessValidationError(status_code=400, error_code='C07', error_message=EC['C07'])
        
        if get_card_board(card_id) != get_list_board(list_id):
            raise BusinessValidationError(status_code=400, error_code='C08', error_message=EC['C08'])

        try:
            card.list_id = mlist.list_id
        except:
            db.session.rollback()
            raise InternalServerError()
        else:
            cache.delete_memoized(get_card_by_id)
            db.session.commit()
            return card, 200

class CardCompletionAPI(Resource):
    @auth_required('token')
    def put(self, card_id):
        card = get_card_by_id(card_id)
        args = card_parser.parse_args()
        completed = validate_bool(args.get('completed'), 'C06', EC['C06'])

        if not card:
            raise NotFoundError(entity='Card')
        
        if get_card_user(card_id) != current_user:
            raise UnauthorizedError('You cannot update a card that doesn\'t belong to you.')

        try:
            if completed is not None:
                card.completed = completed
            if completed is True:
                card.completed_datetime = datetime.now()
            else:
                card.completed_datetime = None
        except:
            db.session.rollback()
            raise InternalServerError()
        else:
            cache.delete_memoized(get_card_by_id)
            db.session.commit()
            return "Successfully updated", 200
