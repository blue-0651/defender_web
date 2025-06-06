import os
import django
from cryptography.fernet import Fernet

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'defender_project.settings')
django.setup()

from defender.models import Client
from django.conf import settings

# Fernet 인스턴스 생성
cipher_suite = Fernet(settings.ENCRYPTION_KEY)

# 모든 고객 정보 조회
clients = Client.objects.all().order_by('store_name', 'nickName')

print("\n=== 고객 전화번호 목록 ===")
print("매장명 | 고객명 | 전화번호 | 불량고객 여부")
print("-" * 60)

for client in clients:
    bad_client_mark = "[불량]" if client.isBadClient else "[정상]"
    # 전화번호 복호화
    try:
        decrypted_phone = client.decrypt_phone()
    except Exception as e:
        decrypted_phone = "복호화 실패"
    
    print(f"{client.store_name} | {client.name} | {decrypted_phone} | {bad_client_mark}")

print(f"\n총 고객 수: {clients.count()}명") 