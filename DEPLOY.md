# 우리가족 시간표 - 배포 및 운영 가이드

## 서비스 정보

| 항목 | 내용 |
|------|------|
| **서비스 URL** | https://daegu.pythonanywhere.com |
| **호스팅** | PythonAnywhere (무료 플랜) |
| **PythonAnywhere ID** | daegu |
| **GitHub 저장소** | https://github.com/Bokang-Lab/family-schedule (Public) |
| **GitHub 계정** | Bokang-Lab |

---

## 프로젝트 경로

| 위치 | 경로 |
|------|------|
| **PC 소스코드** | `F:\python\Personal\schedule\` |
| **PythonAnywhere 소스** | `/home/daegu/mysite/` |
| **PythonAnywhere DB** | `/home/daegu/mysite/instance/schedule.db` |
| **WSGI 설정 파일** | `/var/www/daegu_pythonanywhere_com_wsgi.py` |
| **에러 로그** | `/var/log/daegu.pythonanywhere.com.error.log` |
| **서버 로그** | `/var/log/daegu.pythonanywhere.com.server.log` |

---

## 소스 수정 후 업데이트 방법

### Step 1: PC에서 수정 & GitHub Push

```bash
cd F:\python\Personal\schedule
git add 수정한파일
git commit -m "변경 내용 설명"
git push
```

### Step 2: PythonAnywhere에서 Pull

PythonAnywhere 대시보드 → **Consoles** → **Bash** 콘솔 열기:

```bash
cd ~/mysite && git pull
```

### Step 3: Reload

PythonAnywhere 대시보드 → **Web** 탭 → 초록색 **"Reload daegu.pythonanywhere.com"** 버튼 클릭

> **이 3단계가 전부입니다: push → pull → Reload**

---

## 에러 발생 시 로그 확인

PythonAnywhere Bash에서:

```bash
cat /var/log/daegu.pythonanywhere.com.error.log | tail -30
```

---

## DB 백업/복원

### 백업 (PythonAnywhere Bash)

```bash
cp ~/mysite/instance/schedule.db ~/schedule_backup_$(date +%Y%m%d).db
```

### PC에서 PythonAnywhere로 DB 업로드

1. PythonAnywhere → **Files** 메뉴
2. `/home/daegu/mysite/instance/` 경로로 이동
3. `schedule.db` 파일 업로드
4. **Web** → **Reload**

---

## PythonAnywhere 전체 재설치 (만약 필요 시)

```bash
cd ~ && rm -rf ~/mysite ~/family-schedule
git clone https://github.com/Bokang-Lab/family-schedule.git ~/mysite
mkdir -p ~/mysite/instance
pip3.10 install --user flask flask-sqlalchemy python-dotenv
```

DB 업로드 후 → **Web** → **Reload**

### WSGI 설정 (Web → WSGI configuration file)

```python
import sys
import os

project_home = '/home/daegu/mysite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.chdir(project_home)

from app import app as application
```

---

## 참고

- PythonAnywhere 무료 플랜은 **3개월마다 갱신** 필요 (이메일 알림 옴, 버튼 클릭만 하면 됨)
- DB 파일(`schedule.db`)은 `.gitignore`에 포함되어 GitHub에 올라가지 않음
- 가족 공유: 서비스 URL + 가족 코드만 공유하면 됨
