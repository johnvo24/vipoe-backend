import cloudinary
import cloudinary.uploader
from app.core.config import settings

cloudinary.config(
  cloud_name=settings.CLOUDINARY_URL.split("@")[1],
  api_key=settings.CLOUDINARY_URL.split("//")[1].split(":")[0],
  api_secret=settings.CLOUDINARY_URL.split(":")[2].split("@")[0],
  secure=True
)

async def upload_image_to_cloud(file, folder="vipoe/user_avatars"):
  contents = await file.read()
  result = cloudinary.uploader.upload(contents, resource_type="image", folder=folder)
  if "error" in result:
    raise Exception(f"Error uploading image: {result['error']}")
  return result["secure_url"]