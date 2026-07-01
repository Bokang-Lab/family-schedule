# 우리가족 시간표 - DB 백업 & 복원 가이드 (Render PostgreSQL)

> ⚠️ **왜 필요한가?**
> Render 무료 PostgreSQL은 **자동 백업이 없고**, 생성 후 약 30일이 지나면 만료될 수 있습니다.
> 만료되면 데이터가 사라지므로, **주기적으로 직접 백업**해두어야 합니다.
> 권장: **매주 1회** 또는 일정을 많이 입력한 날 백업.

---

## 준비물: PostgreSQL 클라이언트 설치 (최초 1회)

백업하려면 PC에 `pg_dump` / `psql` 도구가 필요합니다.

### Windows 설치
1. https://www.postgresql.org/download/windows/ 접속
2. **"Download the installer"** → 최신 버전 설치 프로그램 실행
3. 설치 중 구성요소 선택 화면에서 **"Command Line Tools"** 는 반드시 체크
   (Server, pgAdmin 등은 백업만 할 거면 체크 안 해도 됨)
4. 설치 완료 후, 설치 경로의 `bin` 폴더를 확인
   (보통 `C:\Program Files\PostgreSQL\16\bin`)

> 설치 후 PowerShell에서 `pg_dump --version` 이 동작하면 준비 완료.
> 안 되면 위 `bin` 폴더를 시스템 환경변수 PATH에 추가하거나, 명령 앞에 전체 경로를 붙여 실행.

---

## 1단계: External Database URL 확인

1. Render 대시보드 → 왼쪽 **Resources** (또는 My home)
2. **`family-schedule-db`** (PostgreSQL) 클릭
3. **Connect** 버튼 또는 **Info** 페이지에서 **"External Database URL"** 복사
   - `postgresql://user:password@host.oregon-postgres.render.com/dbname` 형태
   - ⚠️ 이 주소에는 비밀번호가 들어있으니 외부에 공유 금지

> **Internal**이 아니라 반드시 **External** Database URL을 써야 PC에서 접속됩니다.

---

## 2단계: 백업 실행 (pg_dump)

PowerShell을 열고 아래 실행 (URL은 1단계에서 복사한 값으로 교체):

```powershell
cd F:\python\Personal\schedule
$env:PGSSLMODE = "require"
pg_dump "여기에_External_Database_URL_붙여넣기" -F c -f "backup_$(Get-Date -Format yyyyMMdd).dump"
```

- 성공하면 `backup_20260701.dump` 같은 파일이 생성됨 (날짜 자동 포함)
- `-F c` = 압축된 커스텀 포맷 (복원 시 `pg_restore` 사용)

### (선택) 사람이 읽을 수 있는 SQL 텍스트로 백업하려면
```powershell
pg_dump "External_Database_URL" -f "backup_$(Get-Date -Format yyyyMMdd).sql"
```

> 💡 백업 파일은 `instance/`, `deploy/`, `*.db` 처럼 .gitignore에 이미 걸러지지 않으므로,
> GitHub에 실수로 올라가지 않게 **저장소 밖 폴더**(예: `F:\백업\`)에 보관 권장.

---

## 3단계: 복원 (새 DB로 되살리기)

DB가 만료됐거나 사고가 나면, 새 PostgreSQL을 만든 뒤 백업을 밀어넣습니다.

### (1) 새 DB 준비
- Render에서 새 무료 PostgreSQL 생성 → 새 **External Database URL** 확보
- (또는 Blueprint 재배포로 자동 생성된 DB 사용)

### (2) 복원 명령
**`.dump` (커스텀 포맷) 복원:**
```powershell
$env:PGSSLMODE = "require"
pg_restore --clean --if-exists --no-owner -d "새_External_Database_URL" "backup_20260701.dump"
```

**`.sql` (텍스트) 복원:**
```powershell
psql "새_External_Database_URL" -f "backup_20260701.sql"
```

### (3) 앱 연결 갱신
- 새 DB를 쓴다면 Render 웹서비스의 `DATABASE_URL` 환경변수를 새 DB로 연결
  (Blueprint로 함께 만들면 자동 연결됨)
- 웹서비스 **Manual Deploy** 또는 재시작 후 접속 확인

---

## 백업 주기 & 팁

| 항목 | 권장 |
|------|------|
| 백업 주기 | 매주 1회 + 일정 대량 입력 후 |
| 보관 위치 | 저장소 밖 폴더 (예: `F:\백업\schedule\`) |
| 보관 개수 | 최근 4~5개 정도 유지 (오래된 건 삭제) |
| 만료 대비 | Render 만료 알림 메일 오면 즉시 백업 → 새 DB 복원 |

---

## 자주 겪는 문제

- **`pg_dump: command not found`** → PostgreSQL 클라이언트 미설치 또는 PATH 미등록.
  명령 앞에 전체 경로 사용: `& "C:\Program Files\PostgreSQL\16\bin\pg_dump.exe" ...`
- **버전 불일치 경고** (`server version mismatch`) → PC의 pg_dump 버전이 서버보다 낮으면 발생.
  최신 PostgreSQL 클라이언트로 업데이트하면 해결.
- **접속 안 됨 / SSL 오류** → `$env:PGSSLMODE = "require"` 설정했는지 확인, Internal이 아닌 **External URL** 사용 확인.
- **비밀번호 노출 주의** → External URL에 비밀번호 포함. 화면 공유·커밋 금지.

---

## 참고
- 배포 가이드: `RENDER_DEPLOY.md`
- 이 앱은 로컬(PC)에서는 SQLite(`instance/schedule.db`)를 쓰므로, 로컬 데이터 백업은 이 파일을 복사하면 됨.
