from django.db import models
from django.core.files.storage import default_storage
import logging

from .project_models import ServiceCategory
from .partner_models import Instructor
from .about_models import About

logger = logging.getLogger(__name__)


class Media(models.Model):
    about = models.ForeignKey(
        About,
        related_name='medias',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='About'
    )
    category = models.ForeignKey(
        ServiceCategory,
        related_name='medias',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Service category'
    )
    partner = models.ForeignKey(
        Instructor,
        related_name='medias',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Partner'
    )
    image = models.ImageField(
        upload_to='images/',
        verbose_name='Image'
    )
    video = models.FileField(
        upload_to='videos/',
        null=True,
        blank=True,
        verbose_name='Video'
    )
    is_home_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Home page background image'
    )
    is_about_page_background_image = models.BooleanField(
        default=False,
        verbose_name='About page background image'
    )
    is_contact_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Contact page background image'
    )
    is_project_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Project page background image'
    )
    is_service_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Service page background image'
    )
    is_courses_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Courses page background image'
    )
    is_tests_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Tests pages background image'
    )
    is_footer_background_image = models.BooleanField(
        default=False,
        verbose_name='Footer background image'
    )
    is_abroad_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Study abroad page background image'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    class Meta:
        verbose_name = 'Media'
        verbose_name_plural = 'Media'

    @property
    def webp_url(self):
        return self.image.url

    def delete_files(self):
        if not self.image:
            return

        image_name = self.image.name
        image_id = self.pk

        logger.info(f"[IMAGE DELETE FILES] Deleting files (Image ID: {image_id}, File: {image_name})")

        try:
            storage = default_storage

            if image_name.lower().endswith('.webp'):
                logger.info(f"[IMAGE DELETE FILES] WebP file found: {image_name}")
                base_name = image_name.rsplit('.', 1)[0]
                possible_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
                for ext in possible_extensions:
                    original_name = base_name + ext
                    if storage.exists(original_name):
                        try:
                            storage.delete(original_name)
                            logger.info(f"[IMAGE DELETE FILES] Original file deleted: {original_name}")
                        except Exception as e:
                            logger.error(f"[IMAGE DELETE FILES] Error deleting original file ({original_name}): {e}")

                if storage.exists(image_name):
                    storage.delete(image_name)
                    logger.info(f"[IMAGE DELETE FILES] WebP file deleted: {image_name}")
                else:
                    logger.warning(f"[IMAGE DELETE FILES] WebP file not found: {image_name}")
            else:
                logger.info(f"[IMAGE DELETE FILES] Original format file found: {image_name}")
                webp_name = image_name.rsplit('.', 1)[0] + '.webp'
                if storage.exists(webp_name):
                    try:
                        storage.delete(webp_name)
                        logger.info(f"[IMAGE DELETE FILES] WebP version deleted: {webp_name}")
                    except Exception as e:
                        logger.error(f"[IMAGE DELETE FILES] Error deleting WebP version ({webp_name}): {e}")

                if storage.exists(image_name):
                    storage.delete(image_name)
                    logger.info(f"[IMAGE DELETE FILES] Original file deleted: {image_name}")
                else:
                    logger.warning(f"[IMAGE DELETE FILES] Original file not found: {image_name}")

            logger.info(f"[IMAGE DELETE FILES] Files successfully deleted (Image ID: {image_id})")
        except Exception as e:
            logger.error(f"[IMAGE DELETE FILES] Error occurred (Image ID: {image_id}): {e}")

    def delete(self, *args, **kwargs):
        image_id = self.pk
        logger.info(f"[IMAGE DELETE] Deleting image (Image ID: {image_id})")

        self.delete_files()

        super().delete(*args, **kwargs)

        logger.info(f"[IMAGE DELETE] Image successfully deleted (Image ID: {image_id})")
