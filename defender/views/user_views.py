import os

from django.core.files.storage import FileSystemStorage
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from defender.decorators import log_request_params
from defender.models import User
from defender.serializers import UserSerializer, UserLoginSerializer
from datetime import datetime


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # 로그인 기능 추가
    @log_request_params
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['id']
            password = serializer.validated_data['pw']

            try:
                user = User.objects.get(id=user_id)
                if user.check_password(password):
                    # UserSerializer를 사용하여 모든 사용자 정보 직렬화
                    user_serializer = self.get_serializer(user)
                    return Response({
                        "resultCode": "20",
                        "message": "로그인 성공",
                        "data": user_serializer.data
                    })
                else:
                    return Response({
                        "resultCode": "40",
                        "message": "비밀번호가 일치하지 않습니다.",
                        "data": None
                    }, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({
                    "resultCode": "40",
                    "message": "존재하지 않는 사용자입니다.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "resultCode": "40",
            "message": "유효하지 않은 요청입니다.",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @log_request_params
    @action(detail=False, methods=['post'], url_path='create')
    def create_user(self, request):
        # request.data를 직접 복사하지 않고 필요한 필드만 새 딕셔너리에 담기
        user_data = {}

        # 텍스트 필드들 복사
        for field in ['id', 'pw', 'isAdmin', 'email', 'store_name', 'phone_number',
                      'search_count', 'usage_end_date', 'usage_start_date']:
            if field in request.data:
                user_data[field] = request.data[field]

        # 파일 필드 별도 처리
        if 'business_license_image' in request.FILES:

            # 파일 객체 가져오기
            file_obj = request.FILES['business_license_image']

            # 저장할 실제 파일 경로 (상대 경로)
            relative_path = f"licenseImage/{user_data.get('id', 'unknown')}_{file_obj.name}"

            # 실제 파일 저장 (상대 경로 사용)
            from django.core.files.storage import default_storage
            saved_path = default_storage.save(relative_path, file_obj)

            # 데이터베이스에 저장할 URL 경로 (MEDIA_URL 포함)
            from defender_project import settings
            db_path = settings.MEDIA_URL + saved_path

            # 저장된 URL 경로를 모델에 저장
            user_data['business_license_image'] = db_path

        # 직렬화 및 저장
        serializer = self.get_serializer(data=user_data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "resultCode": "20",
                "message": "사용자 생성 성공",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "resultCode": "40",
            "message": "사용자 생성 실패",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @log_request_params
    @action(detail=False, methods=['post'], url_path='read')
    def read_users(self, request):
        try:
            users = self.get_queryset()
            serializer = self.get_serializer(users, many=True)

            return Response({
                "resultCode": "20",
                "message": "성공",
                "data": {
                    "usrList": serializer.data
                }
            })
        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": "실패"
            }, status=400)

    @log_request_params
    @action(detail=True, methods=['post'], url_path='read')
    def read_user(self, request, pk=None):
        try:
            user = self.get_object()
            serializer = self.get_serializer(user)
            return Response({
                "resultCode": "20",
                "message": "성공",
                "data": serializer.data
            })
        except User.DoesNotExist:
            return Response(
                {"resultCode": "40", "message": "사용자를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

    # 사용자 정보 수정 (Update)
    @log_request_params
    @action(detail=True, methods=['put'], url_path='update')
    def update_user(self, request, pk=None):
        try:
            user = self.get_object()

            # 이미지 처리
            image_file = request.FILES.get('business_license_image')
            if image_file:
                # 라이센스 이미지 저장 폴더 경로 설정
                from defender_project import settings
                license_image_dir = os.path.join(settings.MEDIA_ROOT, 'licenseImage')

                # 폴더가 없으면 생성
                if not os.path.exists(license_image_dir):
                    os.makedirs(license_image_dir)

                # 파일명 생성 (중복 방지를 위해 타임스탬프 추가)
                now = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{now}_{image_file.name}"

                # 파일 저장
                fs = FileSystemStorage(location=license_image_dir)
                saved_filename = fs.save(filename, image_file)

                # 데이터베이스에 저장할 URL 경로 생성
                image_url = f"/media/licenseImage/{saved_filename}"

                # 이미지 URL을 request.data에 추가
                data = request.data.copy()
                data['business_license_image'] = image_url
            else:
                data = request.data

            serializer = self.get_serializer(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "resultCode": "20",
                    "message": "사용자 정보가 업데이트되었습니다.",
                    "data": {
                        "id": user.id,
                        "isAdmin": user.isAdmin,
                        "email": user.email,
                        "store_name": user.store_name,
                        "phone_number": user.phone_number,
                        "search_count": user.search_count,
                        "usage_count": user.usage_count,
                        "business_license_image": user.business_license_image,
                        "usage_start_date": user.usage_start_date,
                        "usage_end_date": user.usage_end_date
                    }
                })
            return Response({
                "resultCode": "40",
                "message": "유효하지 않은 사용자 정보입니다.",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                "resultCode": "40",
                "message": "사용자를 찾을 수 없습니다.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

    #사용자 정보 삭제
    @log_request_params
    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_user(self, request, pk=None):
        try:
            user = self.get_object()
            user_id = user.id
            user.delete()
            return Response({
                "resultCode": "20",
                "message": "사용자가 성공적으로 삭제되었습니다.",
                "data": {
                    "id": user_id
                }
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                "resultCode": "40",
                "message": "사용자를 찾을 수 없습니다.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

    #사용자 정보 수정에서 비밀번호 변경 시 암호화 처리
    @log_request_params
    @action(detail=False, methods=['put'], url_path='update-password')
    def update_password(self, request):
        try:
            # 요청에서 id와 새 비밀번호 가져오기
            user_id = request.data.get('id')
            new_password = request.data.get('pw')

            # id나 pw가 없는 경우 에러 반환
            if not user_id or not new_password:
                return Response({
                    "resultCode": "40",
                    "message": "아이디와 새 비밀번호를 모두 제공해야 합니다."
                }, status=status.HTTP_400_BAD_REQUEST)

            # 사용자 조회
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    "resultCode": "40",
                    "message": "사용자를 찾을 수 없습니다."
                }, status=status.HTTP_404_NOT_FOUND)

            # 비밀번호 업데이트
            # serializer를 사용하여 비밀번호 업데이트
            serializer = self.get_serializer(user, data={'pw': new_password}, partial=True)
            if serializer.is_valid():
                serializer.save()  # 이 과정에서 모델의 save() 메소드가 암호화를 처리한다고 가정

                return Response({
                    "resultCode": "20",
                    "message": "비밀번호가 성공적으로 업데이트되었습니다.",
                    "data": {
                        "id": user.id
                    }
                })
            else:
                return Response({
                    "resultCode": "40",
                    "message": "유효하지 않은 비밀번호 형식입니다."
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "resultCode": "40",
                "message": f"비밀번호 업데이트 중 오류가 발생했습니다: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 조회가능횟수 조정 API
    @log_request_params
    @action(detail=True, methods=['post'], url_path='adjust-search-count')
    def adjust_search_count(self, request, pk=None):
        try:
            user = self.get_object()

            # 요청에서 변경할 값 가져오기
            action_type = request.data.get('action', 'increase')  # 기본값은 증가
            amount = int(request.data.get('amount', 1))  # 기본값은 1

            if action_type == 'increase':
                new_count = user.increase_search_count(amount)
                message = f"조회가능횟수가 {amount}만큼 증가했습니다."
            elif action_type == 'decrease':
                new_count = user.decrease_search_count(amount)
                message = f"조회가능횟수가 {amount}만큼 감소했습니다."
            elif action_type == 'set':
                new_count = user.set_search_count(amount)
                message = f"조회가능횟수가 {amount}(으)로 설정되었습니다."
            else:
                return Response({
                    "resultCode": "40",
                    "message": "유효하지 않은 작업 유형입니다. 'increase', 'decrease', 'set' 중 하나를 사용하세요.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "resultCode": "20",
                "message": message,
                "data": {
                    "id": user.id,
                    "search_count": new_count
                }
            })

        except User.DoesNotExist:
            return Response({
                "resultCode": "40",
                "message": "사용자를 찾을 수 없습니다.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({
                "resultCode": "40",
                "message": "유효하지 않은 수량입니다.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    # 이용가능횟수 조정 API
    @log_request_params
    @action(detail=True, methods=['post'], url_path='adjust-usage-count')
    def adjust_usage_count(self, request, pk=None):
        try:
            user = self.get_object()

            # 요청에서 변경할 값 가져오기
            action_type = request.data.get('action', 'increase')  # 기본값은 증가
            amount = int(request.data.get('amount', 1))  # 기본값은 1

            if action_type == 'increase':
                new_count = user.increase_usage_count(amount)
                message = f"이용가능횟수가 {amount}만큼 증가했습니다."
            elif action_type == 'decrease':
                new_count = user.decrease_usage_count(amount)
                message = f"이용가능횟수가 {amount}만큼 감소했습니다."
            elif action_type == 'set':
                new_count = user.set_usage_count(amount)
                message = f"이용가능횟수가 {amount}(으)로 설정되었습니다."
            else:
                return Response({
                    "resultCode": "40",
                    "message": "유효하지 않은 작업 유형입니다. 'increase', 'decrease', 'set' 중 하나를 사용하세요.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "resultCode": "20",
                "message": message,
                "data": {
                    "id": user.id,
                    "usage_count": new_count
                }
            })

        except User.DoesNotExist:
            return Response({
                "resultCode": "40",
                "message": "사용자를 찾을 수 없습니다.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({
                "resultCode": "40",
                "message": "유효하지 않은 수량입니다.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    # 사용기간 설정 API
    @log_request_params
    @action(detail=True, methods=['post'], url_path='set-usage-period')
    def set_usage_period_api(self, request, pk=None):
        try:
            user = self.get_object()

            # 요청에서 시작일, 종료일, 사용일수 가져오기
            start_date_str = request.data.get('start_date')
            end_date_str = request.data.get('end_date')
            days = int(request.data.get('days', 30)) if 'days' in request.data else 30

            start_date = None
            end_date = None

            # 시작일 파싱
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return Response({
                        "resultCode": "40",
                        "message": "시작일 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용하세요.",
                        "data": None
                    }, status=status.HTTP_400_BAD_REQUEST)

            # 종료일 파싱
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return Response({
                        "resultCode": "40",
                        "message": "종료일 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용하세요.",
                        "data": None
                    }, status=status.HTTP_400_BAD_REQUEST)

            # 사용기간 설정
            period = user.set_usage_period(start_date=start_date, end_date=end_date, days=days)

            return Response({
                "resultCode": "20",
                "message": "사용기간이 설정되었습니다.",
                "data": {
                    "id": user.id,
                    "usage_start_date": period['start_date'],
                    "usage_end_date": period['end_date']
                }
            })

        except User.DoesNotExist:
            return Response({
                "resultCode": "40",
                "message": "사용자를 찾을 수 없습니다.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({
                "resultCode": "40",
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    # 사용기간 연장 API
    @log_request_params
    @action(detail=True, methods=['post'], url_path='extend-usage-period')
    def extend_usage_period_api(self, request, pk=None):
        try:
            user = self.get_object()

            # 요청에서 연장할 일수 가져오기
            days = int(request.data.get('days', 30))  # 기본값은 30일

            # 사용기간 연장
            period = user.extend_usage_period(days=days)

            return Response({
                "resultCode": "20",
                "message": f"사용기간이 {days}일 연장되었습니다.",
                "data": {
                    "id": user.id,
                    "usage_start_date": period['start_date'],
                    "usage_end_date": period['end_date']
                }
            })

        except User.DoesNotExist:
            return Response({
                "resultCode": "40",
                "message": "사용자를 찾을 수 없습니다.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({
                "resultCode": "40",
                "message": "유효하지 않은 일수입니다.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    # 사용자 상태 확인 API
    @log_request_params
    @action(detail=True, methods=['get'], url_path='check-status')
    def check_status(self, request, pk=None):
        try:
            user = self.get_object()

            return Response({
                "resultCode": "20",
                "message": "사용자 상태 조회 성공",
                "data": {
                    "id": user.id,
                    "search_count": user.search_count,
                    "usage_count": user.usage_count,
                    "usage_start_date": user.usage_start_date,
                    "usage_end_date": user.usage_end_date,
                    "is_valid_period": user.is_usage_period_valid(),
                    "remaining_days": user.get_remaining_days()
                }
            })

        except User.DoesNotExist:
            return Response({
                "resultCode": "40",
                "message": "사용자를 찾을 수 없습니다.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)