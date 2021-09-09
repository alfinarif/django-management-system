from django.db import models

# import class for change permission of user
from django.contrib.auth.models import BaseUserManager, AbstractUser

from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email Address is Required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must be have is_staff True")

        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must be have is_superuser True")

        if extra_fields.get('is_active') is not True:
            raise ValueError("Superuser must be have is_active True")
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    USER_TYPE = (
        (1, 'Customer'),
        (2, 'Trainer'),
        (3, 'Manager')
    )
    username = None
    email = models.EmailField(unique=True)
    user_type = models.IntegerField(choices=USER_TYPE, default=1)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomManager()



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=30, blank=True, null=True)
    first_name = models.CharField(max_length=20, blank=True, null=True)
    last_name = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(max_length=300, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zipcode = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=16, blank=True, null=True)
    image = models.ImageField(upload_to='profile-images')

    def __str__(self):
        return f"{self.user.email}'s profile"
    
    def is_fully_filled(self):
        field_names = [f.name for f in self._meta.get_fields()]
        for field_name in field_names:
            value = getattr(self, field_name)
            if value is None or value=='':
                return False
        return True

    @receiver(post_save, sender=User)
    def create_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)


    @receiver(post_save, sender=User)
    def save_profile(sender, instance, **kwargs):
        instance.profile.save()
