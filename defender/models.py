from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.db.models.signals import post_save
from django.dispatch import receiver


class Announcement(models.Model):
    title = models.CharField(max_length=100, null=True, verbose_name='제목')
    userId = models.CharField(max_length=100, default='unknown', verbose_name='아이디')
    #phonenumber = models.CharField(max_length=20, null=True ,verbose_name='전화번호')
    memo = models.TextField(blank=True,  verbose_name='메모')
    createDate = models.DateTimeField(default=timezone.now, verbose_name='생성일')

    def __str__(self):
        return self.userId

    class Meta:
        db_table = 'announcement'
        ordering = ['-createDate']
        verbose_name = '공지사항'
        verbose_name_plural = '공지사항 목록'

class User(models.Model):
    id = models.CharField(max_length=50, primary_key=True, verbose_name='아이디')
    pw = models.CharField(max_length=128, verbose_name='비밀번호')
    isAdmin = models.BooleanField(default=False, verbose_name='관리자 여부')
    createDate = models.DateTimeField(default=timezone.now,verbose_name='생성일' )
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name='이메일')
    store_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='매장명')
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='전화번호')
    search_count = models.IntegerField(default=0, verbose_name='조회가능횟수')
   # usage_count = models.IntegerField(default=0, verbose_name='이용가능횟수')
    business_license_image = models.CharField(max_length=255, blank=True, null=True, verbose_name='사업자등록증')
    usage_start_date = models.DateField(blank=True, null=True, verbose_name='이용 가능 시작일')
    usage_end_date = models.DateField(blank=True, null=True, verbose_name='이용 가능 마감일')
    valid_until = models.DateTimeField(blank=True, null=True, verbose_name='사용기간')
    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        # 비밀번호가 평문일 경우에만 해시화
        if self.pw and not self.pw.startswith('pbkdf2_sha256$'):
            self.pw = make_password(self.pw)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        """
        입력된 평문 비밀번호가 저장된 해시와 일치하는지 확인
        """
        return check_password(raw_password, self.pw)

    # 조회가능횟수 증가 함수
    def increase_search_count(self, amount=1):
        """
        조회가능횟수를 지정된 양만큼 증가시킴
        """
        self.search_count += amount
        self.save(update_fields=['search_count'])
        return self.search_count

    # 조회가능횟수 감소 함수
    def decrease_search_count(self, amount=1):
        """
        조회가능횟수를 지정된 양만큼 감소시킴 (0 미만으로 내려가지 않도록 함)
        """
        self.search_count = max(0, self.search_count - amount)
        self.save(update_fields=['search_count'])
        return self.search_count

    # 조회가능횟수 설정 함수
    def set_search_count(self, count):
        """
        조회가능횟수를 특정 값으로 설정
        """
        self.search_count = max(0, count)  # 음수 방지
        self.save(update_fields=['search_count'])
        return self.search_count

    # # 이용가능횟수 증가 함수
    # def increase_usage_count(self, amount=1):
    #     """
    #     이용가능횟수를 지정된 양만큼 증가시킴
    #     """
    #     self.usage_count += amount
    #     self.save(update_fields=['usage_count'])
    #     return self.usage_count
    #
    # # 이용가능횟수 감소 함수
    # def decrease_usage_count(self, amount=1):
    #     """
    #     이용가능횟수를 지정된 양만큼 감소시킴 (0 미만으로 내려가지 않도록 함)
    #     """
    #     self.usage_count = max(0, self.usage_count - amount)
    #     self.save(update_fields=['usage_count'])
    #     return self.usage_count
    #
    # # 이용가능횟수 설정 함수
    # def set_usage_count(self, count):
    #     """
    #     이용가능횟수를 특정 값으로 설정
    #     """
    #     self.usage_count = max(0, count)  # 음수 방지
    #     self.save(update_fields=['usage_count'])
    #     return self.usage_count

    # 사용기간 설정 함수
    def set_usage_period(self, start_date=None, end_date=None, days=30):
        """
        사용기간 설정
        start_date: 시작일 (None인 경우 오늘 날짜)
        end_date: 종료일 (None인 경우 start_date + days)
        days: 시작일로부터의 사용 일수 (end_date가 None일 때만 사용)
        """
        if start_date is None:
            start_date = date.today()

        if end_date is None:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = start_date + timedelta(days=days)

        self.usage_start_date = start_date
        self.usage_end_date = end_date
        self.save(update_fields=['usage_start_date', 'usage_end_date'])

        return {
            'start_date': self.usage_start_date,
            'end_date': self.usage_end_date
        }

    # 사용기간 연장 함수
    def extend_usage_period(self, days=30):
        """
        현재 사용기간에 지정된 일수만큼 추가
        """
        today = date.today()

        # 사용기간이 설정되어 있지 않은 경우
        if self.usage_start_date is None or self.usage_end_date is None:
            return self.set_usage_period(days=days)

        # 사용기간이 이미 만료된 경우
        if self.usage_end_date < today:
            # 오늘부터 새로 기간 설정
            return self.set_usage_period(days=days)

        # 현재 종료일에서 연장
        self.usage_end_date = self.usage_end_date + timedelta(days=days)
        self.save(update_fields=['usage_end_date'])

        return {
            'start_date': self.usage_start_date,
            'end_date': self.usage_end_date
        }

    # 사용기간 유효성 확인 함수
    def is_usage_period_valid(self):
        """
        현재 사용기간이 유효한지 확인
        """
        today = date.today()

        # 시작일 또는 종료일이 설정되지 않은 경우
        if self.usage_start_date is None or self.usage_end_date is None:
            return False

        # 현재 날짜가 사용기간 내에 있는지 확인
        return self.usage_start_date <= today <= self.usage_end_date

    # 남은 사용기간 계산 함수
    def get_remaining_days(self):
        """
        남은 사용기간을 일수로 반환
        """
        today = date.today()

        # 시작일 또는 종료일이 설정되지 않은 경우
        if self.usage_start_date is None or self.usage_end_date is None:
            return 0

        # 이미 만료된 경우
        if self.usage_end_date < today:
            return 0

        # 시작일이 미래인 경우 (아직 시작 안함)
        if self.usage_start_date > today:
            return (self.usage_end_date - self.usage_start_date).days

        # 남은 일수 계산
        return (self.usage_end_date - today).days

    class Meta:
        db_table = 'users'
        ordering = ['id']
        verbose_name = '사용자'
        verbose_name_plural = '사용자 목록'

