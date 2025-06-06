import os
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'defender_project.settings')
django.setup()

from defender.models import Client

# 오태양 고객 조회
clients = Client.objects.filter(name='오태양').order_by('store_name')

print('\n=== 오태양 고객 목록 ===')
print('매장명 | 전화번호 | 상태')
print('-' * 50)

for client in clients:
    status = '[불량]' if client.isBadClient else '[정상]'
    print(f'{client.store_name} | {client.decrypt_phone()} | {status}')

print(f'\n총 {clients.count()}명의 오태양 고객이 있습니다.') 