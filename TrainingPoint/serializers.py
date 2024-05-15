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
        fields = ['id', 'name', 'time','location', 'description', 'points', 'assistant_creator']

        time = serializers.DateTimeField(format='%Y-%m-%d %H:%M', input_formats=['%Y-%m-%d %H:%M'])
        expiration_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M', input_formats=['%Y-%m-%d %H:%M'])

class ClassificationSerializer(ModelSerializer):
    class Meta:
        model = Classification
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
class MissingPointReportSerializer(ModelSerializer):
    class Meta:
        model = MissingPointReport
        fields = ['id', 'student', 'activity','reason', 'proof', 'status']
        read_only_fields = ['student', 'status']

class UserSerializer(ModelSerializer):
    
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'avatar', 'department', 'user_type', 'grade']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'avatar': {'required': False, 'allow_null': True}
        }
    
    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        avatar = validated_data.pop('avatar', None)

        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.user_type = user_type
        user.avatar = avatar
        user.save()

        if user_type != 'SV':
            validated_data['grade'] = None
        user.save()

        #Set diem ren luyen = 0 khi tao moi
        if user_type == 'SV':
            TrainingPoint.objects.create(student=user, points=0)
            Classification.objects.create(student=user, name='Kém')

        return user
    
class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content']