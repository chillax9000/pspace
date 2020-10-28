import flask
import flask_login
import os
import flaskr.dao as dao
from flaskr.user import User
import sqlalchemy
import redis
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), "back.log"))
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("starting...")
login_manager = flask_login.LoginManager()
app = flask.Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
login_manager.init_app(app)

try:
    redis_client = redis.Redis(**dao.util.find_params_dict("host", "port", namespace="CACHE"))
    cache = dao.Cache(redis_client)
except Exception as e:
    if "redis_client" in globals():
        redis_client.close()
    logger.info(e)
    logger.info("Using dummy cache...")
    cache = dao.DummyCache()

try:
    dbname, user, pwd, host, port = \
        dao.util.find_params("name", "user", "pwd", "host", "port", namespace="DB")

    db_engine = sqlalchemy.create_engine(
        f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{dbname}")

    dao_users = dao.UsersDAO(db_engine, User)
    dao_defsrc = dao.DefinitionSrcDAO(db_engine, cache)
except Exception as e:
    if "db_engine" in globals():
        db_engine.dispose()
    logger.info(e)
    logger.info("Using dummy daos, no data to be read or written...")
    dao_users = dao.UsersDummyDAO(User)
    dao_defsrc = dao.DefinitionSrcDummyDAO(cache)


@login_manager.user_loader
def load_user(user_id):
    return dao_users.get(user_id)


from flaskr import views
