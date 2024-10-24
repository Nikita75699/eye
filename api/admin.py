from django.contrib import admin
from .models import Doctor_api, Patient_api, Appointment_api, Eye_grounds_api, Location_api, Region_api
from import_export.admin import ImportExportActionModelAdmin
from import_export import fields, resources


class EyeResource(resources.ModelResource):
    class Meta:
        model = Eye_grounds_api


# Register your models here.
class EyeAdmin(ImportExportActionModelAdmin):
    resources_class = EyeResource
    list_filter = ('class_ml', 'class_doctor', 'pathology_doctor')


class PatientResource(resources.ModelResource):
    class Meta:
        model = Patient_api

admin.site.register(Eye_grounds_api, EyeAdmin)
admin.site.register(Appointment_api)
admin.site.register(Location_api)
admin.site.register(Region_api)
admin.site.register(Doctor_api)
admin.site.register(Patient_api)


