"""
URL configuration for defender_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from defender.views.announcement_views import AnnouncementViewSet

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from defender.views.user_views import UserViewSet
from defender.views.client_views import ClientViewSet


# router 인스턴스 생성
router = DefaultRouter()
router.register(r'announce', AnnouncementViewSet)
router.register(r'users', UserViewSet)
router.register(r'clients', ClientViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),  # 문자열이 아닌 router 변수의 urls 속성 사용
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
