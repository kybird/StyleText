import os
import sys
import io
import cv2
import numpy as np
import uuid
from enum import Enum
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image
from pydantic import BaseModel

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from engine.synthesisers import ImageSynthesiser
from utils.config import load_config
from engine import text_drawers, predictors
from utils.logging import get_logger

# --- Enums and Models ---

class Language(str, Enum):
    en = "en"
    ch = "ch"
    ko = "ko"

class Message(BaseModel):
    message: str
    endpoints: list[str]


# --- Global State ---

# Using a dictionary to hold the synthesiser to avoid direct global modification issues in some contexts
state = {"synthesiser": None}


# --- Synthesiser Initialisation ---

def initialize_synthesiser(config_path: str = "configs/config.yml") -> ImageSynthesiser:
    """
    Loads configuration and initializes the ImageSynthesiser.
    This is an unconventional way to instantiate, tailored to the project's structure.
    """
    config = load_config(config_path)

    # Create instance without calling __init__ to bypass CLI arg dependencies
    synth = object.__new__(ImageSynthesiser)
    synth.config = config
    synth.output_dir = config["Global"]["output_dir"]

    os.makedirs(synth.output_dir, exist_ok=True)

    log_path = os.path.join(synth.output_dir, "predict.log")
    synth.logger = get_logger(log_file=log_path)
    synth.text_drawer = text_drawers.StdTextDrawer(config)

    predictor_method = config["Predictor"]["method"]
    synth.predictor = getattr(predictors, predictor_method)(config)

    synth.logger.info("ImageSynthesiser initialized successfully.")
    return synth


# --- FastAPI App ---

app = FastAPI(
    title="StyleText Image Generation API",
    description="API for generating styled text images",
)

@app.on_event("startup")
async def startup_event():
    """Initialise the synthesiser on application startup."""
    try:
        state["synthesiser"] = initialize_synthesiser()
    except Exception as e:
        print(f"FATAL: Failed to initialize synthesiser: {e}")
        state["synthesiser"] = None


# --- Helper Functions ---

async def decode_image(file: UploadFile) -> np.ndarray:
    """Reads and decodes an uploaded image file."""
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image format or corrupted file.")
    return img

def resize_image_to_height_32(img: np.ndarray) -> np.ndarray:
    """
    이미지 높이를 32로 조절하면서 가로세로 비율을 유지합니다.
    """
    target_height = 32
    h, w, _ = img.shape

    # 이미 높이가 32이면 리사이즈하지 않음
    if h == target_height:
        return img

    aspect_ratio = w / h
    target_width = int(target_height * aspect_ratio)
    return cv2.resize(img, (target_width, target_height), interpolation=cv2.INTER_AREA)

def encode_image_to_png(img: np.ndarray) -> bytes:
    """
    투명도를 지원하는 PNG 형식으로 이미지를 인코딩합니다.
    이미지는 BGRA 4채널 형식이어야 합니다.
    """
    success, encoded_img = cv2.imencode('.png', img)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to encode image to PNG.")
    return encoded_img.tobytes()


# --- API Endpoints ---

@app.post("/generate")
async def generate_image(
    image: UploadFile = File(..., description="Style image file"),
    text: str = Form(..., description="Text to generate", min_length=1),
    language: Language = Form(Language.en.value, description="Language for text rendering")
):
    """
    Generate a new image with the provided text in the style of the input image.
    """
    synthesiser = state.get("synthesiser")
    if not synthesiser:
        raise HTTPException(status_code=503, detail="Synthesiser is not available or failed to initialize.")

    try:
        # 1. Decode style image
        style_image_orig = await decode_image(image)
        original_height, original_width, _ = style_image_orig.shape
        # 2. Resize image to have a height of 32, maintaining aspect ratio
        style_image_resized = resize_image_to_height_32(style_image_orig)

        # 3. Generate new image using the resized image
        result = synthesiser.synth_image(text.strip(), style_image_resized, language.value)
        
        fake_text_bgr = result["fake_text"]
        fake_sk = result["fake_sk"]
        fake_fusion = result["fake_fusion"]
        cv2.imwrite("fake_text.png", fake_text_bgr)
        cv2.imwrite("fake_sk.png", fake_sk)
        cv2.imwrite("fake_fusion.png", fake_fusion)
        # 3. fake_text_bgr에서 직접 알파 마스크 생성
        # 배경색(128, 128, 128)에 가까운 영역을 투명하게 처리
        gray_background_color = 128
        # 각 채널이 120~135 범위에 있는 픽셀을 배경으로 간주
        lower_bound = np.array([120, 120, 120])
        upper_bound = np.array([135, 135, 135])
        
        # 배경 영역은 1, 글자 영역은 0인 마스크 생성
        background_mask = cv2.inRange(fake_text_bgr, lower_bound, upper_bound)
        # 마스크 반전 (배경: 0, 글자: 255)
        alpha_mask = cv2.bitwise_not(background_mask)

        b_channel, g_channel, r_channel = cv2.split(fake_text_bgr)
        # alpha_mask는 2D 배열이므로 3D로 확장할 필요 없음
        fake_text_bgra = cv2.merge((b_channel, g_channel, r_channel, alpha_mask))

        # 4. Resize the final image back to the original input size
        # INTER_LANCZOS4 is a high-quality upscaling interpolation method
        final_image_bgra = cv2.resize(fake_text_bgra, (original_width, original_height), interpolation=cv2.INTER_LANCZOS4)

        # --- 파일 저장 로직 수정 ---
        # 고유한 요청 ID 생성
        request_id = str(uuid.uuid4())
        output_dir = synthesiser.output_dir

        # 1. 알파 마스크가 적용된 최종 이미지를 PNG 파일로 저장
        final_filename = f"{request_id}_text.png"
        final_save_path = os.path.join(output_dir, final_filename)
        cv2.imwrite(final_save_path, final_image_bgra)

        # 2. (선택) 원본 fake_sk 마스크도 저장 (그레이스케일로 변환하여 저장)
        sk_filename = f"{request_id}_fake_sk.png"
        sk_save_path = os.path.join(output_dir, sk_filename)
        if len(fake_sk.shape) == 3:
            fake_sk_gray_save = cv2.cvtColor(fake_sk, cv2.COLOR_BGR2GRAY)
        else:
            fake_sk_gray_save = fake_sk
        cv2.imwrite(sk_save_path, fake_sk_gray_save)

        fs_filename = f"{request_id}_fusion.png"
        fs_save_path = os.path.join(output_dir, fs_filename)
        cv2.imwrite(fs_save_path, fake_fusion)

        mask_filename = f"{request_id}_mask.png"
        mask_save_path = os.path.join(output_dir, mask_filename)
        cv2.imwrite(mask_save_path, alpha_mask)
        # 5. PNG로 인코딩하여 반환
        img_bytes = encode_image_to_png(final_image_bgra)
        return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")

    except HTTPException as http_exc:
        # Re-raise HTTPException to let FastAPI handle it
        raise http_exc
    except Exception as e:
        # Catch any other unexpected errors during the process
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.get("/", response_model=Message)
async def root():
    """API root, provides basic information."""
    return {
        "message": "StyleText Image Generation API",
        "endpoints": ["/generate (POST)"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)