import os
import django
import random

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'defender_project.settings')
django.setup()

from defender.models import User, Client

# 기존 오태양 고객 데이터 삭제
Client.objects.filter(name='오태양').delete()

# 기존 매장 목록에서 광주 노래방 03호점을 제외한 매장들 선택
users = list(User.objects.filter(id__startswith='user'))
available_users = [u for u in users if u.store_name != '광주 노래방 03호점']
selected_users = random.sample(available_users, 2)

# 오태양의 공통 전화번호 생성
taeyang_phone = f'010-{random.randint(1000,9999)}-{random.randint(1000,9999)}'

# 광주 노래방 03호점에 불량고객으로 등록
gwangju_user = User.objects.get(store_name='광주 노래방 03호점')
client = Client.objects.create(
    nickName=f'{gwangju_user.store_name}_오태양',
    name='오태양',
    phoneNumber=taeyang_phone,
    gender='male',
    ages='30대',
    isBadClient=True,
    extra='불량고객 - 주의요망',
    registeredBy=gwangju_user.id,
    store_name=gwangju_user.store_name
)
print(f'생성 완료: {gwangju_user.store_name}의 오태양 고객 (전화번호: {client.decrypt_phone()})')

# 두 개의 다른 매장에 동일한 전화번호로 오태양 고객 추가
for user in selected_users:
    client = Client.objects.create(
        nickName=f'{user.store_name}_오태양',
        name='오태양',
        phoneNumber=taeyang_phone,
        gender='male',
        ages='30대',
        isBadClient=False,
        extra='',
        registeredBy=user.id,
        store_name=user.store_name
    )
    print(f'생성 완료: {user.store_name}의 오태양 고객 (전화번호: {client.decrypt_phone()})') 