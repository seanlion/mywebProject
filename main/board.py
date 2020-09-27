from main import *
from flask import Blueprint, send_from_directory
import os
from flask import jsonify

blueprint = Blueprint('board', __name__, url_prefix='/board')

@app.route("/")
def index():
    return render_template("index.html")

@blueprint.route("/comment_delete", methods=["POST"])
@login_required
def comment_delete():
    if request.method == "POST":
        id = request.form.get("id")
        comment_db = mongo.db.comment
        comment_data = comment_db.find_one({"_id" : ObjectId(id)})
        # 댓글을 적은 사람이 현재 접속해 있는 사람과 일치하는지 확인
        if comment_data.get("writer_id") == session.get("id"):
            comment_db.delete_one({"_id" : ObjectId(id)})
            return jsonify(func_request="success")
        else :
            return jsonify(func_request="error")
    else :
        abort(404)

@blueprint.route("/comment_edit", methods=["POST"])
@login_required
def comment_edit():
    if request.method == 'POST':
        id = request.form.get("id")
        comment_content = request.form.get("comment_content")

        comment_db = mongo.db.comment
        comment_data = comment_db.find_one({"_id" : ObjectId(id)})
        # 댓글 쓴 사람이랑 로그인한 사람이 같은지 비교
        if comment_data.get("writer_id") == session.get("id"):
            comment_db.update_one(
                {"_id" : ObjectId(id)},
                {"$set": {"comment_content": comment_content}}
            )
            return jsonify(func_requst="success")
        else :
            jsonify(func_requst="error")
    else:
        return abort(401)

@blueprint.route("/comment_list/<posting_id>", methods=["GET"])
@login_required
def comment_list(posting_id):
    comments_list = []
    comment_db = mongo.db.comment
    comments = comment_db.find({"posting_id": str(posting_id)}).sort([("created",-1)])
    for comment in comments :
        # 댓글 작성자인지 확인
        if comment.get("writer_id") == session.get("id"):
            comment_owner = True
        else : 
            comment_owner = False
        comments_list.append({
            "id": str(comment.get("_id")),
            "posting_id": comment.get("posting_id"),
            "name": comment.get("name"),
            "writer_id": comment.get("writer_id"),
            "comment_content": comment.get("comment_content"),
            "created": filter.format_datetime(comment.get("created")),
            "comment_owner": comment_owner
        })
    return jsonify(func_requst="success", lists=comments_list)

# 댓글 작성 기능 함수 작성
@blueprint.route("/comment_write", methods=["POST"])
@login_required
def comment_write():
    if request.method== 'POST':
        name = session.get("name")
        writer_id = session.get("id")
        posting_id = request.form.get('posting_id')
        comment_content = request.form.get('comment_content')
        current_utc_time = round(datetime.utcnow().timestamp()*1000)

        comment_db = mongo.db.comment
        post = {
            "posting_id" : str(posting_id),
            "name" : name,
            "writer_id" : writer_id,
            "comment_content": comment_content,
            "created": current_utc_time
        }
        comment_db.insert_one(post)
        return redirect(url_for('board.board_view',id_n=posting_id))


# url_for로 받았으니까 route 설정해줘야 함.
@blueprint.route("/upload_image", methods=["POST"])
def upload_image():
    if request.method == 'POST':
        file = request.files["image"]
        # file이 존재하고 우리가 허락한 확장자인지 확인하는 것
        # 근데 filename은 어디서 나온거지?
        if file and allowed_file(file.filename):
            filename = "{}.jpg".format(random_generator())
            print ("filename : ",filename)
            filename = secure_filename(filename)
            print ("secure_filename : ",filename)
            savefilepath = os.path.join(app.config['BOARD_IMAGE_PATH'],filename)
            print ("savefilepath : ",savefilepath)
            file.save(savefilepath)
            # redirect를 해버리니까 src가 깨지는 현상 발생
            return url_for('board.board_images',filename = filename)

@blueprint.route("/images/<filename>")
def board_images(filename):
    print("dir : ",send_from_directory(app.config["BOARD_IMAGE_PATH"], filename))
    return send_from_directory(app.config["BOARD_IMAGE_PATH"], filename)

