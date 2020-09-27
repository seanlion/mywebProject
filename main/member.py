from main import *
from flask import Blueprint

blueprint = Blueprint('member',__name__, url_prefix='/member')

@blueprint.route('/join', methods= ["GET","POST"])
def member_join():
    if request.method == 'POST':
        name = request.form.get("name", type=str)
        email = request.form.get("email", type=str)
        password = request.form.get("password", type=str)
        password2 = request.form.get("password2", type=str)
        if name == "" or email == "" or password == "" or password2 == "":
            flash('입력되지 않은 요소가 있습니다.')
            return render_template("join.html")

        if password != password2:
            flash('비밀번호와 비밀번호 확인이 일치하지 않습니다.')
            return render_template("join.html")

        members = mongo.db.members
        # 이메일이 중복인지 검사해야 함. 기존에 있는 이메일인지
        cnt = members.find({"email":email}).count()
        if cnt > 0:
            flash("중복된 이메일 주소입니다.")
            return render_template("join.html")
        # 중복 아니면 가입해야함. 이 때 가입시간도 기록.
        else:
            current_utc_time = round((datetime.utcnow().timestamp()) * 1000)
            post = {
                "name" : name,
                "email" : email,
                # 비밀번호 암호화해줌.
                "password" : hash_password(password),
                "join_datetime" : current_utc_time,
                "login_time" : 0,
                "login_count" : 0
            }
            members.insert_one(post)
            return redirect(url_for('member.make_login'))
    else :
        return render_template("join.html")

@blueprint.route('/login', methods=['GET','POST'])
def make_login():
    if request.method == 'POST':
        email = request.form.get("email", type=str)
        password = request.form.get("password", type=str)
        # 로그인 전에 페이지가 있으면 기억해야함. 
        next_url = request.form.get("next_url")
        members = mongo.db.members
        # 등록된 이메일인지 확인하기
        data = members.find_one({"email":email})
        if data is None :
            flash("회원 정보가 없습니다.")
            return render_template("login.html")
        # 이메일이 등록되었다면, 비밀번호가 일치하는지 확인하기
        else:
            # 비밀번호가 일치하면 로그인 페이지에서 홈이나 기존에 봤던데로 이동한다.
            # 암호화된 패스워드를 복호화시키고 유저가 입력한 패스워드와 비교한다.
            if check_password(data.get("password"),password):
                # session object에 정보를 담는다.
                session['email'] = email
                session['name'] = data.get("name")
                session['id'] = str(data.get("_id"))
                # print(session)
                # 세션 유지시간 변경 가능
                session.permanent = True
                # login.html에서 next_url을 같이 전송해주면 백엔드에서 next_url로 리다이렉트 해줌.
                if next_url is not None:
                    return redirect(next_url)
                else:
                    return redirect(url_for('board.lists'))
            else:
                flash("비밀번호가 일치하지 않습니다.")
                # return render_template("login.html")
                return redirect(url_for("member.make_login"))
        return "login complete" 
    else:
        next_url = request.args.get("next_url", type=str)
        if next_url is not None:
            print(next_url)
            return render_template("login.html", next_url=next_url) 
        return render_template("login.html")

# 로그아웃 기능 만들기
@blueprint.route('/logout')
def member_logout():
    try:
        del session["name"]
        del session['email']
        del session['id']
    except:
        pass
    return redirect(url_for('member.make_login'))
