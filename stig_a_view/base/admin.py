from django.contrib import admin

from stig_a_view.base import models as base_models

# Register your models here.
admin.site.register(base_models.Product)
admin.site.register(base_models.Control)
admin.site.register(base_models.Stig)