@blueprint.route("/files/<filename>")
def board_files(filename):
    return send_from_directory(app.config['BOARD_ATTACH_PATH'],filename, as_attachment=True)


def delete_file(filename):
    abs_path = os.path.join(app.config['BOARD_ATTACH_PATH'],filename)
    if os.path.exists(abs_path):
        os.remove(abs_path)
        return True
    else :
        return False

@blueprint.route("/view/<id_n>") 
@login_required
def board_view(id_n):
    # id_n = request.args.get("id_n")
    # print(str(id_n))
    if id_n is not None:
        page = request.args.get("page")
        search_type = request.args.get("search_type")
        keyword = request.args.get("keyword")
    # 검색유형과 검색어를 담을 조건의 빈 쿼리를 만들자.
        board_db = mongo.db.board
        data = board_db.find_one({"_id": ObjectId(id_n)})

        if data is not None:
            result = {
                "id": data.get("_id"),
                "author": data.get("author"),
                "title": data.get("title"),
                "contents": data.get("contents"),
                "created": data.get("created"),
                "view": data.get("view"),
                "writer_id": data.get("writer_id", ""),
                "attachFile" : data.get("attachFile", "")
            }

        comment_db = mongo.db.comment
        # 이 게시글(포스팅)의 id에 맞는 코멘트를 모두 찾아야 함.
        comments = comment_db.find({"posting_id": str(data.get("_id"))})
        return render_template("view.html", result=result, page=page, search_type=search_type, keyword=keyword, comments=comments)
    else:
        return abort(404)


@blueprint.route("/write", methods=["GET","POST"])
@login_required
def board_write():
    # if session.get("id") is None:
    #     return redirect(url_for("make_login"))
    if request.method == "POST":

        filename= None
        # file input에 파일이 있는지 없는지 체크해야 함.
        if "attachFile" in request.files:
            # 파일 가져오기
            file = request.files["attachFile"]
            if file and allowed_file(file.filename):
                filename = check_filename(file.filename)
                file.save(os.path.join(app.config["BOARD_ATTACH_PATH"],filename))

        # 특정 name을 가진 input value를 get해야 함.
        name = request.form.get("name")
        title = request.form.get("title")
        contents = request.form.get("contents")
        # 이렇게만 적어도 files가 받아와지나?...
        request.files
        # 글 작성 시간도 찍어야 함. 표준시간으로 남겨야 한다.
        current_utc_time = round(datetime.utcnow().timestamp()*1000)
        # database랑 collection을 한꺼번에 생성
        board_db = mongo.db.board
        # collection에 넣을 document 생성
        post = {
            "author": name,
            "title": title,
            "contents": contents,
            "created": current_utc_time,
            "view": 0,
            'writer_id': session['id']
        }

        # filename이 있을 때
        if filename is not None:
            post['attachFile'] = filename

        # 작성한 데이터 삽입함.
        insert_data = board_db.insert_one(post)
        # 작성한 것의 상세페이지를 보려면 개별 상세페이지로 이동해야 한다.
        return redirect(url_for("board.board_view", id_n=insert_data.inserted_id)) 
    else:
        return render_template("write.html")


