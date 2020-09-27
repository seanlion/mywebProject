from functools import wraps
from main import session, redirect, url_for,request,ALLOWED_EXTENSIONS
from string import ascii_lowercase, ascii_uppercase, digits
from werkzeug.security import generate_password_hash, check_password_hash
import random
import re,os

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("id") is None or session.get("id") == "":
            # request.url은 login_required가 호출된 페이지의 url이다. 그걸 next_url로 받음.
            return redirect(url_for("member.make_login", next_url=request.url))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def check_filename(filename):
    reg = re.compile("[^A-Za-z0-9_.가-힝-]")
    # 파일 경로를 받아와야 함.
    for s in os.path.sep, os.path.altsep:
        if s:
            # replace의 기대결과는 어떤 형식인지 알아보기
            filename = filename.replace(s," ")
            filename = str(reg.sub('', '_'.join(filename.split()))).strip("._")
    print("check_filename : ",filename)
    return filename

def random_generator(length=8):
    print("ascii:",ascii_uppercase)
    char = digits + ascii_lowercase + ascii_uppercase
    print("char: ",char)
    return "".join(random.sample(char,length))


def hash_password(password):
    return generate_password_hash(password)

def check_password(hashed_password, user_password):
    return check_password_hash(hashed_password, user_password)