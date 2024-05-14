from django.http import HttpResponse
from rest_framework.request import Request
from rest_framework import viewsets, permissions, generics, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password
from .serializers import *
from .models import *
from .paginator import *
from .perms import *

# def index(request):
#     return HttpResponse('Training point manager')

class DepartmentViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class GradeViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

class ActivityViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    pagination_class = ActivityPaginator

    def get_permissions(self):
        if self.action in ['create_activity', 'register', 'attend']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(methods=['post'], detail=False, url_path='create')
    def create_activity(self, request):

        if request.user.user_type != 'TLSV':
            return Response({'Lỗi':'Không có quyền tạo' })
        
        request.data['assistant_creator'] = request.user.id

        activity = ActivitySerializer(data=request.data)
        activity.is_valid(raise_exception=True)
        activity.save()
        
        return Response(activity.data, status=status.HTTP_201_CREATED)
    
    @action(methods=['post'], detail=True, url_path='register')
    def register(self, request, pk):
        activity = self.get_object()
        student = request.user

        #Kiem tra user da dang ki
        existing_registration = StudentActivity.objects.filter(student=student, activity=activity).first()

        if existing_registration:
            return Response(
                {'Lỗi': 'Sinh viên đã đăng kí hoạt động này'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        student_activity = StudentActivity.objects.create(student=student, activity=activity, status='registered')
        activity.student.add(student)
        
        return Response({'Đăng ký thành công'}, status=status.HTTP_201_CREATED)
    
    @action(methods=['post'], detail=True, url_path='attend')
    def attend(self, request, pk):
        activity = self.get_object()
        student = request.user

        try:
            student_activity = StudentActivity.objects.get(student=student, activity=activity)
            print(student_activity.status)
        except StudentActivity.DoesNotExist:
            return Response({'Lỗi': 'Sinh viên chưa đăng ký hoạt động này'}, status=status.HTTP_400_BAD_REQUEST)
        
        if student_activity.status == 'attended':
            return Response({'Lỗi': 'Sinh viên đã tham gia hoạt động này'}, status=status.HTTP_400_BAD_REQUEST)
        
        student_activity.status = 'attended'
        student_activity.save()

        training_points = TrainingPoint.objects.get(student=student)
        training_points.points += activity.points
        training_points.save()
        return Response({'message': 'Điểm danh thành công'}, status=status.HTTP_200_OK)


class NewsViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    pagination_class = NewsPaginator

    def get_permissions(self):
        if self.action in ['add_comment', 'like', 'create_news']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    
    @action(methods=['post'], detail=False, url_path='create')
    def create_news(self, request):
        if request.user.user_type != 'TLSV':
            return Response({'Lỗi':'Không có quyền tạo' })
        
        request.data['assistant_creator'] = request.user.id

        news = NewsSerializer(data=request.data)
        news.is_valid(raise_exception=True)
        news.save()
        
        return Response(news.data, status=status.HTTP_201_CREATED)

    
    @action(methods=['post'], detail=True, url_path='comments')
    def add_comment(self, request, pk):
        comment = Comment.objects.create(user=request.user, news=self.get_object(), content=request.data.get('content'))
        comment.save()
        return Response(CommentSerializer(comment, context={
            'request': request
        }).data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='commments')
    def get_comments(self, request, pk):
        comments = self.get_object.comment_set.all()
        return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK)
    
    @action(methods=['post'], detail=True, url_path='like')
    def like(self, request, pk):
        like, create = Like.objects.get_or_create(user=request.user, news=self.get_object)
        if not create:
            like.active = not like.active
            like.save()
        
        return Response(NewsDetailSerializer(self.get_object(), context={
            'request': request
        }).data, status=status.HTTP_200_OK)

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser]

    def get_permissions(self):
        if self.action.__eq__('get_current'):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    @action(methods=['get'], detail=False, url_path='current')
    def get_current(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
    
class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [OwnerPermission]
    
