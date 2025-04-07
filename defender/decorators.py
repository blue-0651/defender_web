import logging
import functools

logger = logging.getLogger('django.request')

def log_request_params(view_func):
    @functools.wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        # 여기서 self는 ViewSet 인스턴스, request는 HTTP 요청 객체입니다
        if request.method in ('POST', 'PUT', 'PATCH'):
            # POST 데이터와 FILES 정보를 로깅
            logger.info(f"Request POST data: {request.POST}")
            files_info = {k: f.name for k, f in request.FILES.items()}
            logger.info(f"Request FILES: {files_info}")

        if request.query_params:
            logger.info(f"Request Query params: {request.query_params}")

        # 원래 뷰 함수를 호출하여 결과 반환
        return view_func(self, request, *args, **kwargs)

    return wrapper