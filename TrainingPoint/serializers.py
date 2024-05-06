from rest_framework.serializers import ModelSerializer
from rest_framework  import serializers
from .models import *

class DepartmentSerializer(ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
    
class GradeSerializer(ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'

class ActivitySerializer(ModelSerializer):
    class Meta:
        model = Activity
        fields = ['id', 'name', 'time', 'location', 'description', 'points', 'student']

class AchievementSerializer(ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'

class NewsSerializer(ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'
    
class NewsDetailSerializer(NewsSerializer):
    like = serializers.SerializerMethodField()

    def get_like(self, news):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return news.like_set.filter(active=True, user=request.user).exists()
    
    class Meta:
        model = NewsSerializer.Meta.model
        fields = list(NewsSerializer.Meta.fields) + ['like']

class UserSerializer(ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'avatar', 'user_type', 'email', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }
    
    def create(self, valdiated_data):
        data = valdiated_data.copy()
        user = User(**data)
        user.set_password(data['password'])
        user.save()

        return user
    
class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content']