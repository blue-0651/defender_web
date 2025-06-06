# DEFENDER PROJECT API 사용 가이드

## 📋 개요

이 문서는 DEFENDER PROJECT의 백엔드 API를 Postman으로 테스트하기 위한 가이드입니다.

## 🔧 Postman 설정

### 1. 컬렉션 가져오기
1. Postman 실행
2. `Import` 버튼 클릭
3. `DEFENDER_PROJECT_API_Collection.postman_collection.json` 파일 선택
4. 가져오기 완료

### 2. 환경 변수 설정
컬렉션에 포함된 변수들:
- `base_url`: `http://3.38.245.204:8000` (개발서버)
- `local_url`: `http://127.0.0.1:8000` (로컬서버)
- `token`: `defender0651` (고정 인증 토큰)
- `user_id`: 사용자 ID
- `client_id`: 고객 ID
- `announcement_id`: 공지사항 ID

## 🚀 API 사용 순서

### 1단계: 사용자 생성 및 로그인

#### 1-1. 사용자 생성 (회원가입)
```
POST /api/users/create/
Content-Type: multipart/form-data

필수 필드:
- id: 사용자 ID (예: "store001")
- pw: 비밀번호 (예: "store123!")
- email: 이메일 (예: "store001@example.com")
- store_name: 매장명 (예: "다이소 강남점")
- phone_number: 전화번호 (예: "010-1234-5678")
- isAdmin: 관리자 여부 (true/false)
- business_license_image: 사업자등록증 이미지 (파일)
```

**샘플 요청:**
```
id: store001
pw: store123!
email: store001@example.com
store_name: 다이소 강남점
phone_number: 010-1234-5678
isAdmin: false
business_license_image: [파일 업로드]
```

#### 1-2. 로그인
```
POST /api/users/login/
Content-Type: application/json

{
  "id": "admin",
  "pw": "admin123"
}
```

**샘플 계정:**
- 관리자: `id: "admin", pw: "admin123"`
- 매장: `id: "store001", pw: "store123!"`

**응답 예시:**
```json
{
  "resultCode": "20",
  "message": "로그인 성공",
  "data": {
    "id": "admin",
    "email": "admin@example.com",
    "store_name": "관리자 매장",
    "isAdmin": true,
    "search_count": 1000,
    "usage_start_date": "2024-01-01",
    "usage_end_date": "2024-12-31",
    "business_license_image": "/media/licenseImage/admin_license.jpg"
  }
}
```

### 2단계: 인증 토큰 설정
이 시스템은 **고정 Bearer Token**을 사용합니다.
- 토큰 값: `defender0651`
- 이미 Postman 환경 변수 `token`에 설정되어 있습니다.
- 로그인은 사용자 정보 확인용이며, 별도 토큰을 발급하지 않습니다.

### 3단계: 고객 관리

#### 3-1. 고객 저장
```
POST /api/clients/save/
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "nickName": "홍길동123",
  "phoneNumber": "010-9876-5432",
  "name": "홍길동",
  "address": "서울시 강남구 테헤란로 123",
  "memo": "단골고객, 매월 정기주문",
  "isBadClient": false,
  "userId": "store001"
}
```

**필드 설명:**
- `nickName`: 고유한 고객 식별자 (중복 불가)
- `phoneNumber`: 암호화되어 저장됨
- `name`: 고객 실명 (선택사항)
- `address`: 주소 정보 (선택사항)
- `memo`: 고객 관련 메모 (선택사항)
- `isBadClient`: 불량고객 여부 (기본값: false)
- `userId`: 등록하는 매장 사용자 ID

#### 3-2. 불량고객 체크
```
POST /api/clients/check-bad-client/
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "phoneNumber": "010-9876-5432",
  "userId": "store001"
}
```

**응답 예시:**
```json
{
  "resultCode": "20",
  "message": "불량고객입니다.",
  "data": {
    "isBadClient": true,
    "clientInfo": {
      "nickName": "홍길동123",
      "name": "홍길동",
      "memo": "결제 지연 이력 있음",
      "registeredBy": "store002",
      "store_name": "다이소 역삼점"
    }
  }
}
```

## 📊 응답 코드 설명

| resultCode | 의미 | 설명 |
|------------|------|------|
| "20" | 성공 | 요청이 성공적으로 처리됨 |
| "30" | 중복 | 데이터 중복 (예: 닉네임 중복) |
| "40" | 실패 | 요청 실패 또는 오류 |

## 🔐 인증 방식

### Bearer Token 인증 (고정 토큰)
모든 API 요청 시 헤더에 포함:
```
Authorization: Bearer defender0651
```

**중요:** 이 시스템은 고정된 Bearer Token을 사용합니다.
- 토큰 값: `defender0651`
- 로그인 API는 사용자 정보 확인용이며, 토큰을 발급하지 않습니다.
- 모든 인증이 필요한 API에는 위 토큰을 사용하세요.

