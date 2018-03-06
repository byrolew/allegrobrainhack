from django.db import models

class Keyword(models.Model):
    keyword = models.CharField(max_length=256, unique=True, db_index=True)
    pv = models.IntegerField(default=100)

    def __str__(self):
    	return self.keyword
