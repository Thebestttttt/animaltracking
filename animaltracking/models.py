from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    phone_number = models.CharField(max_length=10, blank=False, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Tag(models.Model):
    name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name


class Animal(models.Model):
    class the_dender(models.TextChoices):
        Male = "male", "ตัวผู้"
        Female = "female","ตัวเมีย"
        Other = "other", "อื่นๆ"

    class the_type(models.TextChoices):
        DOG = "dog", "สุนัข"
        CAT = "cat", "แมว"
        BIRD = "bird", "นก"
        RABBIT = "rabbit", "กระต่าย"
        OTHER = "other", "อื่นๆ"

    name = models.CharField(max_length=100, blank=False, null=False)
    gender = models.CharField(max_length=10, choices=the_dender.choices, blank=False, null=False)
    age = models.CharField(blank=False, null=False)
    color = models.CharField(max_length=50, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    image = models.ImageField(upload_to='images/', blank=False, null=False)
    species = models.CharField(max_length=20, choices=the_type.choices, blank=False, null=False)
    tag = models.ManyToManyField(Tag, blank=True)

class Comment(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    comment_by = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField(max_length=200, blank=False, null=False)
    comment_date = models.DateTimeField(auto_now_add=True)

class StrayAnimal(models.Model):
    animal = models.OneToOneField(Animal, on_delete=models.CASCADE)
    date_found = models.DateField(blank=False, null=False)
    description_location = models.CharField(max_length=200, blank=False, null=False)
    latitude = models.FloatField(blank=False, null=False)
    longitude = models.FloatField(blank=False, null=False)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)

class LostAnimal(models.Model):
    animal = models.OneToOneField(Animal, on_delete=models.CASCADE)
    date_lost = models.DateField(blank=False, null=False)
    description_location = models.CharField(max_length=200, blank=False, null=False)
    latitude = models.FloatField(blank=False, null=False)
    longitude = models.FloatField(blank=False, null=False)
    status = models.CharField(
        max_length=20, blank=False, null=False,
        choices=[('Lost', 'หาย'), ('Found', 'พบแล้ว')],
        default='Lost'
    )
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
