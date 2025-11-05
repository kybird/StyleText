#!/bin/bash

# --- 변경할 부분 ---
IMAGE_NAME="styletext-server"  # 원하는 이미지 이름으로 변경하세요.
TAG="latest"               # 원하는 태그로 변경하세요.
# ------------------

# 이 스크립트 파일이 있는 디렉토리의 절대 경로를 찾습니다.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

# 프로젝트 최상단 디렉토리(스크립트 디렉토리의 부모)로 이동합니다.
# 이 명령 덕분에 어느 위치에서 스크립트를 실행해도 동일하게 동작합니다.
cd "$SCRIPT_DIR/.."

echo "############################################################"
echo "Project root directory: $(pwd)"
echo "Building Docker image: ${IMAGE_NAME}:${TAG}"
echo "############################################################"

# -t 옵션: 이미지 이름과 태그를 지정합니다.
# -f 옵션: 사용할 Dockerfile의 경로를 명시합니다. (이제 항상 'Docker/Dockerfile' 경로가 됩니다)
# . (점): Docker 빌드 컨텍스트를 현재 디렉토리(프로젝트 최상단)로 지정합니다.
docker build -t ${IMAGE_NAME}:${TAG} -f Docker/Dockerfile .

echo "Build finished."