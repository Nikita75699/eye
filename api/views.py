from django.shortcuts import render
from .models import *
from home.models import *
from django.http import JsonResponse

def migrate_data(request):
    for reg in Region.objects.all():

        if not Region_api.objects.filter(region=reg.region).exists():
          reg_api = Region_api(
              number_id=reg.number_id,
              region=reg.region,
          )
          reg_api.save()
    for log in Location.objects.all():
        reg = Region_api.objects.get(region=log.region)
        if not Location_api.objects.filter(number_id=log.number_id).exists():
          log_api = Location_api(
                number_id = log.number_id,
                location = log.location,
                region = reg,
          )
          log_api.save()
        # Перенос данных из Doctor в Doctor_api
    for doctor in Doctor.objects.all():
        reg = Region_api.objects.get(number_id=doctor.region.number_id)
        if not Doctor_api.objects.filter(user=doctor.user, post=doctor.post).exists():
            doctor_api = Doctor_api(
                user=doctor.user,
                first_name=doctor.first_name,
                surname=doctor.surname,
                patronymic=doctor.patronymic,
                post=doctor.post,
                region=reg
            )
            doctor_api.save()
        else:
            doctor_api = Doctor_api.objects.get(user=doctor.user, post=doctor.post)

    patients = Patient.objects.all()
    for patient in patients:
      if patient.doctor_set.exists():  # Проверяем, есть ли врачи
          patient_doctor = patient.doctor_set.first()
          patient_doctor_api = Doctor_api.objects.get(user=patient_doctor.user)
      else:
          patient_doctor = None
      print(patient_doctor)
      if patient.locations is not None:
        loc = Location_api.objects.get(number_id=patient.locations.number_id)
        if not Patient_api.objects.filter(first_name=patient.first_name,
                                          surname=patient.surname,
                                          patronymic=patient.patronymic,
                                          date_of_birth=patient.date_of_birth).exists():
            patient_api = Patient_api(
                doctor=patient_doctor_api,
                first_name=patient.first_name,
                surname=patient.surname,
                patronymic=patient.patronymic,
                sex=patient.sex,
                pathology=patient.pathology,
                date_of_birth=patient.date_of_birth,
                appointment_last=patient.appointment_last,
                locations=loc,
                checked=patient.checked,
                fixing_doctor=patient.fixing_doctor,
                type_pacient=patient.type_pacient
            )
            patient_api.save()
            pat_api = patient_api
        else:
          pat_api = Patient_api.objects.get(first_name=patient.first_name,
                                            surname=patient.surname,
                                            patronymic=patient.patronymic)
      else:
          print(patient)

      apointments = patient.appointments.all()
      for apointment in apointments:

        if not Appointment_api.objects.filter(patient=pat_api, date=apointment.date).exists():
            apointment_api = Appointment_api(
              patient = pat_api,
              date = apointment.date,
              score = apointment.score,
              report = apointment.report,
              pathology = apointment.pathology,
              checked = apointment.checked,
            )
            apointment_api.save()
        else:
          apointment_api = Appointment_api.objects.get(patient=pat_api, date = apointment.date)

        eyes = apointment.data.all()
        for eye in eyes:
            pathology_doctor_value = eye.pathology_doctor if isinstance(eye.pathology_doctor,
                                                                        (int, float)) else None

            if not Eye_grounds_api.objects.filter(img_path=eye.img_path).exists():
                eye_api = Eye_grounds_api(
                    appointment=apointment_api,
                    img_path=eye.img_path,
                    mask_path=eye.mask_path,
                    class_ml=eye.class_ml,
                    score=eye.score,
                    pathology_ml=eye.pathology_ml,
                    pathology_doctor=pathology_doctor_value,  # Используем проверенное значение
                )
                eye_api.save()

    return JsonResponse({'status': 'Data migration completed'})


