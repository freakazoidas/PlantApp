import datetime

from flask import (Blueprint, flash, get_flashed_messages, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required
from sqlalchemy import not_

from . import db
from .models import (PlantGroup, PlantGroupIntermediary, PlantGroupUsers,
                     PlantSingle, PlantWateringHistory, User)

plants_bp = Blueprint('plants', __name__, url_prefix='/plants')

@plants_bp.route('/plant_groups', methods=['GET', 'POST'])
@login_required
def plant_groups():
    if request.method == 'POST':
        # Create a new plant group and assign it to the logged in user
        new_group = PlantGroup(name=request.form.get('group_name'))
        db.session.add(new_group)
        new_group_user = PlantGroupUsers(user=current_user, plant_group=new_group)
        db.session.add(new_group_user)
        db.session.commit()
        flash('New plant group created!', 'success')

    # Get all plant groups assigned to the logged in user
    plant_groups = PlantGroup.query.join(PlantGroupUsers).filter(PlantGroupUsers.user_id == current_user.id).all()

    # Get all plant names assigned to each plant group
    plant_names = {}
    for group in plant_groups:
        plants = PlantGroupIntermediary.query.join(PlantSingle).filter(PlantGroupIntermediary.plant_group_id == group.id).all()
        plant_names[group.name] = [plant.plant.name for plant in plants]

    return render_template('plant_groups.html', plant_groups=plant_groups, plant_names=plant_names)

@plants_bp.route('/delete_group/<int:group_id>', methods=['POST'])
@login_required
def delete_group(group_id):
    # Find the plant group to delete
    group = PlantGroup.query.filter_by(id=group_id).first()

    # Make sure the group belongs to the current user
    if group and PlantGroupUsers.query.filter_by(user_id=current_user.id, plant_group_id=group.id).first():
        # Delete the group and any associated data
        PlantGroupIntermediary.query.filter_by(plant_group_id=group.id).delete()
        PlantGroupUsers.query.filter_by(plant_group_id=group.id).delete()
        PlantGroup.query.filter_by(id=group.id).delete()
        db.session.commit()
        flash('Plant group deleted!', 'success')

    return redirect(url_for('plants.plant_groups'))




@plants_bp.route('/plant_groups/<int:group_id>')
@login_required
def plant_group_single(group_id):
    # Get the plant group
    group = PlantGroup.query.filter_by(id=group_id).first()

    # Get all plants in the group
    plants = PlantGroupIntermediary.query.join(PlantSingle).filter(PlantGroupIntermediary.plant_group_id == group_id).all()

    return render_template('plant_group_single.html', group=group, plants=plants)

def get_days_until_next_watering(last_watered_date, watering_frequency):
    """
    Calculates the number of days until the next watering based on the last watering date and watering frequency.
    """
    today = datetime.datetime.now().date()
    next_watering_date = last_watered_date + datetime.timedelta(days=watering_frequency)
    days_until_next_watering = (next_watering_date - today).days
    return days_until_next_watering

@plants_bp.route('/create_plant', methods=['GET', 'POST'])
@login_required
def create_plant():
    if request.method == 'POST':
        # Create a new plant and add it to the selected plant group
        name = request.form.get('plant_name')
        type = request.form.get('plant_type')
        watering_frequency = request.form.get('watering_frequency')
        replanting_frequency = request.form.get('replanting_frequency')
        fertilizations_frequency = request.form.get('fertilization_frequency')
        group_id = request.form.get('group_id')

        new_plant = PlantSingle(
            name=name,
            type=type,
            watering_frequency=watering_frequency,
            replanting_frequency=replanting_frequency,
            fertilizations_frequency=fertilizations_frequency,
        )
        db.session.add(new_plant)

        # Add the new plant to the selected plant group
        plant_group = PlantGroup.query.get(group_id)
        new_intermediary = PlantGroupIntermediary(
            plant_group=plant_group,
            plant=new_plant,
        )
        db.session.add(new_intermediary)

        db.session.commit()
        flash('New plant created!', 'success')
        return redirect(url_for('plants.plant_groups'))

    # Get all plant groups assigned to the logged in user
    plant_groups = PlantGroup.query.join(PlantGroupUsers).filter(
        PlantGroupUsers.user_id == current_user.id
    ).all()

    return render_template('plant_create.html', plant_groups=plant_groups)

@plants_bp.route('/update_plant', methods=['POST'])
@login_required
def update_plant():
    """
    Updates the watering history of a plant and adds a new entry to PlantWateringHistory.
    """
    plant_id = request.form.get('plant_id')
    comment = request.form.get('comment')
    watering_date = datetime.datetime.strptime(request.form.get('watering_date'), '%Y-%m-%d').date()

    # Find the plant and make sure it belongs to the current user
    plant = PlantSingle.query.filter_by(id=plant_id).first()
    if plant and plant.groups.filter_by(user_id=current_user.id).first():
        # Update the plant's last watering date and add a new entry to PlantWateringHistory
        plant.last_watered = watering_date
        db.session.add(PlantWateringHistory(plant=plant, date=watering_date, comment=comment))
        db.session.commit()
        flash('Plant watering history updated!', 'success')

    return redirect(url_for('plants.plant_group_single', group_id=plant.group.id))