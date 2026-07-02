from django.db import models

from projects.utils.unique_slugify import unique_slugify


class SluggedModel(models.Model):
    """
    Abstract model that adds a unique slug and auto-populates it from
    get_slug_source() which you implement in your concrete model.
    """

    slug = models.SlugField(
        max_length=255,
        unique=True, 
        db_index=True, 
        blank=True,
        verbose_name='Slug'
    )

    class Meta:
        abstract = True  

    def get_slug_source(self) -> str:
        for cand in (
            'title', 
            'name', 
            'label', 
            'title_az', 
            'name_az'
        ):
            val = getattr(self, cand, None)
            if val:
                return val  
        raise ValueError(f"No slug source on {self.__class__.__name__}")

    def save(self, *args, **kwargs):
        if not self.slug:
            unique_slugify(self, self.get_slug_source(), slug_field="slug")
        super().save(*args, **kwargs)  