import requests
import os

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8003"
ENDPOINT = "/generate"
IMAGE_PATH = os.path.join("examples", "style_images", "zoom_2.jpg")
OUTPUT_PATH = "generated_image.png"  # 투명도를 지원하는 PNG로 변경
TEST_TEXT = "누가 투자안해주냐 십억"
TEST_LANG = "ko"

def test_generate_api():
    """
    Tests the /generate endpoint of the StyleText API.
    
    This script requires the 'requests' library.
    Install it using: pip install requests
    """
    url = BASE_URL + ENDPOINT

    # --- 1. Check if the image file exists ---
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Image file not found at '{IMAGE_PATH}'")
        print("예제 이미지가 있는지 확인해주세요.")
        return

    # --- 2. Prepare the request payload ---
    # The 'files' parameter is used for multipart/form-data uploads.
    # It expects a dictionary where the key is the form field name ('image').
    # The value is a tuple: (filename, file-like-object, content-type).
    try:
        with open(IMAGE_PATH, "rb") as image_file:
            files = {"image": (os.path.basename(IMAGE_PATH), image_file, "image/jpeg")} # 원본 이미지는 jpeg 유지
            data = {"text": TEST_TEXT, "language": TEST_LANG}

            # --- 3. Send the POST request ---
            print(f"Sending request to {url} with image '{IMAGE_PATH}'...")
            response = requests.post(url, files=files, data=data)
    except IOError as e:
        print(f"이미지 파일을 여는 중 오류 발생: {e}")
        return
    except requests.exceptions.RequestException as e:
        print(f"요청을 보내는 중 오류 발생: {e}")
        print("API 서버가 실행 중인지 확인해주세요.")
        return

    # --- 4. Process the response ---
    if response.status_code == 200:
        # If successful, the response content will be the image bytes.
        try:
            with open(OUTPUT_PATH, "wb") as output_file:
                output_file.write(response.content)
            print(f"성공! ✨ 이미지가 '{OUTPUT_PATH}'에 저장되었습니다.")
        except IOError as e:
            print(f"생성된 이미지 저장 중 오류 발생: {e}")
    else:
        # If there's an error, FastAPI usually returns a JSON with details.
        print(f"오류: 상태 코드 {response.status_code} 수신")
        try:
            print("Response JSON:", response.json())
        except requests.exceptions.JSONDecodeError:
            print("Response content:", response.text)

if __name__ == "__main__":
    test_generate_api()