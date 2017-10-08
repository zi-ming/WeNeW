from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.utils import timezone


class User(AbstractBaseUser, PermissionsMixin):
    # user = models.OneToOneField(User, unique=True, verbose_name=u'用户'),
    username = models.CharField(max_length=100, unique=True)
    # password = models.CharField(max_length=500)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20)
    head = models.CharField(max_length=100)
    authority = models.IntegerField(default=100)
    date_joined = models.DateTimeField(default=timezone.now)
    # is_active = models.BooleanField(default=True)
    # is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    # is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email',]

    objects = UserManager()

    def __unicode__(self):
        return self.username

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    # @property
    # def is_superuser(self):
    #     return self.is_admin

