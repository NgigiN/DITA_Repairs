from typing import Optional
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, ForeignKey
import sqlalchemy.orm as so
from sqlalchemy.orm import relationship
from app import db, login
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from enum import Enum


@login.user_loader
def load_user(admission_number):
    return User.query.get(admission_number)


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    admission_number: so.Mapped[str] = so.mapped_column(sa.String(64))
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    is_admin: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    repairs: so.WriteOnlyMapped['Repair'] = so.relationship(
        back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {} {}>'.format(self.admission_number, self.username)


class RepairStatus(Enum):
    REQUEST_MADE = 'Request Made'
    ONGOING = 'Ongoing'
    DONE = 'Done'


class AdminComment(db.Model):
    __tablename__ = 'admin_comment'

    id = Column(Integer, primary_key=True)
    comment = Column(String(300))
    repair_id = Column(Integer, ForeignKey('repair.id'))

    repair = relationship('Repair', back_populates='admin_comments')


class Repair(db.Model):
    __tablename__ = 'repair'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    laptop_brand: so.Mapped[str] = so.mapped_column(sa.String(64))
    serial_number: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)
    admission_number: so.Mapped[str] = so.mapped_column(sa.String(64))
    description: so.Mapped[str] = so.mapped_column(sa.String(300))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    submission_date: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, default=datetime.now(timezone.utc))
    user: so.Mapped[User] = so.relationship(back_populates='repairs')
    status = db.Column(db.Enum(RepairStatus),
                       default=RepairStatus.REQUEST_MADE)
    admin_comments = relationship('AdminComment', back_populates='repair')
    charge: so.Mapped[float] = so.mapped_column(sa.Float, nullable=True)
    transaction_code: so.Mapped[str] = so.mapped_column(sa.String(100))

    def __repr__(self):
        return '<Repair for {} whose machine is a {} serial no {} submitted on {}>'.format(self.admission_number, self.laptop_brand, self.serial_number, self.submission_date)
