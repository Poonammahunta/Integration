from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Post(models.Model):
    text = models.TextField()

    def __str__(self):
    	""" A string representation of the model."""
    	return self.text[:50]



class Question(models.Model):
	question_text = models.CharField(max_length=200)
	pub_date = models.DateTimeField('date published')



class Choice(models.Model):
	question = models.ForeignKey(Question ,on_delete=models.CASCADE)
	choie_text = models.CharField(max_length=200)
	votes = models.IntegerField(default=0)
