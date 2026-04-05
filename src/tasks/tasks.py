import asyncio
import time
import os
import logging

from src.database import async_session_maker_null_pool
from src.tasks.celery_app import celery_instance
from PIL import Image

from src.utils.db_manager import DBManager


@celery_instance.task
def test_task():
    time.sleep(5)
    print("Я закончил")


# @celery_instance.task
def resize_image(image_path: str):
    logging.debug(f"Call resize_image() with {image_path=}")
    sizes = [600, 300, 150]
    output_folder = "src/static/images"

    img = Image.open(image_path)

    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)

    for size in sizes:
        img_resized = img.resize(
            (size, int(img.height * (size / img.width))), Image.Resampling.LANCZOS
        )

        new_file_name = f"{name}_{size}px{ext}"

        output_path = os.path.join(output_folder, new_file_name)

        img_resized.save(output_path)


    logging.info(f"Изображение сохранено в следующих размерах: {sizes} в папке {output_folder}")



async def get_bookings_with_today_checkin_helper():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        logging.debug(f"Launch get_bookings_with_today_checkin_helper()")
        bookings = await db.bookings.get_bookings_with_today_checkin()
        print(f"{bookings}")


@celery_instance.task(name="booking_today_chekin")
def send_emails_to_user_with_today_checkin():
    asyncio.run(get_bookings_with_today_checkin_helper())
