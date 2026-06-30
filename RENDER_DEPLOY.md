# 우리가족 시간표 - Render 배포 가이드

> PythonAnywhere 접속이 막혀 Render로 이전. 이 문서는 Render 기준 배포/접속 방법입니다.
> (기존 PythonAnywhere 가이드는 `DEPLOY.md` 참고)

## 서비스 정보

| 항목 | 내용 |
|------|------|
| **호스팅** | Render (무료 플랜) |
| **GitHub 저장소** | https://github.com/Bokang-Lab/family-schedule (Public) |
| **GitHub 계정** | Bokang-Lab |
| **서비스 URL** | 배포 후 생성됨 (`https://family-schedule-xxxx.onrender.com`) |
| **DB** | Render 무료 PostgreSQL (`family-schedule-db`) |

---

## 최초 배포 (Blueprint 방식)

`render.yaml`이 저장소에 있어 **웹서비스 + 무료 PostgreSQL을 자동 생성**합니다.

### 1단계 — Render 가입 & GitHub 연결
1. https://render.com 접속 → **Sign up**
2. **GitHub 계정(Bokang-Lab)으로 로그인** (가장 간편)
3. Render의 저장소 접근 권한 요청 시 → `family-schedule` 저장소 허용

### 2단계 — Blueprint로 배포
1. 대시보드 우상단 **"New +"** → **"Blueprint"**
2. `Bokang-Lab/family-schedule` 저장소 선택 → **Connect**
3. Render가 `render.yaml`을 자동 인식 (웹서비스 + DB 구성 표시)
4. **"Apply"** 클릭 → 빌드 시작 (몇 분 소요)

### 3단계 — 접속 확인
- 생성된 URL(`https://family-schedule-xxxx.onrender.com`)로 접속
- 새 DB이므로 **가족 새로 만들기**부터 시작
- 가족 코드를 가족 구성원에게 공유

---

## 소스 수정 후 업데이트 (자동 배포)

PythonAnywhere와 달리 **pull/Reload가 필요 없습니다.** GitHub에 push만 하면 Render가 자동 재배포합니다.

```bash
cd F:\python\Personal\schedule
git add 수정한파일
git commit -m "변경 내용 설명"
git push
```

→ push하면 Render가 감지해 자동으로 빌드 & 배포. 대시보드의 **Logs** 탭에서 진행 상황 확인 가능.

---

## 알아둘 점 (무료 플랜 특성)

1. **슬립(Sleep)** — 15분간 접속이 없으면 서버가 잠듦.
   다음 첫 접속이 **30초~1분 정도 느림** (그 후 정상). 가족용이라 큰 문제 없음.

2. **무료 PostgreSQL 만료** — Render 무료 DB는 생성 후 일정 기간(정책상 약 30일)
   경과 시 만료될 수 있음. 만료 알림이 오면 새 DB 생성 필요 (이때 데이터 초기화).

3. **데이터 백업 권장** — 중요한 일정은 주기적으로 백업해두는 게 안전.
   Render 대시보드 → 해당 PostgreSQL → **Backups** 또는 `pg_dump`로 내보내기 가능.

---

## 환경변수 (render.yaml에서 자동 설정)

| 변수 | 설명 |
|------|------|
| `DATABASE_URL` | PostgreSQL 연결 문자열 (DB에서 자동 주입) |
| `SECRET_KEY` | 세션 암호화 키 (Render가 자동 생성·고정) |
| `PYTHON_VERSION` | `3.11.0` |

> 코드는 `DATABASE_URL`이 없으면 로컬 SQLite로 동작하므로, PC에서 개발/테스트는 그대로 가능.

---

## 문제 발생 시

- **빌드 실패**: Render 대시보드 → 웹서비스 → **Logs** 탭에서 에러 확인
- **DB 연결 오류**: 환경변수 `DATABASE_URL`이 제대로 주입됐는지 확인
- **502/접속 안 됨**: 슬립 상태일 수 있으니 30초~1분 대기 후 재시도

---

## 참고: 로컬 실행 (PC에서 테스트)

```bash
cd F:\python\Personal\schedule
pip install -r requirements.txt
python app.py
```
→ http://localhost:5000 (로컬은 SQLite `instance/schedule.db` 사용)
