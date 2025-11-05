# 베이스 이미지로 Python 3.9 slim 버전을 사용합니다.
FROM python:3.9-slim

# 컨테이너 내의 작업 디렉토리를 /app 으로 설정합니다.
WORKDIR /app

# [추가된 부분] 누락된 시스템 라이브러리를 설치합니다.
# apt-get 패키지 리스트를 업데이트하고 libgl1-mesa-glx를 설치합니다.
# RUN 뒤에 불필요한 캐시를 삭제하여 이미지 크기를 최적화합니다.
# [수정된 부분] 변경된 패키지 이름으로 설치합니다.
# 기존에 설치하던 라이브러리 목록에 libgomp1을 추가합니다.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    ccache \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 파일을 먼저 복사합니다.
COPY requirements.txt .

# requirements.txt에 명시된 패키지들을 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트의 나머지 파일들을 작업 디렉토리로 복사합니다.
COPY . .

# 컨테이너의 8000번 포트를 외부에 노출합니다.
EXPOSE 8000

# 컨테이너가 시작될 때 uvicorn 서버를 실행합니다.
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]