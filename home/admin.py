from django.contrib import admin
from .models import Doctor, Patient, Appointment, Eye_grounds, Location, Region, Metrics, Message_save_dicom
from import_export.admin import ImportExportActionModelAdmin
from import_export import fields, resources

class AppointmentResource(resources.ModelResource):
    class Meta:
        model = Appointment

class AppointmentAdmin(admin.ModelAdmin):
    resources_class = AppointmentResource
    search_fields = ('patient__first_name', 'patient__surname')
    list_filter = ('doctor',)  # Добавление фильтра по полю "checked"

class EyeResource(resources.ModelResource):
    class Meta:
        model = Eye_grounds


#    list_display = ('date', 'checked')  # Отображаемые поля в списке записей
#    list_filter = ('checked',)  # Добавление фильтра по полю "checked"

# Register your models here.
class EyeAdmin(ImportExportActionModelAdmin):
    resources_class = EyeResource
    list_filter = ('class_ml', 'class_doctor', 'pathology_doctor')
    search_fields = ('id', 'appointment__patient__first_name', 'appointment__patient__surname')

class PatientResource(resources.ModelResource):
    class Meta:
        model = Patient


# Register your models here.
class PatientAdmin(ImportExportActionModelAdmin):
    resources_class = PatientResource
    search_fields = ('first_name', 'surname')
    
        
class Message_save_dicomResource(resources.ModelResource):
    class Meta:
        model = Message_save_dicom

class Message_save_dicomAdmin(ImportExportActionModelAdmin):
    resources_class = Message_save_dicomResource
    search_fields = ('message',)
    list_filter = ('message', )

admin.site.register(Message_save_dicom, Message_save_dicomAdmin)
admin.site.register(Eye_grounds, EyeAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Location)
admin.site.register(Region)
admin.site.register(Doctor)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Metrics)
