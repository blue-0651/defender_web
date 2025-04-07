from django.http import JsonResponse
from rest_framework import status
import logging


class BearerTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.token = "defender0651"
        # 토큰 인증을 우회할 경로 목록
        self.exempt_paths = [
            '/api/users/login/',  # 로그인 경로
            '/api/users/create/'  # 회원가입 경로.  
            '/api/users/read/'
        ]

    def __call__(self, request):
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return self.get_response(request)

        # 우회할 경로인지 확인
        path = request.path_info
        if any(path.endswith(exempt_path) for exempt_path in self.exempt_paths):
            return self.get_response(request)

        # Get authorization header
        auth_header = request.headers.get('Authorization', '')

        # Check if the header is in the correct format
        if not auth_header.startswith('Bearer '):
            return JsonResponse(
                {"error": "인증 토큰이 필요합니다. Bearer 형식으로 제공해주세요."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Extract the token
        token = auth_header.split(' ')[1].strip()

        # Verify the token
        if token != self.token:
            return JsonResponse(
                {"error": "유효하지 않은 인증 토큰입니다."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Continue with the request
        return self.get_response(request)

logger = logging.getLogger('django.request')

class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 로깅 시 바이너리 데이터 처리 개선
        if request.method in ('POST', 'PUT', 'PATCH'):
            # Content-Type 확인
            content_type = request.META.get('CONTENT_TYPE', '')

            # multipart/form-data인 경우 (파일 업로드 포함)
            if 'multipart/form-data' in content_type:
                # POST 데이터와 FILES 정보만 로깅
                logger.info(f"Request POST data: {request.POST}")
                # 파일 이름만 로깅
                files_info = {k: f.name for k, f in request.FILES.items()}
                logger.info(f"Request FILES: {files_info}")
            else:
                # 일반 텍스트 데이터인 경우만 body 로깅 시도
                try:
                    logger.info(f"Request Body: {request.body.decode('utf-8')}")
                except UnicodeDecodeError:
                    logger.info("Request contains binary data that cannot be displayed")

        if request.GET:
            logger.info(f"Request GET params: {request.GET}")

        # 요청 처리
        response = self.get_response(request)

        return response