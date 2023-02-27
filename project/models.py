from flask_login import UserMixin
from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from . import db


class User(UserMixin, db.Model):
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    password = Column(String(100))
    name = Column(String(1000))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class BillGroups(db.Model):
    __tablename__ = 'bill_groups'
    id = Column(Integer, primary_key=True)
    group_name = Column(String(255), unique=True)
    bill_intermediaries = relationship("BillGroupIntermediary", back_populates="bill_groups")

class BillGroupIntermediary(db.Model):
    __tablename__ = 'group_user_intermediary'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    group_id = Column(Integer, ForeignKey('bill_groups.id'))
    user = relationship("User")
    bill_groups = relationship("BillGroups", back_populates="bill_intermediaries")

class IndividualBill(db.Model):
    __tablename__ = 'individual_bill'
    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey('bill_groups.id'))
    bill_item = Column(String(255))
    item_price = Column(Numeric(100, 2))

class Projects(db.Model):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    project_name = Column(String(255), nullable=False)
    project_description = Column(String(1000), nullable=False)
    project_picture = Column(String(1000), nullable=True)
    departments = relationship("ProjectsDepartmentsIntermediary", back_populates="project", cascade="all, delete-orphan")

class Departments(db.Model):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    department_name = Column(String(255), nullable=False)
    projects = relationship("ProjectsDepartmentsIntermediary", back_populates="department", cascade="all, delete-orphan")

class ProjectsDepartmentsIntermediary(db.Model):
    __tablename__ = 'projects_departments_intermediary'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    project = relationship("Projects", back_populates="departments")
    department = relationship("Departments", back_populates="projects")
