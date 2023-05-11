from flask_restful import Resource, fields, marshal_with, reqparse
from ..models import User, Board, List
from datetime import datetime
from .validations import *
from application.database import db
from application.cache import cache
from application.database_queries import get_board_by_id, get_board_user, get_card_by_id, get_card_user
from flask_security import auth_required, current_user

EC = {
    'B01': '{user_id} is required and must be an integer',
    'B02': '{board_name} is required and must be a non-empty string between 4 and 50 characters',
    'B03': '{board_name} must be a non-empty string between 4 and 50 characters'
}

board_output_fields = {
    'board_id': fields.Integer,
    'board_name': fields.String,
    'created': fields.DateTime(dt_format='iso8601') # rfc822, .strftime('%Y-%m-%d %H:%M:%S')
}

board_parser = reqparse.RequestParser()
board_parser.add_argument('user_id')
board_parser.add_argument('board_name')

class BoardAPI(Resource):
    @auth_required('token')
    @marshal_with(board_output_fields)
    def post(self):
        args = board_parser.parse_args()
        uid = validate_int(args.get('user_id'), 'B01', EC['B01'])
        bname = validate_str(args.get('board_name'), 'B02', EC['B02'])
        user = User.query.get(uid)
        
        if not user:
            raise NotFoundError(entity='User')
        
        if user != current_user:
            raise UnauthorizedError({'message':'You cannot add boards for other users.'})
        
        try:
            new_board = Board(board_name=bname, user_id=uid)
            db.session.add(new_board)
        except:
            db.session.rollback()
            raise InternalServerError()
        else:
            db.session.commit()
            return new_board, 201
    
    @auth_required('token')
    @marshal_with(board_output_fields)
    def get(self, board_id):
        board = get_board_by_id(board_id)
        if board:
            if get_board_user(board_id) == current_user:
                return board, 200
            else:
                raise UnauthorizedError({'message':'You cannot access a board you did not create.'})
        else:
            raise NotFoundError(entity='Board')
    
    @auth_required('token')
    @marshal_with(board_output_fields)
    def put(self, board_id):
        board = get_board_by_id(board_id)
        if not board:
            raise NotFoundError(entity='Board')
        
        if get_board_user(board_id) != current_user:
            raise UnauthorizedError(message='You cannot edit a board you did not create.')
        
        args = board_parser.parse_args()
        bname = validate_str(args.get('board_name'), 'B03', EC['B03'])
        
        try:
            board.board_name = bname
        except:
            db.session.rollback()
        else:
            db.session.commit()
            return board, 200
    
    @auth_required('token')
    def delete(self, board_id):
        board = get_board_by_id(board_id)
        
        if not board:
            raise NotFoundError(entity='Board')
        
        if get_board_user(board_id) != current_user:
            raise UnauthorizedError({'message':'You cannot delete a board you did not create.'})
        
        else:
            try:
                db.session.delete(board)
            except:
                db.session.rollback()
                raise InternalServerError()
            else:
                cache.delete_memoized(get_card_by_id)
                db.session.commit()
                return 'Successfully deleted', 200