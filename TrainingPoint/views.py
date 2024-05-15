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

class ClassificationViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Classification.objects.all()
    serializer_class = ClassificationSerializer

    @action(methods=['get'], detail=False, url_path='calculate/(?P<user_id>\d+)')
    def calculate_classification(self, request, user_id=None):
        user = User.objects.get(id=user_id)
        total_points = TrainingPoint.objects.get(student=user).points

        if 0 <= total_points <= 20:
            classification_name = 'kém'
        elif 20 < total_points <= 40:
            classification_name = 'yếu'
        elif 40 < total_points <= 60:
            classification_name = 'trung bình'
        elif 60 < total_points <= 80:
            classification_name = 'khá'
        elif 80 < total_points <= 90:
            classification_name = 'giỏi'
        else:
            classification_name = 'xuất sắc'
        
        classification, created= Classification.objects.get_or_create(student=user, defaults={"name": classification_name})
        if not created:
            classification.name = classification_name
            classification.save()
        
        
        return Response(ClassificationSerializer(classification).data)


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
        
        return Response({'message':'Đăng ký thành công'}, status=status.HTTP_201_CREATED)
    
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

        classification_view = ClassificationViewSet()
        classification_response = classification_view.calculate_classification(request, student.id)

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
        if request.user.user_type not in ['TLSV', 'CV']:
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

class MissingPointReportViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView,
                                generics.RetrieveAPIView, generics.UpdateAPIView):
    serializer_class = MissingPointReportSerializer
    pagination_class = MissingPointReportPaginator
    permission_classes = IsAuthenticatedOrCreate

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'SV':
            return MissingPointReport.objects.filter(student=user)
        elif user.user_type == 'TLSV' or user.user_type == 'CV':
            return MissingPointReport.objects.filter(active=True)
        
    def get_permissions(self):
        if self.action in ['create', 'pending_reports', 'approve_report', 'reject_report']:
            return [permissions.IsAuthenticated()]
        elif self.action == 'list':
            return [permissions.IsAuthenticated()]
        else:
            return [permissions.AllowAny()]
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        activity = serializer.validated_data['activity']
        student = request.user

        try:
            student_activity = StudentActivity.objects.get(student=student, activity=activity)
        except StudentActivity.DoesNotExist:
            return Response({'Lỗi': 'Bạn chưa đăng kí hoạt động này'}, status=status.HTTP_400_BAD_REQUEST)

        student_activity.status = 'missing_point_reported'
        student_activity.save()

        serializer.save(student=student) 

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['get'], detail=False, url_path='pending')
    def pending_reports(self, request):
        if request.user.user_type not in ['TLSV', 'CV']:
            return Response({'Lỗi': 'Bạn không có quyền truy cập'}, status=status.HTTP_403_FORBIDDEN)
        
        reports = MissingPointReport.objects.filter(status='pending')
        serializer = self.get_serializer(reports, many=True)
        return Response(serializer.data)
    
    @action(methods=['put'], detail=True, url_path='approve')
    def approve_report(self, request, pk):
        if request.user.user_type not in ['TLSV', 'CV']:
            return Response({'Lỗi': 'Bạn không có quyền truy cập'}, status=status.HTTP_403_FORBIDDEN)
        
        report = self.get_object()
        if report.status != 'pending':
            return Response({'Lỗi': 'Report không trong trạng thái chờ'}, status=status.HTTP_400_BAD_REQUEST)
        
        report.status = 'approved'
        report.save()

        student_activity = StudentActivity.objects.get(student=report.student, activity=report.activity)
        student_activity.status = 'attended'
        student_activity.save()

        training_points = TrainingPoint.objects.get(student=report.student)
        training_points.points += report.activity.points
        training_points.save()

        return Response({'message': 'Report thiếu điểm đã được duyệt'}, status=status.HTTP_200_OK)
    
    @action(methods=['put'], detail=True, url_path='reject')
    def reject_report(self, request, pk):
        if request.user.user_type not in ['TLSV', 'CV']:
            return Response({'Lỗi': 'Bạn không có quyền truy cập'}, status=status.HTTP_403_FORBIDDEN)
        
        report = self.get_object()
        if report.status != 'pending':
            return Response({'Lỗi': 'Report không trong trạng thái chờ'}, status=status.HTTP_400_BAD_REQUEST)
        
        report.status = 'rejected'
        report.save()

        return Response({'message': 'Report thiếu điểm đã bị từ chối'}, status=status.HTTP_200_OK)