# 암호화 키 설정 (실제 프로젝트에서는 settings.py에 저장하고 환경변수에서 로드하는 것이 좋음)
# settings.py에 다음 코드 추가:
# ENCRYPTION_KEY = Fernet.generate_key()  # 최초 한 번만 실행하고 저장된 키를 사용
# 고객 클래스
class Client(models.Model):
    GENDER_CHOICES = (
        ('male', '남성'),
        ('female', '여성'),
    )
    id = models.AutoField(primary_key=True)
    nickName = models.CharField(max_length=100 ,unique=True, null=False,verbose_name='고객 별명')
    name = models.CharField(max_length=100, verbose_name='고객이름')
    phoneNumber = models.CharField(max_length=1000,verbose_name='고객 전화번호')  # 암호화된 텍스트를 저장하기 위해 TextField 사용
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name='성별')
    ages = models.CharField(max_length=20, verbose_name='연령대')
    isBadClient = models.BooleanField(default=False, verbose_name='불량 고객 유무')
    extra = models.TextField(blank=True, null=True, verbose_name='특이사항')
    createDate = models.DateTimeField(default=timezone.now, verbose_name='생성일')
    registeredBy = models.CharField(max_length=50, blank=True, null=True, verbose_name='등록한 사용자 ID')
    store_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='등록한 사용자 매장명')

    def __str__(self):
        return self.name

    @property
    def cipher_suite(self):
        return Fernet(settings.ENCRYPTION_KEY)

    def encrypt_phone(self, phone):
        """전화번호 암호화"""
        if phone:
            return self.cipher_suite.encrypt(phone.encode()).decode()
        return None

    def decrypt_phone(self):
        """전화번호 복호화"""
        if self.phoneNumber:
            try:
                return self.cipher_suite.decrypt(self.phoneNumber.encode()).decode()
            except Exception:
                return "복호화 오류"
        return None

    def save(self, *args, **kwargs):
        # 전화번호가 암호화되지 않은 상태라면 암호화
        if self.phoneNumber and not self.phoneNumber.startswith('gAAA'):
            self.phoneNumber = self.encrypt_phone(self.phoneNumber)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'clients2'
        ordering = ['-createDate']
        verbose_name = '고객'
        verbose_name_plural = '고객 목록'

# Store 모델 추가
class Store(models.Model):
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='주소')
    ownerId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stores', verbose_name='소유자 ID', db_column='ownerId')
    province = models.CharField(max_length=50, blank=True, null=True, verbose_name='소재지')
    storeName = models.CharField(max_length=100, blank=True, null=True, verbose_name='매장명')
    createDate = models.DateTimeField(default=timezone.now, verbose_name='생성일')
    isDefenderActive = models.BooleanField(default=True, verbose_name='앱 사용 여부')

    def __str__(self):
        return f"{self.storeName or self.ownerId}의 매장"

    class Meta:
        db_table = 'stores'
        ordering = ['-createDate']
        verbose_name = '매장'
        verbose_name_plural = '매장 목록'

# User 생성 시 Store 자동 생성을 위한 시그널 등록
@receiver(post_save, sender=User)
def create_store_for_user(sender, instance, created, **kwargs):
    """
    사용자가 생성되면 자동으로 매장 정보를 생성합니다.
    """
    if created:  # 새로운 사용자가 생성된 경우에만
        Store.objects.create(
            ownerId=instance,
            address=None,
            province=None,
            storeName=instance.store_name
        )