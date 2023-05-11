from flask import current_app as app
from flask_caching import Cache

cache = Cache(app)
app.app_context().push()