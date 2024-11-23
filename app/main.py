# import logging.config

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
import os

from .model import load_model, generate_caption
from .utils import load_image_from_file
from .config import settings
from fastapi import Form

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for all origins (for local testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)



# Load the BLIP model once when the app starts
try:
    model, processor = load_model(settings.blip_model_name)
    # logger.info("BLIP model loaded successfully")
except Exception as e:
    # logger.exception("Failed to load BLIP model")
    raise RuntimeError("Could not load the model") from e


# Add this before your existing routes
app.mount("/home", StaticFiles(directory="frontend", html=True), name="static")

@app.get("/home")
async def serve_index():
    return FileResponse("frontend/index.html")

@app.get("/")
async def read_root():
    """Redirect to home page."""
    # logger.info("Root endpoint accessed, redirecting to home")
    return RedirectResponse(url="/home")

@app.post("/caption")
async def caption(image: UploadFile = File(...), text: str = Form(None)):
    """
    Generate a caption for an uploaded image.
    :param image: The uploaded image file.
    :param text: Optional text to guide the caption generation.
    :return: Generated caption.
    """
    try:
        # logger.info(f"Received caption request with file: {image.filename}")

        # Validate image content type
        if image.content_type not in ["image/jpeg", "image/png"]:
            # logger.warning(f"Invalid image format: {image.content_type}")
            raise HTTPException(status_code=400, detail="Invalid image format. Only JPEG and PNG are supported.")

        # Load and process the image
        image_data = await image.read()
        loaded_image = load_image_from_file(image_data)

        # Generate the caption
        caption = generate_caption(model, processor, loaded_image, text)
        # logger.info("Caption generated successfully")
        return {"caption": caption}

    except HTTPException as http_err:
        # logger.error(f"Client error: {http_err.detail}")
        raise
    except Exception as e:
        # logger.exception("Unexpected error in /caption endpoint")
        raise HTTPException(status_code=500, detail="Internal server error") from e
    finally:
        # Ensure the image file is closed
        await image.close()
        # logger.debug(f"Closed file: {image.filename}")
