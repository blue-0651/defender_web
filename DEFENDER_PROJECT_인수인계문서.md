# 🔐 DEFENDER PROJECT 인수인계 문서

**작성일:** 2025년 5월26일 
**프로젝트:** 불량고객 관리 시스템

---

## 📋 1. 프로젝트 개요

### 1-1. 프로젝트 구성
- **백엔드(웹서버):** Django REST Framework 기반 API 서버
- **프론트엔드(모바일앱):** Android Kotlin 기반 네이티브 앱
- **데이터베이스:** PostgreSQL
- **서버 환경:** AWS EC2 (Ubuntu)

### 1-2. 주요 기능
- 사용자 관리 (로그인/회원가입)
- 고객 정보 관리 (불량고객 체크 시스템)
- 공지사항 관리
- 매장 관리

### 1-3. 프로젝트 구조
```
defender_project/
├── defender/                 # Django 메인 앱
│   ├── views/               # API 뷰 파일들
│   ├── models.py            # 데이터베이스 모델
│   ├── migrations/          # DB 마이그레이션 파일
│   └── middleware.py        # 커스텀 미들웨어
├── defender_project/        # Django 프로젝트 설정
│   ├── settings.py          # 주요 설정 파일
│   ├── urls.py             # URL 라우팅
│   └── defender.conf       # Nginx 설정
├── defender_app/           # Android 앱 소스코드
└── defender_env/           # Python 가상환경
```

---

## 🌐 2. 서버 및 네트워크 정보

### 2-1. 운영 서버 정보

| 구분 | 정보 | 비고 |
|------|------|------|
| **운영 서버 IP** | `3.38.245.204` | AWS EC2 인스턴스 |
| **웹 접속 주소** | `http://3.38.245.204` | 포트 80 (nginx) |
| **Django 서버** | `http://127.0.0.1:8000` | 내부 포트 |
| **SSH 접속** | `ssh ec2-user@3.38.245.204` | AWS 기본 계정 |

### 2-2. 허용된 호스트 목록
```python
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    '3.38.245.204', 
    '192.168.0.4', 
    '10.30.2.91'
]
```

### 2-3. 개발 환경 주소
- **로컬 개발:** `http://127.0.0.1:8000`
- **내부 네트워크:** `http://192.168.0.4:8000`

---

## 🔑 3. 중요 계정 및 비밀번호 정보

### 3-1. Django 설정 (실제 정보)

**⚠️ 매우 중요한 보안 정보입니다!**

```python
# SECRET KEY (Django 암호화에 사용)
SECRET_KEY = 'django-insecure-*(iprgwcz2774y51v2=(pojqagou*nl%mh4i1+_r7n!e#c2a1*'

# 고객 전화번호 암호화 키
ENCRYPTION_KEY = b'fJIz6AZnv9LBoAlDGt0WhcZ9q11WOP6fwOjJhJwo600='
```

### 3-2. 데이터베이스 정보 (실제 정보)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'defender',
        'USER': 'postgres',
        'PASSWORD': '111222',
        'HOST': '3.38.245.204',
        'PORT': '5432',
    }
}
```

**데이터베이스 직접 접속:**
```bash
psql -h 3.38.245.204 -U postgres -d defender
# 비밀번호: 111222
```

### 3-3. 앱 인증 토큰(******)

```kotlin
// Android 앱에서 사용하는 Bearer 토큰
bearerToken: String = "defender0651"
```

### 3-4. Django 관리자 계정(********)

- **접속 주소:** `http://3.38.245.204/admin`
- **계정 생성 방법:** 
  ```bash
  python manage.py createsuperuser
  ```
- **⚠️ 실제 관리자 계정은 별도 전달 필요**

---

## 📱 4. 앱(Android) 상세 정보

### 4-1. 앱 기본 정보

```kotlin
applicationId = "com.daiso.depender"
versionName = "1.0.2-20250507"
minSdk = 28
targetSdk = 34
namespace = "com.daiso.depender"
```

### 4-2. 서버 연결 설정

```kotlin
// 운영 서버 주소
private var host: String = "http://3.38.245.204:80/"

// 개발용 주소 (주석 처리됨)
// private var host: String = "http://localhost:8000/"
// private var host: String = "http://192.168.0.4:8000/"
```

### 4-3. 주요 API 엔드포인트

