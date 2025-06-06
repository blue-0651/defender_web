import os
import django
import random
from datetime import datetime, timedelta

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'defender_project.settings')
django.setup()

from defender.models import User, Client

# 기존 고객 데이터 삭제
Client.objects.all().delete()

# 사용자(매장) 목록 가져오기
users = list(User.objects.filter(id__startswith='user')[:6])  # 6개 매장만 선택

# 고객 데이터 생성을 위한 기초 데이터
names = [
    '김민수', '이영희', '박철수', '최지영', '정현우', '강서연',
    '윤미래', '장동민', '임수정', '한지민', '오태양', '신하늘'
]

ages = ['20대', '30대', '40대', '50대']
genders = ['male', 'female']

# 불량고객이 될 인덱스 미리 선정 (총 30개 중 10개)
total_clients = 30
bad_indices = set(random.sample(range(total_clients), 10))

# 고객 데이터 생성
clients_created = 0
bad_clients_created = 0

# 각 매장별로 5명의 고객 생성
for user in users:
    for i in range(5):
        current_index = clients_created
        is_bad = current_index in bad_indices
        
        client = Client.objects.create(
            nickName=f'{user.store_name}_고객{i+1}',
            name=random.choice(names),
            phoneNumber=f'010-{random.randint(1000,9999)}-{random.randint(1000,9999)}',
            gender=random.choice(genders),
            ages=random.choice(ages),
            isBadClient=is_bad,
            extra='불량고객 - 주의요망' if is_bad else '',
            registeredBy=user.id,
            store_name=user.store_name
        )
        
        clients_created += 1
        if is_bad:
            bad_clients_created += 1
            
        print(f'생성된 고객: {client.name} ({client.store_name}) - {"불량" if is_bad else "정상"}고객')

print(f'\n총 {clients_created}명의 고객 데이터 생성 완료 (불량고객: {bad_clients_created}명)')

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