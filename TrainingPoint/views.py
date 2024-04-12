from django.http import HttpResponse
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password
import re

def index(request):
    return HttpResponse('Training point manager')
