from flask_restful import Resource, fields, marshal_with, reqparse
from flask_security import current_user, auth_required

from application.database import db
from application.database_queries import get_board_by_id, get_board_user, get_list_board
from ..models import User, Board, List
from .validations import *

board_output_fields = {
    'user_id': fields.Integer,
    'board_id': fields.Integer,
    'board_name': fields.String,
    'created': fields.DateTime(dt_format='iso8601') # rfc822, .strftime('%Y-%m-%d %H:%M:%S')
}

card_output_fields = {
    'list_id': fields.Integer,
    'card_id': fields.Integer,
    'title': fields.String,
    'content': fields.String,
    'completed': fields.Boolean,
    'created': fields.DateTime(dt_format='iso8601'), # rfc822, .strftime('%Y-%m-%d %H:%M:%S')
    'updated': fields.DateTime(dt_format='iso8601'),
    'deadline': fields.DateTime(dt_format='iso8601'),
    'completed_datetime': fields.DateTime(dt_format='iso8601')
}

boardlists_output_fields = {
    'board_id': fields.Integer,
    'list_id': fields.Integer,
    'list_name': fields.String,
    'created': fields.DateTime(dt_format='iso8601'), # rfc822, .strftime('%Y-%m-%d %H:%M:%S')
    'cards': fields.List(fields.Nested(card_output_fields), default=[])
}

lists_output_fields = {
    'list_id': fields.Integer,
    'list_name': fields.String,
    'board_name': fields.String
}

class UserBoardsAPI(Resource):
    @auth_required('token')
    @marshal_with(board_output_fields)
    def get(self):
        return current_user.boards, 200

class UserLists(Resource):
    @auth_required('token')
    @marshal_with(lists_output_fields)
    def get(self):
        data = []
        for board in current_user.boards:
            for lst in board.lists:
                lst.board_name = get_list_board(lst.list_id).board_name
                data.append(lst)
        return data, 200

class BoardListsAPI(Resource):
    @auth_required('token')
    @marshal_with(boardlists_output_fields)
    def get(self, board_id):
        board = get_board_by_id(board_id)
        if get_board_user(board_id) == current_user:
            return board.lists, 200
        else:
            return "You can view lists of boards you own", 401