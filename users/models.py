import time
from djongo import models
from django.contrib.auth.models import User

# class Follower(models.Model):
#     username = models.CharField(max_length=25)

#     def __str__(self):
#         return self.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # username = models.CharField(max_length=25)
    # email = models.CharField(max_length=50)
    followers = models.ArrayModelField(
        model_container=User,
    )
    following = models.ArrayModelField(
        model_container=User,
    )
    # created_at = models.FloatField(default=time.time)

    # def save(self):
    #     super().save()
