from main import app
from main import datetime
from flask import Blueprint

blueprint = Blueprint('filter', __name__)

@blueprint.app_template_filter()
def format_datetime(time_int):
    if time_int is None:
        return ""
    else:
        #  일단 현재시간의 타임스탬프(클라이언트의 로컬 시간)를 구해야함.
        #  현재 클라이언트 시간을 가지고 datetime 객체를 만들어주는 함수 사용. #  뒤에는 utc datetime 객체를 반환해주는 함수. 이 2개를 빼면 utc 시간대와 로컬 시간대의 시간 차이가 나옴. 그 숫자를 구해야 함.
        now_timestamp = datetime.now()
        offset = now_timestamp - datetime.utcnow()
        # print(offset)
         # board_view 함수의 result에서 받아온 tiemstamp는 second 기준이니까 다시 밀리세컨드 기준으로 만들어야 함. 그러려면 1000을 나눠줘야 함. 그 다음 timestamp를 datetime 객체로 만들어주는 함수 사용하고 거기에 offset을 더해줌.(db에 저장된 utc 시간 + 시간차 = 로컬시간대의 현재 시간이 됨.)
        time_int = datetime.fromtimestamp(int(time_int) / 1000) + offset
        return time_int.strftime('%Y-%m-%d %H:%M:%S')

