from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()


class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), unique=True, nullable=False)
    name = db.Column(db.String(50), default='우리 가족')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    children = db.relationship('Child', backref='family', lazy=True, cascade='all, delete-orphan')
    semesters = db.relationship('Semester', backref='family', lazy=True, cascade='all, delete-orphan')
    members = db.relationship('FamilyMember', backref='family', lazy=True, cascade='all, delete-orphan')


class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    school_name = db.Column(db.String(50), default='')
    color = db.Column(db.String(7), default='#4A90D9')
    sort_order = db.Column(db.Integer, default=0)
    schedules = db.relationship('Schedule', backref='child', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'grade': self.grade,
            'school_name': self.school_name,
            'color': self.color,
            'sort_order': self.sort_order,
        }


class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'is_active': self.is_active,
        }


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), nullable=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=월 ~ 4=금
    start_time = db.Column(db.String(5), nullable=False)  # HH:MM
    end_time = db.Column(db.String(5), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(20), nullable=False)  # school, aftercare, after_school, academy
    location = db.Column(db.String(50), default='')
    memo = db.Column(db.String(200), default='')
    pickup_person = db.Column(db.String(20), default='')
    is_active = db.Column(db.Boolean, default=True)

    CATEGORY_LABELS = {
        'school': '정규수업',
        'aftercare': '돌봄교실',
        'after_school': '방과후',
        'academy': '학원',
    }

    def to_dict(self):
        return {
            'id': self.id,
            'child_id': self.child_id,
            'semester_id': self.semester_id,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'title': self.title,
            'category': self.category,
            'category_label': self.CATEGORY_LABELS.get(self.category, self.category),
            'location': self.location,
            'memo': self.memo,
            'pickup_person': self.pickup_person,
            'is_active': self.is_active,
        }


class SpecialEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), default='')
    start_time = db.Column(db.String(5), default='')
    end_time = db.Column(db.String(5), default='')
    cancel_normal = db.Column(db.Boolean, default=False)  # 정규 일정 취소 여부

    def to_dict(self):
        return {
            'id': self.id,
            'child_id': self.child_id,
            'child_name': self.child.name if self.child else '',
            'date': self.date.isoformat(),
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'cancel_normal': self.cancel_normal,
        }


class FamilyMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    role = db.Column(db.String(20), default='')  # 아빠, 엄마, 할머니 등
    color = db.Column(db.String(7), default='#9C27B0')
    sort_order = db.Column(db.Integer, default=0)
    events = db.relationship('MemberEvent', backref='member', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'color': self.color,
            'sort_order': self.sort_order,
        }


class MemberEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('family_member.id'), nullable=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=True)
    date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), default='')
    start_time = db.Column(db.String(5), default='')
    end_time = db.Column(db.String(5), default='')
    cancel_normal = db.Column(db.Boolean, default=False)

    child = db.relationship('Child', backref='member_events')

    def to_dict(self):
        if self.child_id:
            person_name = self.child.name if self.child else ''
            person_color = self.child.color if self.child else '#999'
        else:
            person_name = self.member.name if self.member else ''
            person_color = self.member.color if self.member else '#999'
        return {
            'id': self.id,
            'member_id': self.member_id,
            'child_id': self.child_id,
            'person_name': person_name,
            'person_color': person_color,
            'type': 'child' if self.child_id else 'member',
            'date': self.date.isoformat(),
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time or '',
            'end_time': self.end_time or '',
            'cancel_normal': self.cancel_normal or False,
        }
