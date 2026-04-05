import shutil

from fastapi import APIRouter, UploadFile
from starlette.background import BackgroundTasks

from src.tasks.tasks import resize_image

router = APIRouter(prefix="/images", tags=["Hotels Images"])


@router.post("")
def upload_image(file: UploadFile, background_tasks: BackgroundTasks):
    image_path = f"src/static/images/{file.filename}"
    with open(image_path, "wb+") as new_file:
        shutil.copyfileobj(file.file, new_file)

    background_tasks.add_task(resize_image, image_path)
