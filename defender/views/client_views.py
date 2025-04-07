from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from defender.decorators import log_request_params
from defender.models import Client, User
from defender.serializers import ClientSerializer
from django.shortcuts import get_object_or_404


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    # 고객 저장
    @log_request_params
    @action(detail=False, methods=['post'], url_path='save')
    def save_client(self, request):
        """
        '/api/client/save/' 엔드포인트로 고객 정보 저장
        """
        try:
            # 전화번호 중복 체크
            phone_number = request.data.get('phoneNumber', '')
            if phone_number:
                # 모든 고객의 전화번호를 복호화하여 비교
                for client in self.get_queryset():
                    decrypted_phone = client.decrypt_phone()
                    if decrypted_phone and decrypted_phone == phone_number:
                        return Response({
                            "resultCode": "1000",
                            "message": "동일한 고객전화 번호가 이미 존재합니다.",
                            "data": None
                        }, status=status.HTTP_400_BAD_REQUEST)
            
            # 요청 데이터 복사
            data = request.data.copy()
            
            # 유저 ID와 매장명 추가
            user_id = request.data.get('userId')
            if user_id:
                # 유저 정보 조회
                try:
                    from defender.models import User
                    user = User.objects.get(id=user_id)
                    data['registeredBy'] = user.id
                    data['store_name'] = user.store_name
                except User.DoesNotExist:
                    pass
            
            # 중복이 없으면 저장 진행
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "resultCode": "20",
                    "message": "성공",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                "resultCode": "40",
                "message": "실패",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": f"오류가 발생했습니다: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 고객 목록 조회 (전화번호 복호화 포함)
    @log_request_params
    @action(detail=False, methods=['post'], url_path='list')
    def list_client(self, request):
        """
        '/api/client/list/' 엔드포인트로 고객 목록 조회
        """
        try:
            clients = self.get_queryset().order_by('-createDate')
            serializer = self.get_serializer(clients, many=True)
            return Response({
                "resultCode": "20",
                "message": "성공",
                "data": {
                    "clientList": serializer.data
                }
            })
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": "실패"
            }, status=status.HTTP_400_BAD_REQUEST)

    # 고객 수정
    @log_request_params
    @action(detail=True, methods=['put'], url_path='update')
    def update_client(self, request, pk=None):
        """
        '/api/client/{id}/update/' 엔드포인트로 고객 정보 수정
        """
        try:
            client = self.get_object()
            serializer = self.get_serializer(client, data=request.data, partial=True)
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
        except Client.DoesNotExist:
            return Response({
                "resultCode": "40",
                "message": "고객을 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)

    # 고객 삭제
    @log_request_params
    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_client(self, request, pk=None):
        """
        '/api/client/{id}/delete/' 엔드포인트로 고객 정보 삭제
        """
        try:
            client = self.get_object()
            client.delete()
            return Response({
                "resultCode": "20",
                "message": "고객이 성공적으로 삭제되었습니다."
            }, status=status.HTTP_200_OK)
        except Client.DoesNotExist:
            return Response({
                "resultCode": "40",
                "message": "고객을 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)

    # 고객 검색 (이름, 별명으로 검색)
    @log_request_params
    @action(detail=False, methods=['post'], url_path='search')
    def search_client(self, request):
        """
        '/api/client/search/?query=검색어' 엔드포인트로 고객 검색
        """
        try:
            query = request.query_params.get('query', '')
            if not query:
                return Response({
                    "resultCode": "40",
                    "message": "검색어를 입력하세요."
                }, status=status.HTTP_400_BAD_REQUEST)

            # 이름, 별명으로 검색
            clients = self.get_queryset().filter(
                Q(name__icontains=query) |
                Q(nickName__icontains=query)
            )

            serializer = self.get_serializer(clients, many=True)
            return Response({
                "resultCode": "20",
                "message": "성공",
                "data": {
                    "clientList": serializer.data
                }
            })
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": "검색 중 오류가 발생했습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

    # 전화번호로 고객 검색
    @log_request_params
    @action(detail=False, methods=['post'], url_path='search-by-phone')
    def search_by_phone(self, request):
        """
        '/api/client/search-by-phone/' 엔드포인트로 전화번호를 통한 고객 검색
        """
        try:
            phone_number = request.data.get('phoneNumber', '')
            if not phone_number:
                return Response({
                    "resultCode": "40",
                    "message": "전화번호를 입력하세요."
                }, status=status.HTTP_400_BAD_REQUEST)

            # 모든 고객의 전화번호를 복호화하여 검색
            matching_clients = []
            for client in self.get_queryset():
                decrypted_phone = client.decrypt_phone()
                if decrypted_phone and phone_number in decrypted_phone:
                    matching_clients.append(client)

            serializer = self.get_serializer(matching_clients, many=True)
            return Response({
                "resultCode": "20",
                "message": "성공",
                "data": {
                    "clientList": serializer.data
                }
            })
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": "검색 중 오류가 발생했습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

    # 전화번호로 불량 고객 확인
    @log_request_params
    @action(detail=False, methods=['post'], url_path='check-bad-client')
    def check_bad_client(self, request):
        """
        '/api/client/check-bad-client/' 엔드포인트로 전화번호를 통한 불량 고객 확인
        """
        try:
            if request.content_type == 'application/json':
                phone_number = request.data.get('phoneNumber', '')
            # POST 폼 데이터 처리
            else:
                phone_number = request.POST.get('phoneNumber', '')

            if not phone_number:
                return Response({
                    "resultCode": "40",
                    "message": "전화번호를 입력하세요."
                }, status=status.HTTP_400_BAD_REQUEST)

            # 모든 고객의 전화번호를 복호화하여 검색
            for client in self.get_queryset():
                decrypted_phone = client.decrypt_phone()
                if decrypted_phone and decrypted_phone == phone_number:
                    message = "불량 고객입니다." if client.isBadClient else "정상 고객입니다."
                    return Response({
                        "resultCode": "20",
                        "message": message,
                        "data": {
                            "id": client.id,
                            "name": client.name,
                            "nickName": client.nickName,
                            "gender": client.gender,
                            "ages": client.ages,
                            "isBadClient": client.isBadClient,
                            "extra": client.extra,
                            "createDate": client.createDate,
                            "registeredBy": client.registeredBy,
                            "store_name": client.store_name
                        }
                    })

            return Response({
                "resultCode": "40",
                "message": "해당 전화번호로 등록된 고객을 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": "오류가 발생했습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

    # nickName으로 고객 조회 (POST 방식)
    @log_request_params
    @action(detail=False, methods=['post'], url_path='get-by-nickname')
    def get_by_nickname(self, request):
        """
        '/api/client/by-nickname/' 엔드포인트로 특정 고객 정보 조회 (POST 방식)
        """
        try:
            nickname = request.data.get('nickName')
            if not nickname:
                return Response({
                    "resultCode": "40",
                    "message": "닉네임을 입력하세요."
                }, status=status.HTTP_400_BAD_REQUEST)

            client = get_object_or_404(self.get_queryset(), nickName=nickname)
            serializer = self.get_serializer(client)
            return Response({
                "resultCode": "20",
                "message": "성공",
                "data": serializer.data
            })
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": "고객을 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)

    # nickName으로 고객 수정 (POST 방식)
    @log_request_params
    @action(detail=False, methods=['post'], url_path='update-by-nickname')
    def update_by_nickname(self, request):
        """
        '/api/client/update-by-nickname/' 엔드포인트로 고객 정보 수정 (POST 방식)
        """
        try:
            nickname = request.data.get('nickName')
            if not nickname:
                return Response({
                    "resultCode": "40",
                    "message": "닉네임을 입력하세요."
                }, status=status.HTTP_400_BAD_REQUEST)

            client = get_object_or_404(self.get_queryset(), nickName=nickname)

            # nickName은 제외하고 나머지 데이터로 업데이트
            update_data = {k: v for k, v in request.data.items() if k != 'nickName'}

            serializer = self.get_serializer(client, data=update_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "resultCode": "20",
                    "message": "고객 정보가 업데이트되었습니다.",
                    "data": serializer.data
                })
            return Response({
                "resultCode": "40",
                "message": "유효하지 않은 요청입니다."
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": "고객을 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)

    # nickName으로 고객 삭제 (POST 방식)
    @log_request_params
    @action(detail=False, methods=['post'], url_path='delete-by-nickname')
    def delete_by_nickname(self, request):
        """
        '/api/client/delete-by-nickname/' 엔드포인트로 고객 정보 삭제 (POST 방식)
        """
        try:
            nickname = request.data.get('nickName')
            if not nickname:
                return Response({
                    "resultCode": "40",
                    "message": "닉네임을 입력하세요."
                }, status=status.HTTP_400_BAD_REQUEST)

            client = get_object_or_404(self.get_queryset(), nickName=nickname)
            client.delete()
            return Response({
                "resultCode": "20",
                "message": "고객이 성공적으로 삭제되었습니다."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": "고객을 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)

    @log_request_params
    @action(detail=False, methods=['post'], url_path='search-phone-and-decrease')
    def search_phone_and_decrease(self, request):
        """
        '/api/client/search-phone-and-decrease/' 엔드포인트로 전화번호 검색 및 횟수 차감
        """
        try:
            # 사용자 ID 확인
            user_id = request.data.get('user_id')
            if not user_id:
                return Response({
                    "resultCode": "40",
                    "message": "사용자 ID를 입력하세요."
                }, status=status.HTTP_400_BAD_REQUEST)

            # 전화번호 확인
            phone_number = request.data.get('phone_number', '')
            if not phone_number:
                return Response({
                    "resultCode": "40",
                    "message": "전화번호를 입력하세요."
                }, status=status.HTTP_400_BAD_REQUEST)

            # 사용자 조회 및 검색 횟수 차감
            try:
                user = User.objects.get(id=user_id)

                # 검색 횟수가 0이면 검색 불가
                if user.search_count <= 0:
                    return Response({
                        "resultCode": "40",
                        "message": "검색 가능 횟수가 부족합니다."
                    }, status=status.HTTP_403_FORBIDDEN)

                # 검색 횟수 차감
                remaining_count = user.decrease_search_count(1)

                # 모든 고객의 전화번호를 복호화하여 검색
                matching_clients = []
                for client in self.get_queryset():
                    decrypted_phone = client.decrypt_phone()
                    if decrypted_phone and phone_number in decrypted_phone:
                        matching_clients.append(client)

                serializer = self.get_serializer(matching_clients, many=True)

                # 결과와 함께 남은 검색 횟수 반환
                return Response({
                    "resultCode": "20",
                    "message": "성공",
                    "data": {
                        "remaining_search_count": remaining_count,
                        "clientList": serializer.data
                    }
                })

            except User.DoesNotExist:
                return Response({
                    "resultCode": "40",
                    "message": "존재하지 않는 사용자입니다."
                }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": "오류가 발생했습니다."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)