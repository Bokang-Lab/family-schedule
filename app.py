import os
import secrets
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from models import db, Family, Child, Semester, Schedule, SpecialEvent

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///schedule.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

DAY_NAMES = ['월', '화', '수', '목', '금']
DAY_NAMES_FULL = ['일', '월', '화', '수', '목', '금', '토']  # 한국 달력 (일~토)


def get_family():
    """세션에서 현재 가족 정보 가져오기"""
    family_id = session.get('family_id')
    if not family_id:
        return None
    return db.session.get(Family, family_id)


def login_required(f):
    """로그인 필수 데코레이터"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('family_id'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ─── 페이지 라우트 ───

@app.route('/')
@login_required
def index():
    """오늘 보기"""
    family = get_family()
    children = Child.query.filter_by(family_id=family.id).order_by(Child.sort_order).all()
    today_dow = datetime.now().weekday()  # 0=월
    today_date = date.today()

    children_schedules = []
    for child in children:
        schedules = Schedule.query.filter_by(
            child_id=child.id, day_of_week=today_dow, is_active=True
        ).order_by(Schedule.start_time).all()

        special = SpecialEvent.query.filter_by(
            child_id=child.id, date=today_date
        ).all()

        children_schedules.append({
            'child': child,
            'schedules': [s.to_dict() for s in schedules],
            'special_events': [e.to_dict() for e in special],
        })

    return render_template('today.html',
                           family=family,
                           children_schedules=children_schedules,
                           today_dow=today_dow,
                           day_name=DAY_NAMES[today_dow] if today_dow < 5 else '주말',
                           today_str=today_date.strftime('%Y년 %m월 %d일'),
                           now_time=datetime.now().strftime('%H:%M'))


@app.route('/weekly')
@login_required
def weekly():
    """주간 시간표"""
    family = get_family()
    children = Child.query.filter_by(family_id=family.id).order_by(Child.sort_order).all()

    selected_child_id = request.args.get('child_id', type=int)
    if not selected_child_id and children:
        selected_child_id = children[0].id

    # 주간 날짜 계산 (일요일 시작)
    week_offset = request.args.get('week', 0, type=int)  # 0=이번주, -1=지난주, 1=다음주
    today = date.today()
    # Python weekday: 월=0 ~ 일=6 → 일요일 찾기
    days_since_sunday = (today.weekday() + 1) % 7
    week_sunday = today - timedelta(days=days_since_sunday) + timedelta(weeks=week_offset)
    week_dates = [week_sunday + timedelta(days=i) for i in range(7)]  # 일~토

    # 요일 헤더 데이터 (일~토, 각 날짜 포함)
    week_header = []
    for i, d in enumerate(week_dates):
        week_header.append({
            'name': DAY_NAMES_FULL[i],
            'date': d,
            'date_str': f'{d.month}/{d.day}',
            'is_today': d == today,
        })

    # 일~토 → Python weekday 매핑: 일=6, 월=0, 화=1, 수=2, 목=3, 금=4, 토=5
    korean_to_python_dow = [6, 0, 1, 2, 3, 4, 5]

    weekly_data = {}
    special_events_data = {}
    if selected_child_id:
        for i in range(7):  # 일~토 (i=0~6)
            python_dow = korean_to_python_dow[i]
            schedules = Schedule.query.filter_by(
                child_id=selected_child_id, day_of_week=python_dow, is_active=True
            ).order_by(Schedule.start_time).all()
            weekly_data[i] = [s.to_dict() for s in schedules]

            # 해당 날짜의 특별 일정
            specials = SpecialEvent.query.filter_by(
                child_id=selected_child_id, date=week_dates[i]
            ).all()
            special_events_data[i] = [e.to_dict() for e in specials]

    # 주간 제목
    week_title = f'{week_dates[0].month}월 {week_dates[0].day}일 ~ {week_dates[6].month}월 {week_dates[6].day}일'

    return render_template('weekly.html',
                           family=family,
                           children=children,
                           selected_child_id=selected_child_id,
                           weekly_data=weekly_data,
                           special_events_data=special_events_data,
                           week_header=week_header,
                           week_offset=week_offset,
                           week_title=week_title)


@app.route('/manage')
@login_required
def manage():
    """일정 관리"""
    family = get_family()
    children = Child.query.filter_by(family_id=family.id).order_by(Child.sort_order).all()
    semesters = Semester.query.filter_by(family_id=family.id).order_by(Semester.start_date.desc()).all()

    selected_child_id = request.args.get('child_id', type=int)
    if not selected_child_id and children:
        selected_child_id = children[0].id

    schedules = []
    special_events = []
    if selected_child_id:
        schedules = Schedule.query.filter_by(
            child_id=selected_child_id, is_active=True
        ).order_by(Schedule.day_of_week, Schedule.start_time).all()
        special_events = SpecialEvent.query.filter_by(
            child_id=selected_child_id
        ).filter(SpecialEvent.date >= date.today()).order_by(SpecialEvent.date).all()

    return render_template('manage.html',
                           family=family,
                           children=children,
                           semesters=semesters,
                           selected_child_id=selected_child_id,
                           schedules=[s.to_dict() for s in schedules],
                           special_events=[e.to_dict() for e in special_events],
                           day_names=DAY_NAMES)


@app.route('/settings')
@login_required
def settings():
    """설정"""
    family = get_family()
    children = Child.query.filter_by(family_id=family.id).order_by(Child.sort_order).all()
    semesters = Semester.query.filter_by(family_id=family.id).order_by(Semester.start_date.desc()).all()
    return render_template('settings.html',
                           family=family,
                           children=children,
                           semesters=semesters)


@app.route('/login')
def login():
    if session.get('family_id'):
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ─── API 라우트 ───

@app.route('/api/family/create', methods=['POST'])
def api_create_family():
    """가족 생성"""
    data = request.get_json()
    code = secrets.token_hex(3).upper()[:6]
    family = Family(code=code, name=data.get('name', '우리 가족'))
    db.session.add(family)
    db.session.commit()
    session['family_id'] = family.id
    return jsonify({'success': True, 'code': code, 'family_id': family.id})


@app.route('/api/family/join', methods=['POST'])
def api_join_family():
    """가족 코드로 참여"""
    data = request.get_json()
    code = data.get('code', '').strip().upper()
    family = Family.query.filter_by(code=code).first()
    if not family:
        return jsonify({'success': False, 'error': '가족 코드를 찾을 수 없습니다.'}), 404
    session['family_id'] = family.id
    return jsonify({'success': True, 'family_name': family.name})


@app.route('/api/family', methods=['PUT'])
@login_required
def api_update_family():
    """가족 이름 수정"""
    family = get_family()
    data = request.get_json()
    family.name = data.get('name', family.name)
    db.session.commit()
    return jsonify({'success': True})


# ─── 자녀 API ───

@app.route('/api/child', methods=['POST'])
@login_required
def api_add_child():
    family = get_family()
    data = request.get_json()
    child = Child(
        family_id=family.id,
        name=data['name'],
        grade=data['grade'],
        school_name=data.get('school_name', ''),
        color=data.get('color', '#4A90D9'),
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(child)
    db.session.commit()
    return jsonify({'success': True, 'child': child.to_dict()})


@app.route('/api/child/<int:child_id>', methods=['PUT'])
@login_required
def api_update_child(child_id):
    child = Child.query.get_or_404(child_id)
    data = request.get_json()
    child.name = data.get('name', child.name)
    child.grade = data.get('grade', child.grade)
    child.school_name = data.get('school_name', child.school_name)
    child.color = data.get('color', child.color)
    child.sort_order = data.get('sort_order', child.sort_order)
    db.session.commit()
    return jsonify({'success': True, 'child': child.to_dict()})


@app.route('/api/child/<int:child_id>', methods=['DELETE'])
@login_required
def api_delete_child(child_id):
    child = Child.query.get_or_404(child_id)
    db.session.delete(child)
    db.session.commit()
    return jsonify({'success': True})


# ─── 스케줄 API ───

@app.route('/api/schedule', methods=['POST'])
@login_required
def api_add_schedule():
    data = request.get_json()
    schedule = Schedule(
        child_id=data['child_id'],
        semester_id=data.get('semester_id'),
        day_of_week=data['day_of_week'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        title=data['title'],
        category=data['category'],
        location=data.get('location', ''),
        memo=data.get('memo', ''),
        pickup_person=data.get('pickup_person', ''),
    )
    db.session.add(schedule)
    db.session.commit()
    return jsonify({'success': True, 'schedule': schedule.to_dict()})


@app.route('/api/schedule/<int:schedule_id>', methods=['PUT'])
@login_required
def api_update_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    data = request.get_json()
    for field in ['day_of_week', 'start_time', 'end_time', 'title', 'category',
                  'location', 'memo', 'pickup_person', 'semester_id', 'is_active']:
        if field in data:
            setattr(schedule, field, data[field])
    db.session.commit()
    return jsonify({'success': True, 'schedule': schedule.to_dict()})


@app.route('/api/schedule/<int:schedule_id>', methods=['DELETE'])
@login_required
def api_delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    return jsonify({'success': True})


# ─── 특별일정 API ───

@app.route('/api/special-event', methods=['POST'])
@login_required
def api_add_special_event():
    data = request.get_json()
    event = SpecialEvent(
        child_id=data['child_id'],
        date=date.fromisoformat(data['date']),
        title=data['title'],
        description=data.get('description', ''),
        start_time=data.get('start_time', ''),
        end_time=data.get('end_time', ''),
        cancel_normal=data.get('cancel_normal', False),
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({'success': True, 'event': event.to_dict()})


@app.route('/api/special-event/<int:event_id>', methods=['PUT'])
@login_required
def api_update_special_event(event_id):
    event = SpecialEvent.query.get_or_404(event_id)
    data = request.get_json()
    for field in ['title', 'description', 'start_time', 'end_time', 'cancel_normal']:
        if field in data:
            setattr(event, field, data[field])
    if 'date' in data:
        event.date = date.fromisoformat(data['date'])
    db.session.commit()
    return jsonify({'success': True, 'event': event.to_dict()})


@app.route('/api/special-event/<int:event_id>', methods=['DELETE'])
@login_required
def api_delete_special_event(event_id):
    event = SpecialEvent.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({'success': True})


# ─── 학기 API ───

@app.route('/api/semester', methods=['POST'])
@login_required
def api_add_semester():
    family = get_family()
    data = request.get_json()
    semester = Semester(
        family_id=family.id,
        name=data['name'],
        start_date=date.fromisoformat(data['start_date']),
        end_date=date.fromisoformat(data['end_date']),
        is_active=data.get('is_active', True),
    )
    db.session.add(semester)
    db.session.commit()
    return jsonify({'success': True, 'semester': semester.to_dict()})


@app.route('/api/semester/<int:semester_id>', methods=['PUT'])
@login_required
def api_update_semester(semester_id):
    semester = Semester.query.get_or_404(semester_id)
    data = request.get_json()
    semester.name = data.get('name', semester.name)
    if 'start_date' in data:
        semester.start_date = date.fromisoformat(data['start_date'])
    if 'end_date' in data:
        semester.end_date = date.fromisoformat(data['end_date'])
    semester.is_active = data.get('is_active', semester.is_active)
    db.session.commit()
    return jsonify({'success': True, 'semester': semester.to_dict()})


@app.route('/api/semester/<int:semester_id>', methods=['DELETE'])
@login_required
def api_delete_semester(semester_id):
    semester = Semester.query.get_or_404(semester_id)
    db.session.delete(semester)
    db.session.commit()
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
