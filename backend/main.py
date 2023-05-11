from application.config import LocalDevelopmentConfig
from application.database import db
from application.models import User, Role, Board, List, Card
from application.celery.workers import celery, KanbanTask

from flask import Flask, send_from_directory
from flask_restful import Resource, Api, fields, marshal_with, reqparse
from flask_security import Security, SQLAlchemySessionUserDatastore, hash_password, auth_required
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(LocalDevelopmentConfig)
CORS(app)

# Setup database and API
db.init_app(app)
app.app_context().push()
api = Api(app)
app.app_context().push()

# Setup Flask Security
user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
security = Security(app, user_datastore)

# Configure Celery
celery.conf.update(
    broker_url = app.config['CELERY_BROKER_URL'],
    result_backend = app.config['CELERY_RESULT_BACKEND']
)
celery.Task = KanbanTask

# Sign up
user_parser = reqparse.RequestParser()
user_parser.add_argument('email')
user_parser.add_argument('username')
user_parser.add_argument('password')

class SignupAPI(Resource):
    def post(self):
        args = user_parser.parse_args()
        email = args.get('email')
        uname = args.get('username')
        pword = args.get('password')
        try:
            hashed_pword = hash_password(pword)
            user_datastore.create_user( email=email,
                                        username=uname,
                                        password=hashed_pword,
                                        monthly_report_format='html',
                                        send_daily_reminders=True,
                                        active = True
                                    )
        except Exception as e:
            db.session.rollback()
            return f'There was an error signing up due to {e}', 500
        else:
            db.session.commit()
            return "You have successfully registered", 200

# Export controller
@app.route('/download/<string:file_name>')
@auth_required('token')
def download(file_name):
    return send_from_directory(app.config['EXPORT_DIR'], file_name, as_attachment=True)


# importing restful api
from application.api.user_api import UserAPI, SettingsAPI
from application.api.frontend_api import UserBoardsAPI, BoardListsAPI, UserLists
from application.api.list_api import ListAPI, ListMoveDeleteAPI
from application.api.card_api import CardAPI, CardMoveAPI, CardCompletionAPI
from application.api.board_api import BoardAPI
from application.api.stats_api import BreakdownAPI, TimelineAPI
from application.api.backend_jobs_api import ExportListAPI, ExportBoardAPI, TaskStatusAPI

# adding resources
api.add_resource(TaskStatusAPI, '/api/task/<string:task_id>')

api.add_resource(SignupAPI, '/signup')
api.add_resource(UserAPI, '/api/user')
api.add_resource(SettingsAPI, '/api/settings')
api.add_resource(UserBoardsAPI, '/api/boards')
api.add_resource(BoardListsAPI, '/api/boardlists/<int:board_id>')
api.add_resource(UserLists, '/api/lists')

api.add_resource(BoardAPI, '/api/board','/api/board/<int:board_id>')
api.add_resource(ExportBoardAPI, '/api/board/<int:board_id>/export')    

api.add_resource(ListAPI, '/api/list','/api/list/<int:list_id>')
api.add_resource(ListMoveDeleteAPI, '/api/list/<int:list_id>/delete_move/<int:mlist_id>')
api.add_resource(ExportListAPI, '/api/list/<int:list_id>/export')    

api.add_resource(CardAPI, '/api/card','/api/card/<int:card_id>')
api.add_resource(CardMoveAPI, '/api/card/<int:card_id>/move_to_list/<int:list_id>')
api.add_resource(CardCompletionAPI, '/api/card/<int:card_id>/complete')

api.add_resource(BreakdownAPI, '/api/stats/breakdown')
api.add_resource(TimelineAPI, '/api/stats/timeline')

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000
    )
