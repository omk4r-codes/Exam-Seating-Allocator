from django.db import models

# Create your models here.
class Addstudent(models.Model):
    name = models.CharField(max_length=100)
    mis = models.CharField(max_length=10)
    branch = models.CharField(max_length=50)
    year = models.CharField(max_length=10)

    def __str__(self):
        return self.name + "    " +self.mis  + "    " + self.branch + "    " + self.year 

class Addclassrooms(models.Model):
    name = models.CharField(max_length=10)
    seats = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.seats} seats)"