from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from defender.decorators import log_request_params
from defender.models import Announcement
from defender.serializers import AnnouncementSerializer


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

    @log_request_params
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response({
                "resultCode": "20",
                "message": "성공",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED, headers=headers)
        return Response({
            "resultCode": "40",
            "message": "실패"
        }, status=status.HTTP_400_BAD_REQUEST)

    # 공지사항 저장
    @log_request_params
    @action(detail=False, methods=['post'], url_path='save')
    def save_announce(self, request):
        """
        '/api/announce/save/' 엔드포인트로 연락처 저장
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "resultCode": "20",
                "message": "성공",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "resultCode": "40",
            "message": "실패"
        }, status=status.HTTP_400_BAD_REQUEST)

    # 공지사항 목록 조회
    @log_request_params
    @action(detail=False, methods=['post'], url_path='list')
    def list_announce(self, request):
        """
        '/api/announce/list/' 엔드포인트로 공지사항 목록 조회
        """
        try:
            announcements = self.get_queryset().order_by('-createDate')
            serializer = self.get_serializer(announcements, many=True)
            return Response({
                "resultCode": "20",
                "message": "성공",
                "data": {
                    "announceList": serializer.data
                }
            })
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": "실패"
            }, status=status.HTTP_400_BAD_REQUEST)

    # 공지사항 수정
    @log_request_params
    @action(detail=True, methods=['put'], url_path='update')
    def update_announce(self, request, pk=None):
        """
        '/api/announce/{id}/update/' 엔드포인트로 공지사항 수정
        """
        try:
            announcement = self.get_object()
            serializer = self.get_serializer(announcement, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "resultCode": "20",
                    "message": "성공",
                    "data": serializer.data
                })
            return Response({
                "resultCode": "40",
                "message": "유효하지 않은 요청입니다."
            }, status=status.HTTP_400_BAD_REQUEST)
        except Announcement.DoesNotExist:
            return Response({
                "resultCode": "40",
                "message": "공지사항을 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)

    # 공지사항 삭제
    @log_request_params
    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_announce(self, request, pk=None):
        """
        '/api/announce/{id}/delete/' 엔드포인트로 공지사항 삭제
        """
        try:
            announcement = self.get_object()
            announcement.delete()
            return Response({
                "resultCode": "20",
                "message": "공지사항이 성공적으로 삭제되었습니다."
            }, status=status.HTTP_200_OK)
        except Announcement.DoesNotExist:
            return Response({
                "resultCode": "40",
                "message": "공지사항을 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)