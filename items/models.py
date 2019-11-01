import time
from djongo import models

# Create your models here.
class ItemProperty(models.Model):
    likes = models.IntegerField(default=0)

    def __str__(self):
        prop = {"likes": self.likes}
        return str(prop)

class Item(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    # content = models.FileField()
    username = models.CharField(max_length=25)
    property = models.EmbeddedModelField(
        model_container=ItemProperty
    )
    retweeted = models.IntegerField(default=0)
    content = models.CharField(max_length=280)
    # timestamp = models.DateTimeField(auto_now_add=True, blank=True)
    timestamp = models.FloatField(default=time.time)