| 기능 | 메소드 | 엔드포인트 | 설명 |
|------|--------|------------|------|
| 로그인 | POST | `/api/users/login/` | 사용자 인증 |
| 고객 목록 | POST | `/api/clients/list/` | 고객 리스트 조회 |
| 불량고객 체크 | POST | `/api/clients/check-bad-client/` | 전화번호로 불량고객 확인 |
| 고객 등록 | POST | `/api/clients/save/` | 새 고객 정보 등록 |
| 고객 수정 | PUT | `/api/clients/update/` | 고객 정보 수정 |
| 고객 상세 | POST | `/api/clients/get-client/` | 특정 고객 상세 정보 |
| 공지사항 | POST | `/api/announce/list/` | 공지사항 목록 |

### 4-4. Android 개발 환경

```bash
# Android SDK 경로
SDK_PATH = "/Users/mac_kyh/Library/Android/sdk"

# 빌드 명령어
./gradlew assembleDebug    # 디버그 빌드
./gradlew assembleRelease  # 릴리즈 빌드
```

---

## 🗄️ 5. 데이터베이스 구조

### 5-1. 주요 테이블

#### users 테이블
```sql
- id (VARCHAR): 사용자 ID (Primary Key)
- pw (VARCHAR): 해시된 비밀번호
- isAdmin (BOOLEAN): 관리자 여부
- email (VARCHAR): 이메일
- store_name (VARCHAR): 매장명
- phone_number (VARCHAR): 전화번호
- search_count (INTEGER): 조회가능횟수
- usage_start_date (DATE): 이용 시작일
- usage_end_date (DATE): 이용 종료일
- createDate (DATETIME): 생성일
```

#### clients2 테이블
```sql
- id (INTEGER): 고객 ID (Primary Key)
- nickName (VARCHAR): 고객 별명 (Unique)
- name (VARCHAR): 고객 이름
- phoneNumber (TEXT): 암호화된 전화번호
- gender (VARCHAR): 성별 (male/female)
- ages (VARCHAR): 연령대
- isBadClient (BOOLEAN): 불량고객 여부
- extra (TEXT): 특이사항
- registeredBy (VARCHAR): 등록한 사용자 ID
- store_name (VARCHAR): 등록한 매장명
- createDate (DATETIME): 생성일
```

#### stores 테이블
```sql
- id (INTEGER): 매장 ID (Primary Key)
- address (VARCHAR): 주소
- ownerId (VARCHAR): 소유자 ID (Foreign Key)
- province (VARCHAR): 소재지
- storeName (VARCHAR): 매장명
- isDefenderActive (BOOLEAN): 앱 사용 여부
- createDate (DATETIME): 생성일
```

#### announcement 테이블
```sql
- id (INTEGER): 공지 ID (Primary Key)
- title (VARCHAR): 제목
- userId (VARCHAR): 작성자 ID
- memo (TEXT): 내용
- createDate (DATETIME): 생성일
```


## 🛠️ 6. 개발 환경 설정

### 6-1. 백엔드 (Django) 설정

```bash
# 1. 프로젝트 디렉토리로 이동
cd /Users/mac_kyh/WebProjects/defender_project

# 2. 가상환경 활성화
source defender_env/bin/activate

# 3. 필수 패키지 설치
pip install django==4.2.19
pip install djangorestframework
pip install psycopg2-binary
pip install cryptography

# 4. 데이터베이스 마이그레이션
python manage.py migrate

# 5. 개발 서버 실행
python manage.py runserver

# 6. 관리자 계정 생성 (최초 1회)
python manage.py createsuperuser
```

### 6-2. 자주 사용하는 Django 명령어

```bash
# 마이그레이션 파일 생성
python manage.py makemigrations

# 마이그레이션 적용
python manage.py migrate

# 슈퍼유저 생성
python manage.py createsuperuser

# 개발 서버 실행 (디버그 모드)
python manage.py runserver --verbosity=2

# 정적 파일 수집 (배포시)
python manage.py collectstatic
```

## 🔧 7. 서버 배포 정보

### 7-1. Nginx 설정 (`defender.conf`)

```nginx
server {
    listen 80;
    server_name 3.38.245.204;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        root /home/ec2-user/projects/defender_project;
    }
    
    location /media/ {
        root /home/ec2-user/projects/defender_project;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 7-2. 서버 경로 정보

```bash
# 프로젝트 루트
/home/ec2-user/projects/defender_project

# 정적 파일 경로
/home/ec2-user/projects/defender_project/static/

# 미디어 파일 경로
/home/ec2-user/projects/defender_project/media/