class TraingingPointStatisticsViewSet(viewsets.ViewSet):

    def get_permissions(self):
        if self.action in ['by_grade', 'by_department', 'by_classification']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


    @action(methods=['get'], detail=False, url_path='by-grade')
    def by_grade(self, request):
        if request.user.user_type != 'CV':
            return Response({'Lỗi': 'Bạn không có quyền truy cập'}, status=status.HTTP_403_FORBIDDEN)
        
        grades = Grade.objects.all()
        data = []
        for grade in grades:
            total_points = 0
            user_count = 0
            classifications = {}
            for user in User.objects.filter(grade=grade, user_type='SV'):
                total_points += TrainingPoint.objects.get(student=user).points
                user_count += 1

                classification, created = Classification.objects.get_or_create(student=user, defaults={'name': 'Chưa phân loại'})
                if not created:
                    classification.save()
                if classification.name in classifications:
                    classifications[classification.name] += 1
                else:
                    classifications[classification.name] = 1
            data.append({
                'grade': grade.name,
                'total_points': total_points,
                'user_count': user_count,
                'classifications': classifications 
            })
        return Response(data)
    
    @action(methods=['get'], detail=False, url_path='by-department')
    def by_department(self, request):
        if request.user.user_type != 'CV':
            return Response({'Lỗi': 'Bạn không có quyền truy cập'}, status=status.HTTP_403_FORBIDDEN)
        
        departments = Department.objects.all()
        data = []
        for department in departments:
            total_points = 0
            user_count = 0
            classifications = {}
            for user in User.objects.filter(department=department, user_type='SV'):
                try:
                    total_points += TrainingPoint.objects.get(student=user).points
                    user_count += 1
                    classification, created = Classification.objects.get_or_create(student=user, defaults={'name': 'Chưa phân loại'})
                    if not created:
                        classification.save()
                    if classification.name in classifications:
                        classifications[classification.name] += 1
                    else:
                        classifications[classification.name] = 1
                except TrainingPoint.DoesNotExist:
                    pass
            data.append({
                'department': department.name,
                'total_points': total_points,
                'user_count': user_count,
                'classifications': classifications 
            })
        return Response(data)
    
    @action(methods=['get'], detail=False, url_path='by-classification')
    def by_classification(self, request):
        if request.user.user_type != 'CV':
            return Response({'Lỗi': 'Bạn không có quyền truy cập'}, status=status.HTTP_403_FORBIDDEN)
        
        classifications = Classification.objects.all()
        data = []
        for classification in classifications:
            user_count = User.objects.filter(classification=classification, user_type='SV').count()
            data.append({
                'classification': classification.name,
                'user_count': user_count
            })
        return Response(data)

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser]
    permission_classes = [IsAuthenticatedOrCreate] #Cho phep anonymous user tao tai khoan

    def get_permissions(self):
        if self.action.__eq__('get_current'):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    @action(methods=['get'], detail=False, url_path='current')
    def get_current(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_type = serializer.validated_data['user_type']
        if not request.user.is_anonymous and request.user.user_type != 'CV' and user_type == 'TLSV':
            return Response({'Lỗi': 'Bạn không có quyền tạo người dùng này.'}, status=status.HTTP_403_FORBIDDEN)
        
        user = serializer.save()
            
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [OwnerPermission]
   
