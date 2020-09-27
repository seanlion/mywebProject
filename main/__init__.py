from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import make_response
from flask import session
from flask_pymongo import PyMongo
from datetime import datetime
from datetime import timedelta
from bson.objectid import ObjectId
from flask import abort
import math,os
from flask_jsglue import JSGlue
from flask import flash
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, template_folder='template')
csrf = CSRFProtect(app)
jsglue = JSGlue(app)
# 도커컨테이너를 네트워크에 연결시키기위해 localhost를 mongo로 변경
app.config["MONGO_URI"]="mongodb://mongo:27017/my_test"
mongo = PyMongo(app)
app.secret_key = 'secret'
# app.config['EXPLAIN_TEMPLATE_LOADING'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Ubuntu로 파일을 옮기기 위해 경로 수정
# BOARD_IMAGE_PATH = "/home/seung/myweb/images"
# BOARD_ATTACH_PATH = "/home/seung/myweb/files"
# docker에 올리는 용으로 다시 경로 설정
BOARD_IMAGE_PATH = "/images"
BOARD_ATTACH_PATH = "/files"

app.config["BOARD_IMAGE_PATH"] = BOARD_IMAGE_PATH
app.config["BOARD_ATTACH_PATH"] = BOARD_ATTACH_PATH
ALLOWED_EXTENSIONS = set(['txt','png','pdf','jpg', 'jpeg','gif'])

# path가 없으면 path를 만드는 로직 추가
if not os.path.exists(app.config["BOARD_IMAGE_PATH"]):
    os.mkdir(app.config["BOARD_IMAGE_PATH"])

if not os.path.exists(app.config["BOARD_ATTACH_PATH"]):
    os.mkdir(app.config["BOARD_ATTACH_PATH"])


from .common import login_required, allowed_file, random_generator, check_filename, hash_password, check_password
from .filter import format_datetime
from . import filter
from . import board
from . import member

app.register_blueprint(board.blueprint)
app.register_blueprint(member.blueprint)
app.register_blueprint(filter.blueprint)