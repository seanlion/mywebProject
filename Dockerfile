FROM tiangolo/uwsgi-nginx-flask:python3.7

RUN pip3 install Flask Flask-PyMongo Flask-WTF Flask-JSGlue
# 앱 실행에 필요한 파일을 모두 도커로 복사
COPY . /app 
# 작업경로 생성해서 새로운 도커 이미지 생성
WORKDIR /app