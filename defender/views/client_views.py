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
            # 닉네임 필수 체크
            nickname = request.data.get('nickName', '')
            if not nickname:
                return Response({
                    "resultCode": "40",
                    "message": "닉네임을 입력하세요.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # 닉네임 중복 체크 (더 상세한 정보 포함)
            if Client.objects.filter(nickName=nickname).exists():
                existing_client = Client.objects.get(nickName=nickname)
                return Response({
                    "resultCode": "30",
                    "message": "아이디가 이미 존재합니다.",
                    "data": {
                        "nickName": nickname,
                        "exists": True,
                        "registeredBy": existing_client.registeredBy,
                        "store_name": existing_client.store_name
                    }
                }, status=status.HTTP_200_OK)
            
            # 요청 데이터 복사
            data = request.data.copy()
            
            # 유저 ID와 매장명 추가
            user_id = request.data.get('userId')
            if not user_id:
                return Response({
                    "resultCode": "40",
                    "message": "사용자(매장소유자) ID를 입력하세요.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # 유저 정보 조회
            try:
                from defender.models import User
                user = User.objects.get(id=user_id)
                data['registeredBy'] = user.id
                data['store_name'] = user.store_name
            except User.DoesNotExist:
                return Response({
                    "resultCode": "40",
                    "message": "존재하지 않는 사용자입니다.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
                
            # 전화번호 중복 체크 (같은 매장에서만)
            phone_number = request.data.get('phoneNumber', '')
            if phone_number:
                existing_client = None
                # 모든 고객의 전화번호를 복호화하여 비교
                for client in self.get_queryset():
                    decrypted_phone = client.decrypt_phone()
                    # 같은 전화번호이고 같은 매장인 경우
                    if decrypted_phone and decrypted_phone == phone_number and client.registeredBy == user_id:
                        existing_client = client
                        break
                
                # 같은 매장에서 동일한 전화번호의 고객이 있는 경우 업데이트
                if existing_client:
                    serializer = self.get_serializer(existing_client, data=data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return Response({
                            "resultCode": "20",
                            "message": "고객 정보가 업데이트되었습니다.",
                            "data": serializer.data
                        })
                    return Response({
                        "resultCode": "40",
                        "message": "유효하지 않은 요청입니다.",
                        "data": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # 새로운 고객 등록
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
                    "message": "고객 정보가 성공적으로 수정되었습니다.",
                    "data": serializer.data
                })
            return Response({
                "resultCode": "40",
                "message": "유효하지 않은 요청입니다.",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Client.DoesNotExist:
            return Response({
                "resultCode": "40",
                "message": "고객을 찾을 수 없습니다.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": f"오류가 발생했습니다: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
                    "message": "전화번호를 입력하세요.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            # 모든 고객의 전화번호를 복호화하여 정확히 일치하는 고객만 검색
            matching_clients = []
            for client in self.get_queryset():
                decrypted_phone = client.decrypt_phone()
                if decrypted_phone and decrypted_phone == phone_number:
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
                "message": f"검색 중 오류가 발생했습니다: {str(e)}",
                "data": None
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
                user_id = request.data.get('userId', '')
            # POST 폼 데이터 처리
            else:
                phone_number = request.POST.get('phoneNumber', '')
                user_id = request.POST.get('userId', '')

            if not phone_number:
                return Response({
                    "resultCode": "40",
                    "message": "전화번호를 입력하세요.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            if not user_id:
                return Response({
                    "resultCode": "40",
                    "message": "사용자 ID를 입력하세요.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            # 모든 고객의 전화번호를 복호화하여 검색
            for client in self.get_queryset():
                decrypted_phone = client.decrypt_phone()
                if decrypted_phone and decrypted_phone == phone_number:
                    # 매장의 고객인지 확인
                    if client.registeredBy == user_id:
                        # 현 매장의 고객인 경우
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
                                "store_name": client.store_name,
                                "isOwnCustomer": True
                            }
                        })
                    else:
                        # 다른 매장의 고객인 경우
                        return Response({
                            "resultCode": "30",
                            "message": "외부 고객입니다.",
                            "data": {
                                "id": client.id,
                                "phoneNumber": phone_number,
                                "store_name": client.store_name,
                                "isOwnCustomer": False
                            }
                        })

            return Response({
                "resultCode": "40",
                "message": "해당 전화번호로 등록된 고객을 찾을 수 없습니다.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": f"오류가 발생했습니다: {str(e)}",
                "data": None
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
                    "message": "닉네임을 입력하세요.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                client = Client.objects.get(nickName=nickname)
            except Client.DoesNotExist:
                return Response({
                    "resultCode": "40",
                    "message": "고객을 찾을 수 없습니다.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

            # 새 닉네임 변경 요청이 있는 경우 중복 체크
            new_nickname = request.data.get('newNickName')
            if new_nickname and new_nickname != nickname:
                if Client.objects.filter(nickName=new_nickname).exists():
                    return Response({
                        "resultCode": "30",
                        "message": "아이디가 이미 존재합니다.",
                        "data": {
                            "nickName": new_nickname,
                            "exists": True
                        }
                    }, status=status.HTTP_200_OK)
                # 새 닉네임을 업데이트 데이터에 추가
                update_data = {k: v for k, v in request.data.items() if k != 'nickName'}
                update_data['nickName'] = new_nickname
            else:
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
                "message": "유효하지 않은 요청입니다.",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": f"오류가 발생했습니다: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        # 이 API는 더 이상 사용하지 않습니다
        return Response({
            "resultCode": "40",
            "message": "이 API는 더 이상 사용하지 않습니다. search-by-phone API를 사용하세요.",
            "data": None
        }, status=status.HTTP_410_GONE)

    # ID로 고객 수정 (POST 방식)
    @log_request_params
    @action(detail=False, methods=['post'], url_path='update-by-id')
    def update_client_by_id(self, request):
        """
        '/api/client/update-by-id/' 엔드포인트로 고객 정보 수정 (POST 방식)
        """
        try:
            client_id = request.data.get('id')
            if not client_id:
                return Response({
                    "resultCode": "40",
                    "message": "고객 ID를 입력하세요.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                client = Client.objects.get(id=client_id)
            except Client.DoesNotExist:
                return Response({
                    "resultCode": "40",
                    "message": "고객을 찾을 수 없습니다.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

            # 닉네임 변경 시 중복 체크
            new_nickname = request.data.get('nickName')
            if new_nickname and new_nickname != client.nickName:
                if Client.objects.filter(nickName=new_nickname).exists():
                    return Response({
                        "resultCode": "30",
                        "message": "아이디가 이미 존재합니다.",
                        "data": {
                            "nickName": new_nickname,
                            "exists": True
                        }
                    }, status=status.HTTP_200_OK)

            # ID는 제외하고 나머지 데이터로 업데이트
            update_data = {k: v for k, v in request.data.items() if k != 'id'}

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
                "message": "유효하지 않은 요청입니다.",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": f"오류가 발생했습니다: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 닉네임 중복 확인
    @log_request_params
    @action(detail=False, methods=['post'], url_path='check-nickname')
    def check_nickname_exists(self, request):
        """
        '/api/client/check-nickname/' 엔드포인트로 닉네임 중복 확인
        """
        try:
            nickname = request.data.get('nickName')
            if not nickname:
                return Response({
                    "resultCode": "40",
                    "message": "닉네임을 입력하세요.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 닉네임 존재 여부 확인
            try:
                existing_client = Client.objects.get(nickName=nickname)
                # 닉네임이 이미 존재하는 경우 (더 상세한 정보 포함)
                return Response({
                    "resultCode": "30",
                    "message": "아이디가 이미 존재합니다.",
                    "data": {
                        "nickName": nickname,
                        "exists": True,
                        "id": existing_client.id,
                        "registeredBy": existing_client.registeredBy,
                        "store_name": existing_client.store_name,
                        "createDate": existing_client.createDate
                    }
                }, status=status.HTTP_200_OK)
            except Client.DoesNotExist:
                # 닉네임이 존재하지 않는 경우
                return Response({
                    "resultCode": "20",
                    "message": "사용 가능한 아이디입니다.",
                    "data": {
                        "nickName": nickname,
                        "exists": False
                    }
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": f"오류가 발생했습니다: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ID 없이 고객 수정 (POST/PUT 방식)
    @log_request_params
    @action(detail=False, methods=['post', 'put'], url_path='update')
    def update_without_id(self, request):
        """
        '/api/clients/update/' 엔드포인트로 고객 정보 수정 (POST 또는 PUT 방식)
        """
        try:
            # ID 또는 닉네임 중 하나는 필수
            client_id = request.data.get('id')
            nickname = request.data.get('nickName')
            
            if not client_id and not nickname:
                return Response({
                    "resultCode": "40",
                    "message": "고객 ID 또는 닉네임 중 하나는 필수입니다.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # ID로 고객 조회
            if client_id:
                try:
                    client = Client.objects.get(id=client_id)
                except Client.DoesNotExist:
                    return Response({
                        "resultCode": "40",
                        "message": "고객을 찾을 수 없습니다.",
                        "data": None
                    }, status=status.HTTP_404_NOT_FOUND)
            # 닉네임으로 고객 조회
            elif nickname:
                try:
                    client = Client.objects.get(nickName=nickname)
                except Client.DoesNotExist:
                    return Response({
                        "resultCode": "40",
                        "message": "고객을 찾을 수 없습니다.",
                        "data": None
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # 닉네임 변경 체크
            new_nickname = request.data.get('newNickName')
            if new_nickname and new_nickname != client.nickName:
                if Client.objects.filter(nickName=new_nickname).exists():
                    return Response({
                        "resultCode": "30",
                        "message": "아이디가 이미 존재합니다.",
                        "data": {
                            "nickName": new_nickname,
                            "exists": True
                        }
                    }, status=status.HTTP_200_OK)
                
                # 새 닉네임으로 업데이트
                update_data = {k: v for k, v in request.data.items() if k not in ['id', 'nickName', 'newNickName']}
                update_data['nickName'] = new_nickname
            else:
                # ID와 닉네임을 제외한 데이터로 업데이트
                update_data = {k: v for k, v in request.data.items() if k not in ['id', 'nickName']}
            
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
                "message": "유효하지 않은 요청입니다.",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": f"오류가 발생했습니다: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)