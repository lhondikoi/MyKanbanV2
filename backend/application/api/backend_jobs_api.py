from flask_restful import Resource, fields, marshal_with, reqparse
from flask_security import current_user, auth_required

from application.database import db
from application.database_queries import get_list_by_id, get_board_by_id, get_list_board, get_list_user
from ..models import User, Board, List, Card
from .validations import *
from ..celery.tasks import list_export_csv, board_export_csv

from datetime import datetime
class TaskStatusAPI(Resource):
    @auth_required('token')
    def get(self, task_id):
        task = list_export_csv.AsyncResult(task_id)
        if task.state == 'PENDING':
            response = {
                'state': 'PENDING',
                'current': 0,
                'total': 1,
                'status': 'Export process will begin shortly...'
            }
        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1),
                'status': task.info.get('status', '')
            }
            if 'result' in task.info:
                response['result'] = task.info['result']
        else:
            response = {
                'state': task.state,
                'current': 1,
                'total': 1,
                'status': str(task.info)
            }
        return response, 200

class ExportListAPI(Resource):
    @auth_required('token')
    def get(self, list_id):
        if get_list_user(list_id) != current_user:
            return "You cannot export a list that belongs to a different user.", 401
        task = list_export_csv.apply_async(args=[list_id])
        return {'message': "The exported list will be available for download when it is ready.", 'task_id': task.id}, 202

class ExportBoardAPI(Resource):
    @auth_required('token')
    def get(self, board_id):
        if get_board_by_id(board_id).user != current_user:
            return "You cannot export a board that belongs to a different user.", 401
        task = board_export_csv.apply_async(args=[board_id])
        return {'message': "The exported board will be available for download when it is ready.", 'task_id': task.id}, 202