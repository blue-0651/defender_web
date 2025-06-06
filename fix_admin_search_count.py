import os
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'defender_project.settings')
django.setup()

from defender.models import User

# admin 계정들의 검색 가능 횟수를 1000회로 설정
admin_users = ['admin1', 'admin2', 'admin3', 'defender']

print("=== admin 계정 검색 가능 횟수 수정 시작 ===")

for user_id in admin_users:
    try:
        user = User.objects.get(id=user_id)
        old_count = user.search_count
        user.set_search_count(1000)
        print(f'{user_id}: {old_count}회 -> 1000회로 설정 완료')
    except User.DoesNotExist:
        print(f'{user_id}: 사용자를 찾을 수 없습니다.')

print("\n=== 수정 후 admin 계정 상태 확인 ===")
admin_users_db = User.objects.filter(id__in=admin_users)
for user in admin_users_db:
    print(f'{user.id}: {user.search_count}회')

print("\n모든 admin 계정의 검색 가능 횟수가 수정되었습니다.") 