## 📝 주요 API 엔드포인트

### 사용자 관리
- `POST /api/users/login/` - 로그인
- `POST /api/users/create/` - 사용자 생성
- `POST /api/users/read/` - 사용자 목록 조회
- `PUT /api/users/{id}/update/` - 사용자 정보 수정
- `DELETE /api/users/{id}/delete/` - 사용자 삭제 (ID로)
- `DELETE /api/users/email/{email}/delete/` - 사용자 삭제 (이메일로)
- `PUT /api/users/update-password/` - 비밀번호 변경
- `POST /api/users/{id}/adjust-search-count/` - 검색 횟수 조정
- `POST /api/users/{id}/set-usage-period/` - 사용 기간 설정
- `GET /api/users/{id}/check-status/` - 사용자 상태 확인

### 고객 관리
- `POST /api/clients/save/` - 고객 저장
- `POST /api/clients/list/` - 고객 목록 조회
- `PUT /api/clients/{id}/update/` - 고객 정보 수정
- `DELETE /api/clients/{id}/delete/` - 고객 삭제
- `POST /api/clients/search/` - 고객 검색
- `POST /api/clients/search-by-phone/` - 전화번호로 고객 검색
- `POST /api/clients/check-bad-client/` - 불량고객 체크
- `POST /api/clients/get-by-nickname/` - 닉네임으로 고객 조회
- `POST /api/clients/check-nickname/` - 닉네임 중복 확인
- `POST /api/clients/search-phone-and-decrease/` - 전화번호 검색 및 횟수 차감

### 공지사항 관리
- `POST /api/announce/save/` - 공지사항 저장
- `POST /api/announce/list/` - 공지사항 목록 조회
- `PUT /api/announce/{id}/update/` - 공지사항 수정
- `DELETE /api/announce/{id}/delete/` - 공지사항 삭제

## 🛠️ 테스트 시나리오

### 기본 테스트 플로우
1. **사용자 생성** → 새 계정 생성
   ```
   id: store001, pw: store123!, email: store001@example.com
   store_name: 다이소 강남점, phone_number: 010-1234-5678
   ```

2. **로그인** → 사용자 정보 확인 (토큰은 이미 설정됨)
   ```
   id: store001, pw: store123!
   ```

3. **고객 저장** → 새 고객 정보 등록
   ```
   nickName: 홍길동123, phoneNumber: 010-9876-5432
   name: 홍길동, userId: store001
   ```

4. **불량고객 체크** → 전화번호로 불량고객 여부 확인
   ```
   phoneNumber: 010-9876-5432, userId: store001
   ```

5. **고객 검색** → 등록된 고객 정보 검색
   ```
   keyword: 홍길동, userId: store001
   ```

6. **공지사항 관리** → 공지사항 CRUD 테스트
   ```
   title: 시스템 점검 안내, userId: admin
   ```

### 고급 테스트 시나리오

#### 1. 중복 데이터 테스트
- **닉네임 중복**: 같은 `nickName`으로 고객 등록 시도
  ```json
  응답: {"resultCode": "30", "message": "아이디가 이미 존재합니다."}
  ```

- **전화번호 중복**: 같은 매장에서 동일 전화번호 등록 시 기존 정보 업데이트

#### 2. 권한 테스트
- 다른 사용자의 고객 정보 수정/삭제 시도
- 매장 소유자가 아닌 고객 정보 접근 시도

#### 3. 검색 횟수 제한 테스트
- `search-phone-and-decrease` API로 검색 횟수 차감 확인
- 검색 횟수 0일 때 API 호출 결과 확인

#### 4. 사용 기간 만료 테스트
- `usage_end_date`가 지난 계정으로 API 호출
- 관리자 권한으로 사용 기간 연장 테스트

## 🚨 주의사항

1. **파일 업로드**: 사용자 생성 시 `business_license_image`는 실제 이미지 파일을 업로드해야 합니다.
2. **전화번호 암호화**: 전화번호는 서버에서 자동으로 암호화되어 저장됩니다.
3. **검색 횟수 제한**: 사용자별로 검색 횟수가 제한되어 있습니다.
4. **사용 기간**: 사용자별로 서비스 이용 기간이 설정되어 있습니다.

## 🔍 디버깅 팁

1. **응답 확인**: 모든 응답에는 `resultCode`, `message`, `data` 필드가 포함됩니다.
2. **로그 확인**: 서버 로그에서 요청/응답 상세 정보를 확인할 수 있습니다.
3. **네트워크 오류**: 서버 연결 실패 시 `base_url` 변수를 확인하세요.
4. **인증 오류**: 토큰이 `defender0651`로 정확히 설정되어 있는지 확인하세요.

## 📞 문의사항

API 사용 중 문제가 발생하면 개발팀에 문의하시기 바랍니다.

---

**마지막 업데이트:** 2025년 3월 22일 