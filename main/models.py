from django.db import models

class PacketModel(models.Model):
    clientID = models.IntegerField()
    data = models.TextField(max_length=80)
    country = models.TextField(max_length=30)
    description = models.TextField(max_length=100,null=True)
    def info(self):
        return self.data, self.country, self.description
