from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import db
from .models import Departments, Projects

departments_bp = Blueprint('departments', __name__, url_prefix='/departments')

@departments_bp.route('/departments', methods=['GET', 'POST'])
@login_required
def list_departments():
    departments = Departments.query.all()

    if request.method == 'POST':
        department_name = request.form['department_name']
        new_department = Departments(department_name=department_name)
        db.session.add(new_department)
        db.session.commit()

    return render_template('departments.html', departments=departments)

@departments_bp.route('/departments/<int:department_id>', methods=['GET', 'POST'])
@login_required
def department(department_id):
    department = Departments.query.filter_by(id=department_id).first()
    projects = Projects.query.filter_by(department_id=department_id).all()

    if request.method == 'POST':
        department_name = request.form['department_name']
        department.department_name = department_name
        db.session.commit()
        return redirect(url_for('departments.department', department_id=department_id))

    return render_template('department.html', department=department, projects=projects)

@departments_bp.route('/projects/<int:project_id>', methods=['GET', 'POST'])
@login_required
def project(project_id):
    project = Projects.query.filter_by(id=project_id).first()

    if request.method == 'POST':
        project_name = request.form['project_name']
        project_description = request.form['project_description']
        department_id = request.form['department_id']

        project.project_name = project_name
        project.project_description = project_description
        project.department_id = department_id

        if 'project_picture' in request.files:
            project_picture = request.files['project_picture']
            if project_picture.filename != '':
                project_picture.save('static/images/' + project_picture.filename)
                project.project_picture = project_picture.filename

        db.session.commit()
        return redirect(url_for('departments.project', project_id=project_id))

    return render_template('project.html', project=project, departments=Departments.query.all())

@departments_bp.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    projects = Projects.query.all()

    if request.method == 'POST':
        project_name = request.form['project_name']
        project_description = request.form['project_description']
        department_id = request.form['department_id']
        project_picture = None

        if 'project_picture' in request.files:
            project_picture = request.files['project_picture']
            if project_picture.filename != '':
                project_picture.save('static/images/' + project_picture.filename)

        new_project = Projects(
            project_name=project_name,
            project_description=project_description,
            project_picture=project_picture.filename if project_picture else None,
            department_id=department_id
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('departments.projects'))

    return render_template('projects.html', projects=projects, departments=Departments.query.all())
