from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    date_of_birth = models.DateField(blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    avatar = models.ImageField(
        upload_to='user_profile/',
        blank=True,
        verbose_name='Изображение',
        help_text='Загрузите изображение'
    )
    status = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Профили'
        verbose_name = 'Профиль'

    def __str__(self):
        return f'Profile for user {self.user.username}'

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()
