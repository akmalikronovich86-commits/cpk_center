from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsDirectorOrHead


class BaseReportView(APIView):
    permission_classes = [IsAuthenticated, IsDirectorOrHead]
    def get_excel_response(self, workbook, filename):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={filename}.xlsx'
        workbook.save(response)
        return response

class LecturerLoadReportView(BaseReportView):
    def get(self, request): return Response({'message':'Report'})
class AttendanceReportView(BaseReportView):
    def get(self, request): return Response({'message':'Report'})
class ScheduleReportView(BaseReportView):
    def get(self, request): return Response({'message':'Report'})
class StudentListReportView(BaseReportView):
    def get(self, request): return Response({'message':'Report'})
class ExamResultsReportView(BaseReportView):
    def get(self, request): return Response({'message':'Report'})
