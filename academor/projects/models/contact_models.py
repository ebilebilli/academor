from django.db import models


class Contact(models.Model):
    address_az = models.CharField(
        max_length=255,
        verbose_name='Address (AZ)'
    )
    address_en = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Address (EN)'
    )
    address_ru = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Address (RU)'
    )
    phone = models.CharField(
        max_length=50,
        verbose_name='Phone'
    )
    whatsapp_number = models.CharField(
        null=True,
        blank=True,
        max_length=50,
        verbose_name='WhatsApp number'
    )
    whatsapp_number_2 = models.CharField(
        null=True,
        blank=True,
        max_length=50,
        verbose_name='WhatsApp number 2'
    )
    phone_three = models.CharField(
        null=True,
        blank=True,
        max_length=50,
        verbose_name='Phone (additional)'
    )
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name='Email'
    )
    instagram = models.URLField(
        null=True,
        blank=True,
        verbose_name=('Instagram')
    )
    facebook = models.URLField(
        null=True,
        blank=True,
        verbose_name=('Facebook')
    )
    youtube = models.URLField(
        null=True,
        blank=True
    )
    linkedn = models.URLField(
        null=True,
        blank=True,
        verbose_name=('LinkedIn')
    )
    tiktok = models.URLField(
        null=True,
        blank=True
    )
    map_embed_url = models.TextField(
        null=True,
        blank=True,
        verbose_name='Google Maps embed URL',
        help_text='iframe src dəyəri (məs. https://www.google.com/maps/embed?pb=...)',
    )

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"

    def __str__(self):
        return self.address_az or 'Contact'
