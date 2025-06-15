from urllib.parse import urlparse
import cloudinary
import cloudinary.uploader
from app.core.config import settings

url = urlparse(settings.CLOUDINARY_URL)

cloudinary.config(
  cloud_name=url.hostname,
  api_key=url.username,
  api_secret=url.password,
  api_url=settings.CLOUDINARY_URL,
  secure=True
)

async def upload_image_to_cloud(file):
    contents = await file.read()
    result = cloudinary.uploader.upload(contents, resource_type="image")
    return result["secure_url"]