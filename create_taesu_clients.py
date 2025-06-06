import os
import django
import random

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'defender_project.settings')
django.setup()

from defender.models import User, Client

# 기존 김태수 데이터 삭제
Client.objects.filter(name='김태수').delete()

# 매장 목록 가져오기
users = list(User.objects.filter(id__startswith='user'))
selected_users = random.sample(users, 5)  # 5개 매장 무작위 선택

# 정상고객으로 등록할 매장과 불량고객으로 등록할 매장 분리
normal_stores = selected_users[:3]  # 앞의 3개 매장은 정상고객
bad_stores = selected_users[3:]     # 뒤의 2개 매장은 불량고객

# 김태수의 기본 정보
taesu_phone = '010-6739-7588'  # 지정된 전화번호

print("\n=== 김태수 고객 생성 시작 ===")

# 정상고객으로 등록
for user in normal_stores:
    client = Client.objects.create(
        nickName=f'{user.store_name}_김태수',
        name='김태수',
        phoneNumber=taesu_phone,
        gender='male',
        ages='40대',
        isBadClient=False,
        extra='',
        registeredBy=user.id,
        store_name=user.store_name
    )
    print(f'생성 완료: {user.store_name}의 김태수 고객 (정상고객)')

# 불량고객으로 등록
for user in bad_stores:
    client = Client.objects.create(
        nickName=f'{user.store_name}_김태수',
        name='김태수',
        phoneNumber=taesu_phone,
        gender='male',
        ages='40대',
        isBadClient=True,
        extra='불량고객 - 주의요망',
        registeredBy=user.id,
        store_name=user.store_name
    )
    print(f'생성 완료: {user.store_name}의 김태수 고객 (불량고객)')

print("\n=== 생성된 김태수 고객 정보 ===")
clients = Client.objects.filter(name='김태수').order_by('store_name')
print("매장명 | 전화번호 | 상태")
print("-" * 50)
for client in clients:
    status = '[불량]' if client.isBadClient else '[정상]'
    print(f'{client.store_name} | {client.decrypt_phone()} | {status}')

print(f'\n총 {clients.count()}개 매장에 김태수 고객이 등록되었습니다.') 