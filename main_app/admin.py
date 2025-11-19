from django.contrib import admin

# This app currently defines Pydantic models in `main_app.models` for schema/transport
# purposes (BaseModel classes). Django's admin only accepts Django ORM model classes
# (subclasses of django.db.models.Model). Attempting to register Pydantic models
# (or other non-ORM types) raises the TypeError seen in the traceback.
#
# If you want to manage ORM models in the admin, define them as subclasses of
# `django.db.models.Model` in `main_app/models.py` and import/register them here,
# for example:
#
# from .models import MyDjangoModel
# admin.site.register(MyDjangoModel)
#
# For now, keep admin registrations empty to avoid startup errors.

# No registrations at the moment.