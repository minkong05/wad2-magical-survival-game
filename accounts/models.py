from django.conf import settings
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    class_type = models.CharField(max_length=20, blank=True, default="")
    coins = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} profile"