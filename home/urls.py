from django.urls import path, include, reverse_lazy
from.import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.authorization),
    path('authorization', views.authorization, name='authorization'),
    path('index', views.index, name='home'),
    path('relogin', views.relogin),
    path('appointment_search', views.appointment_search),
    path('task', views.task),
    path('back', views.back, name='back'),
    path('get_appointment<uuid:patient>/', views.get_appointment, name='get_appointment'),
    path('get_check_appointment<uuid:id_appointment>/', views.get_check_appointment, name='get_check_appointment'),
    path('report', views.save_report),
    # path('modal_pacient<uuid:id_appointment>', views.modal_pacient),
    path('get_appointment<uuid:patient>/old_appointment', views.old_appointment),
    path('progress_bar', views.progress_bar),
    path('del_check<int:id_patient>/', views.delete_check, name='del_check'),
    path('filter_chart', views.filter_chart, name='filter_chart'),
    path('delegate<uuid:id_patient>/', views.delegate, name='delegate'),
    path('download_excel/', views.download_excel, name='download_excel'),
    path('api_dicom', views.api_dicom, name='api_dicom'),
    path('json_data_appoints<int:id_patient>', views.json_data_appoints),
    path('patients/json/', views.employee_json, name='patient_list_json'),
    path('migrate', views.migrate_data),
    path('patients/', views.patient_list, name='patient_list'),
    path('get_image/', views.get_image, name='get_image'),
    path('app_check/', views.app_check, name='app_check'),
]
