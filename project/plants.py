from flask import (Blueprint, flash, get_flashed_messages, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required
from sqlalchemy import not_

from . import db
from .models import (PlantGroup, PlantGroupIntermediary, PlantGroupUsers,
                     PlantSingle, PlantWateringHistory, User)

plants_bp = Blueprint('plants', __name__, url_prefix='/plants')