@blueprint.route("/list")
def lists():
    print("wrong?")
    # print(session)
    page = request.args.get("page",1, type=int)
    limit = request.args.get("limit",5, type=int)
    # 검색유형과 검색어를 받아오자.
    search_type = request.args.get("search_type",-1, type=int)
    keyword = request.args.get("keyword", "", type=str)
    # 검색유형과 검색어를 담을 조건의 빈 쿼리를 만들자.
    query = {}
    # search_list = []
    if search_type == 0:
        # search_list.append({"title": {"$regex":keyword}})
        query = {"title": {"$regex": keyword}}
    elif search_type == 1:
        query = {"contents": {"$regex": keyword}}
    elif search_type == 2:
        search_list = []
        search_list.append({"title": {"$regex": keyword}})
        search_list.append({"contents": {"$regex": keyword}})
        if len(search_list) > 0:
            query = {"$or":search_list}
        print(search_list)
    elif search_type == 3:
        query = {"author": {"$regex": keyword}}
    
    # 제목+내용의 경우 (search_list 안의 내용이 1개라도 있는 경우) OR 연산자를 붙여주자.
    print(query)
    # 디비에 담긴 모든 내용을 보여주자.
    board_db = mongo.db.board
    # 검색어에 맞는 결과만 나와야 한다. 검색을 안하면 어짜피 빈 오브젝트이기 때문에 모두 갖고 오겠지?
    datas = board_db.find(query).skip((page-1)*limit).limit(limit).sort("created",-1)
    # 미자믹 페이지 넘버를 구하기 = 전체 게시물 개수에서 limit을 나누고 그 수를 반올림하면 나오는 수
    total_article_cnt = board_db.find(query).count()
    last_page_num = math.ceil(total_article_cnt / limit)
    # 페이지 블럭은 5개로 정하기.
    page_block_size = 5
    block_locator_num = int((page-1)/page_block_size)
    block_first_pagenum = int((block_locator_num * page_block_size)+1)
    block_last_pagenum = math.ceil(block_first_pagenum+(page_block_size-1))

    return render_template(
        "list.html", 
        datas=datas, 
        page=page,
        limit=limit,
        last_page_num=last_page_num, 
        block_first_pagenum = block_first_pagenum, 
        block_last_pagenum=block_last_pagenum,
        search_type = search_type,
        keyword = keyword
        )


@blueprint.route('/edit/<id_n>', methods=['GET','POST'])
def post_edit(id_n):
    if request.method == 'GET':
        board_db = mongo.db.board
        data = board_db.find_one({"_id":ObjectId(id_n)})
        if data is None:
            flash("해당 게시물이 존재하지 않습니다.")
            return redirect(url_for('lists'))

        else:
            if session['id'] != data.get("writer_id"):
                flash("수정 권한이 없습니다.")
                return redirect(url_for('board_view/<id_n>'))
            else:
                return render_template('edit.html', data=data)
    else:
        # 바뀐 title, content 받아와야 함.
        title = request.form.get("title")
        contents = request.form.get("contents")
        # 파일 삭제를 위해 checkbox input을 받아와야 함.
        deleteoldFile = request.form.get('deleteoldFile')
        
        board_db = mongo.db.board
        data = board_db.find_one({"_id":ObjectId(id_n)})
        if session["id"] == data.get("writer_id"):
            # 여기서도 파일 추가 할 수 있어야 함.
            filename= None
            # file input에 파일이 있는지 없는지 체크해야 함.
            
            if "attachFile" in request.files:
                # 파일 가져오기
                print("attachFile : ",request.files["attachFile"])
                file = request.files["attachFile"]
                if file and allowed_file(file.filename):
                    filename = check_filename(file.filename)
                    file.save(os.path.join(app.config["BOARD_ATTACH_PATH"],filename))
                    # 예전파일 있으면 삭제하고 교체
                    if data.get("attachFile"):
                        delete_file(data.get("attachFile"))
            else :
                if deleteoldFile == "on":
                    filename = None
                    if data.get("attachFile"):
                        delete_file(data.get("attachFile"))
                else :
                    filename= data.get("attachFile")
            
            board_db.update_one(
                {"_id":ObjectId(id_n)},
                {"$set":
                    {
                      "title":title,
                      "contents":contents,
                      "attachFile": filename
                    }})
            flash("글이 수정되었습니다.")
            return redirect(url_for("board.board_view", id_n=id_n))

        else:
            flash("글 수정 권한이 없습니다.")
            return redirect(url_for('board.lists'))


@blueprint.route('/delete/<id_n>',methods=['GET'])
def post_delete(id_n):
    board_db = mongo.db.board
    data = board_db.find_one({"_id": ObjectId(id_n)})
    if data.get("writer_id") == session['id']:
        board_db.delete_one({"_id": ObjectId(id_n)})
        flash("글이 삭제 되었습니다.")
        return redirect(url_for("board.lists"))
    else: 
        flash("삭제 권한이 없습니다.")
        return redirect(url_for("board.lists"))