# Nginx 설정 파일
/etc/nginx/sites-available/defender.conf
/etc/nginx/sites-enabled/defender.conf
```

### 7-3. 서버 관리 명령어

```bash
# Nginx 재시작
sudo systemctl restart nginx

# Nginx 상태 확인
sudo systemctl status nginx

# Django 서버 백그라운드 실행
nohup python manage.py runserver 127.0.0.1:8000 &

# 프로세스 확인
ps aux | grep python
```

## ⚠️ 9. 보안 주의사항

### 9-1. 절대 공개하면 안 되는 정보

**🚨 다음 정보들은 절대 GitHub 등 공개 저장소에 올리면 안 됩니다:**

- Django SECRET_KEY: `django-insecure-*(iprgwcz2774y51v2=(pojqagou*nl%mh4i1+_r7n!e#c2a1*`
- 데이터베이스 비밀번호: `111222`
- 암호화 키: `fJIz6AZnv9LBoAlDGt0WhcZ9q11WOP6fwOjJhJwo600=`
- Bearer 토큰: `defender0651`

### 9-2. 권장 보안 조치

1. **즉시 변경해야 할 항목:**
   - 데이터베이스 비밀번호
   - Django SECRET_KEY
   - Bearer 토큰
   - 관리자 계정 비밀번호

2. **환경변수 사용:**
   ```python
   # .env 파일 생성 후 사용
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   SECRET_KEY = os.getenv('SECRET_KEY')
   DB_PASSWORD = os.getenv('DB_PASSWORD')
   ```

3. **추가 보안 설정:**
   - HTTPS 적용 (현재 HTTP만 사용)
   - 방화벽 설정 (필요한 포트만 개방)
   - 정기적인 보안 업데이트

---

## 🆘 10. 문제 해결 가이드

### 10-1. 자주 발생하는 문제

#### 서버 연결 문제
```bash
# 문제: 서버에 접속이 안 됨
# 해결: 서버 상태 및 포트 확인
sudo netstat -tlnp | grep :8000
sudo systemctl status nginx
```

#### 데이터베이스 연결 오류
```bash
# 문제: DB 연결 실패
# 해결: PostgreSQL 서비스 확인
sudo systemctl status postgresql
sudo systemctl restart postgresql
```

#### 앱 로그인 실패
```bash
# 문제: 앱에서 로그인이 안 됨
# 해결: API 엔드포인트 및 토큰 확인
curl -X POST http://3.38.245.204/api/users/login/ \
  -H "Authorization: Bearer defender0651" \
  -H "Content-Type: application/json" \
  -d '{"id":"testuser","pw":"testpass"}'
```

### 10-2. 로그 확인 방법

```bash
# Django 개발 서버 로그
python manage.py runserver --verbosity=2

# Nginx 에러 로그
sudo tail -f /var/log/nginx/error.log

# Nginx 액세스 로그
sudo tail -f /var/log/nginx/access.log

# 시스템 로그
sudo journalctl -u nginx -f
```

### 10-3. 디버깅 팁

```python
# Django에서 디버그 정보 출력
import logging
logging.basicConfig(level=logging.DEBUG)

# API 응답 확인
from rest_framework.response import Response
return Response({"debug": "test"}, status=200)
```


## 📞 12. 연락처 및 추가 자료

### 12-1. 참고 문서

- [Django 공식 문서 (한글)](https://docs.djangoproject.com/ko/4.2/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Android 개발 가이드](https://developer.android.com/guide)
- [PostgreSQL 문서](https://www.postgresql.org/docs/)

### 12-2. 유용한 도구(********)

- **API 테스트:** Postman, curl
- **데이터베이스 관리:** pgAdmin, DBeaver
- **서버 모니터링:** htop, netstat
- **로그 분석:** tail, grep, journalctl

---

## ⚠️ 최종 주의사항

**🔴 이 문서에 포함된 모든 비밀번호, 키, 토큰은 실제 운영 정보입니다.**

**인수인계 완료 후 반드시 다음 작업을 수행하세요:**

1. **모든 비밀번호 즉시 변경**
2. **이 문서를 안전한 곳에 보관**
3. **불필요한 복사본 삭제**
4. **새로운 보안 정책 수립**

**문의사항이 있으시면 언제든 연락 주세요!**

---

*문서 작성일: 2025년 3월 22일*  
*최종 수정일: 2025년 3월 22일*  
*버전: 1.0* 
