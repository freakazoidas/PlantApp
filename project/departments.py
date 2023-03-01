from flask import (Blueprint, flash, get_flashed_messages, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required

from . import db
from .models import Departments, Projects, ProjectsDepartmentsIntermediary

departments_bp = Blueprint('departments', __name__, url_prefix='/departments')

@departments_bp.route('/', methods=['GET', 'POST'])
@login_required
def list_departments():
    departments = Departments.query.all()

    if request.method == 'POST':
        department_name = request.form['department_name']
        # Check if department with same name already exists
        existing_department = Departments.query.filter_by(department_name=department_name).first()
        if existing_department:
            flash('Department already exists')
        else:
            new_department = Departments(department_name=department_name)
            db.session.add(new_department)
            db.session.commit()
            flash('Department created successfully')
        return redirect(url_for('departments.list_departments'))

    return render_template('departments.html', departments=departments)

@departments_bp.route('/<int:department_id>/delete', methods=['POST'])
@login_required
def delete_department(department_id):
    department = Departments.query.filter_by(id=department_id).first()
    if not department:
        flash('Department not found')
    else:
        db.session.delete(department)
        db.session.commit()
        flash('Department deleted successfully')
    return redirect(url_for('departments.list_departments', departments=Departments.query.all()))


@departments_bp.route('/<int:department_id>', methods=['GET', 'POST'])
@login_required
def department(department_id):
    department = Departments.query.filter_by(id=department_id).first()
    if not department:
        flash('Department not found')
        return redirect(url_for('departments.list_departments'))
    projects = db.session.query(Projects).join(ProjectsDepartmentsIntermediary).filter_by(department_id=department_id)

    if request.method == 'POST':
        department_name = request.form['department_name']
        existing_department = Departments.query.filter_by(department_name=department_name).first()
        if existing_department:
            flash('Department already exists')
        else:
            # Retrieve the updated department name from the hidden span element
            department_name = request.form.get('department_name_hidden')
            department.department_name = department_name
            db.session.commit()
            flash('Department updated successfully')
        return redirect(url_for('departments.department', department_id=department_id))

    return render_template('department.html', department=department, projects=projects)


@departments_bp.route('/<int:department_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_department(department_id):
    department = Departments.query.filter_by(id=department_id).first()
    if not department:
        flash('Department not found')
        return redirect(url_for('departments.list_departments'))

    if request.method == 'POST':
        department_name = request.form['department_name']
        existing_department = Departments.query.filter_by(department_name=department_name).first()
        if existing_department:
            flash('Department already exists')
        else:
            department.department_name = department_name
            db.session.commit()
            flash('Department updated successfully')
        return redirect(url_for('departments.list_departments'))

    return render_template('edit_department.html', department=department)


@departments_bp.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    projects = Projects.query.all()

    if request.method == 'POST':
        project_name = request.form['project_name']
        project_description = request.form['project_description']
        department_ids = request.form.getlist('department_ids')
        project_picture = None

        if 'project_picture' in request.files:
            project_picture = request.files['project_picture']
            if project_picture.filename != '':
                project_picture.save('static/images/' + project_picture.filename)

        new_project = Projects(
            project_name=project_name,
            project_description=project_description,
            project_picture=project_picture.filename if project_picture else None
        )
        for department_id in department_ids:
            department = Departments.query.filter_by(id=department_id).first()
            intermediary = ProjectsDepartmentsIntermediary(project=new_project, department=department)
            new_project.departments.append(intermediary)

        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('departments.projects'))

    return render_template('projects.html', projects=projects, departments=Departments.query.all())

@departments_bp.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Projects.query.filter_by(id=project_id).first()
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully')
    return redirect(url_for('departments.projects'))


