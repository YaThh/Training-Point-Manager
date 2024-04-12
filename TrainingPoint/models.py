from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from cloudinary.models import CloudinaryField

class User(AbstractUser):
    avatar = CloudinaryField('avatar', null=True)
    USER_TYPE = (
        ('CV', 'Chuyên viên CTSV'),
        ('TLSV', 'Trợ lý sinh viên'),
        ('SV', 'Sinh viên'),
    )
    user_type = models.CharField(max_length=4, choices=USER_TYPE)


class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name
    
class Grade(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

class Student(User):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)

class StudentAssistant(User):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

class Activity(models.Model):
    name = models.CharField(max_length=100)
    time = models.DateTimeField()
    location = models.CharField(max_length=150)
    description = models.TextField()
    assistant_creator = models.ForeignKey(StudentAssistant, on_delete=models.CASCADE)

class Achievement(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name

class News(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    content = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='ban_tin/')
    assistant_creator = models.ForeignKey(StudentAssistant, on_delete=models.CASCADE)
    likes = models.ManyToManyField(Student, related_name='news_likes')
    comments = models.ManyToManyField(Student, through='Comment', related_name='news_comment')

class Comment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

class StudentActivity(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    registered_time = models.DateTimeField(auto_now_add=True)

class TrainingPoint(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    # Thêm các trường cho từng tiêu chí đánh giá điểm rèn luyện

    total = models.FloatField()