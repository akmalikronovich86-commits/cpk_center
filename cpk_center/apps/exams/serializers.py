from rest_framework import serializers

from .models import ExamQuestion, ExamResult, TestSession


class ExamQuestionSerializer(serializers.ModelSerializer):
    class Meta: model = ExamQuestion; fields = '__all__'
class ExamResultSerializer(serializers.ModelSerializer):
    class Meta: model = ExamResult; fields = '__all__'
class TestSessionSerializer(serializers.ModelSerializer):
    class Meta: model = TestSession; fields = '__all__'
