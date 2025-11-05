#!/bin/bash

# --- 설정 부분 ---
IMAGE_NAME="styletext-server" # build.sh에서 사용한 이미지 이름과 동일해야 합니다.
CONTAINER_NAME="styletext-app"
# ------------------

# 이 스크립트 파일이 있는 디렉토리의 절대 경로를 찾습니다.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

# 프로젝트 최상단 디렉토리(스크립트 디렉토리의 부모)로 이동합니다.
# 이 명령 덕분에 어느 위치에서 스크립트를 실행해도 동일하게 동작합니다.
cd "$SCRIPT_DIR/.."

# Stop and remove the container if it already exists
echo "Stopping and removing old container: $CONTAINER_NAME"
docker stop $CONTAINER_NAME >/dev/null 2>&1
docker rm $CONTAINER_NAME >/dev/null 2>&1

# Run the new container
echo "Running new container '$CONTAINER_NAME' from image '$IMAGE_NAME'"
echo "Current directory: $(pwd)" # 현재 경로가 프로젝트 최상단인지 확인

# 아래 두 docker run 명령어 중 사용할 것 하나의 주석을 제거하고 사용하세요.

# 1. 컨테이너를 백그라운드에서 실행 (Detached mode)
docker run --rm -d --name $CONTAINER_NAME -p 8003:8000 $IMAGE_NAME

# 2. 컨테이너에 직접 접속하여 bash 셸 실행 (Interactive mode)
#    컨테이너 내부를 확인할 때 유용합니다.
# docker run --rm -it --name $CONTAINER_NAME -p 8003:8000 $IMAGE_NAME /bin/bash