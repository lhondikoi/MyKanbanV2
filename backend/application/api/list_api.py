from flask_restful import Resource, fields, marshal_with, reqparse
from ..models import User, Board, List
from datetime import datetime
from .validations import *
from application.database import db
from application.cache import cache
from application.database_queries import get_list_by_id, get_board_by_id, get_list_board, get_list_user, get_board_user, get_card_by_id
from flask_security import auth_required, current_user

EC = {
    'L01': '{board_id} is required and must be an integer',
    'L02': '{list_name} is required and must be a non-empty string between 4 and 50 characters',
    'L03': '{list_name} must be a non-empty string between 4 and 50 characters',
    'L04': 'Cannot move cards to a list which belongs to different board',
    'L05': 'Card is already in this list'
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

list_output_fields = {
    'board_id': fields.Integer,
    'list_id': fields.Integer,
    'list_name': fields.String,
    'cards': fields.List(fields.Nested(card_output_fields), default=[]),
    'created': fields.DateTime(dt_format='iso8601') # rfc822, .strftime('%Y-%m-%d %H:%M:%S')
}

list_parser = reqparse.RequestParser()
list_parser.add_argument('board_id')
list_parser.add_argument('list_name')

class ListAPI(Resource):

    @auth_required('token')
    @marshal_with(list_output_fields)
    def post(self):
        args = list_parser.parse_args()
        bid = validate_int(args.get('board_id'), 'L01', EC['L01'])
        lname = validate_str(args.get('list_name'), 'L02', EC['L02'])
        board = get_board_by_id(bid)
        
        if board is None:
            raise NotFoundError(entity='Board')
        
        if get_board_user(bid) != current_user:
            raise UnauthorizedError(message='You cannot create a list in a board that doesn\'t belong to you.')
        
        try:
            new_list = List(list_name=lname, board_id=bid)
            db.session.add(new_list)
        except:
            db.session.rollback()
            raise InternalServerError()
        else:
            db.session.commit()
            return get_list_by_id(new_list.list_id), 201

    @auth_required('token')
    @marshal_with(list_output_fields)
    def get(self, list_id):
        l = get_list_by_id(list_id)
        if l:
            if get_list_user(list_id) == current_user:
                return l, 200
            else:
                raise UnauthorizedError(message="You cannot access a list which you did not create.")
        else:
            raise NotFoundError(entity='List')

    @auth_required('token')
    @marshal_with(list_output_fields)
    def put(self, list_id):
        l = get_list_by_id(list_id)
        if not l:
            raise NotFoundError(entity='List')
        
        if get_list_user(list_id) != current_user:
            raise UnauthorizedError(message='You cannot update a list which you did not create.')
        
        args = list_parser.parse_args()
        lname = validate_str(args.get('list_name'), 'List', EC['L03'])
        
        try:
            l.list_name = lname
        except:
            db.session.rollback()
        else:
            db.session.commit()
            return l, 200

    @auth_required('token')
    def delete(self, list_id):
        l = get_list_by_id(list_id)
        if not l:
            raise NotFoundError(entity='List')
        
        if get_list_user(list_id) != current_user:
            raise UnauthorizedError(message='You cannot delete a list you did not create.')
        
        try:
            db.session.delete(l)
        except:
            db.session.rollback()
            raise InternalServerError()
        else:
            cache.delete_memoized(get_card_by_id)
            db.session.commit()
            return 'Successfully deleted', 200

class ListMoveDeleteAPI(Resource):
    @auth_required('token')
    def delete(self, list_id, mlist_id):
        l = get_list_by_id(list_id)
        mlist = get_list_by_id(mlist_id)

        if not l or not mlist:
            raise NotFoundError('List')
        
        if get_list_user(list_id) != current_user:
            raise UnauthorizedError(message='You cannot delete a list you did not create.')
        
        if get_list_user(mlist_id) != current_user:
            raise UnauthorizedError(message='You cannot move cards to a list that doesn\'t belong to you.')
        
        if l.board != mlist.board:
            raise BusinessValidationError(status_code=400, error_code='L04', error_message=EC['L04'])
        
        if l == mlist:
            raise BusinessValidationError(status_code=400, error_code='L05', error_message=EC['L05'])

        try:
            for card in l.cards:
                card.list_id = mlist.list_id
        except:
            db.session.rollback()
            raise InternalServerError()
        else:
            db.session.commit()

        try:
            db.session.delete(l)
        except:
            db.session.rollback()
            raise InternalServerError()
        else:
            db.session.commit()
            return 'Successfully moved cards and deleted', 200