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
    department = models.ForeignKey('Department', on_delete=models.CASCADE, null=True)
    grade = models.ForeignKey('Grade', on_delete=models.SET_NULL, null=True, blank=True)


class BaseModel(models.Model):
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['id']

class Department(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name
    
class Grade(BaseModel):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

class Activity(BaseModel):
    name = models.CharField(max_length=100)
    time = models.DateTimeField()
    location = models.CharField(max_length=150)
    description = models.TextField()
    points = models.IntegerField()
    student = models.ManyToManyField(User, 'StudentActivity', blank=True)
    assistant_creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

class Classification(BaseModel):
    name = models.CharField(max_length=50)
    student = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

class News(BaseModel):
    content = models.TextField()
    image = models.ImageField(upload_to='news/%Y/%m', null=True)
    assistant_creator = models.ForeignKey(User, on_delete=models.CASCADE)

class Interaction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.CASCADE)

    class Meta:
        abstract = True

class Like(Interaction):
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'news')

class Comment(Interaction):
    content = models.CharField(max_length=255)

class StudentActivity(BaseModel):
    STATUS_CHOICES = (
        ('registered', 'Đã đăng ký'),
        ('attended', 'Đã tham gia'),
        ('missing_point_reported', 'Báo thiếu')
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE) 
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='registered')

class TrainingPoint(BaseModel):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()

class MissingPointReport(BaseModel):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    reason = models.TextField()
    # proof = models.FileField(upload_to='missing_point_proofs/%Y/%m')
    proof = models.TextField()
    STATUS_CHOICES = (
        ('pending', 'Đang chờ'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Đã bị từ chối')
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')