from django.db import models
from django.core.files.storage import default_storage
import logging

from .project_models import Project
from .partner_models import Partner
from .about_models import About
from .vacancy_models import Vacancy
from .service_models import Service

logger = logging.getLogger(__name__)


class Media(models.Model):
    about = models.ForeignKey(
        About,
        related_name='medias',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Haqqımızda'
    )
    project = models.ForeignKey(
        Project,
        related_name='medias',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Lahiyə'
    )
    partner = models.ForeignKey(
        Partner,
        related_name='medias',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Əməkdaşlar'
    )
    vacancy = models.ForeignKey(
        Vacancy,
        related_name='medias',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Vakansiyalar'
    )
    service = models.ForeignKey(
        Service,
        related_name='medias',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Servislər'
    )
    image = models.ImageField(
        upload_to='images/',  
        verbose_name='Şəkil'
    )
    video = models.FileField(
        upload_to='videos/',  
        null=True,
        blank=True,
        verbose_name='Video'
    )
    is_home_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Ana səhifəs üçün arxa plan şəkli'
    )
    is_about_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Haqqımızda səhifəsi üçü arxa plan şəkli'
    )
    is_contact_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Əlaqə səhifəsi üçün arxa plan şəkli'
    )
    is_project_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Lahiyə səhifəsi üçün arxa plan şəkli'
    )
    is_vacany_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Vakansiya səhifəsi üçün arxa plan şəkli'
    )
    is_service_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Servis səhifəsi üçün arxa plan şəkli'
    )
    is_footer_background_image = models.BooleanField(
        default=False,
        verbose_name='Websiten-ın aşağı hissəsi üçün arxa plan şəkli'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Image yaradılma tarixi'
    )

    class Meta:
        verbose_name = 'Media'
        verbose_name_plural = 'Medialar'

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