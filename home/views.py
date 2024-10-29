from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.template.loader import render_to_string
import json
import urllib.request
from .models import Doctor, Patient, Appointment, Eye_grounds, Location, Metrics, Message_save_dicom, Region
from django.db.models import Q
import random
import os
import io
import cv2
import uuid
import scipy
import base64
import pydicom
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt
import queue
import threading
import logging
import concurrent.futures
from ultralytics import YOLO
from api.models import *
from django.core.paginator import Paginator
from django.shortcuts import render
from home import inference_pb
   

#model quality image
model_clas = YOLO('inference_model/best.pt')
#model classification image DR
model = YOLO('inference_model/best_DR_class.pt')

classes_list = [[1, 'Norma'], [2, 'PDR'], [3, 'PrePDR'], [4, 'NPDR'], [5, 'OTHER'], [6, 'НС']]
prog_bar_val = None

def get_personal_area(
        request,
        doctor,
        patients
):
    doctor_region = doctor.region
    # doctor_patients = patients.filter(doctor=doctor)

    if doctor.post == 2:
        patient_with = Patient.objects.filter(Q(locations__region=doctor_region) & Q(type_pacient=1))
        patient_without = Patient.objects.filter(Q(locations__region=doctor_region) & Q(type_pacient=2))

        app_with_d = Appointment.objects.filter(
            Q(patient__locations__region=doctor_region) & Q(patient__type_pacient=1) & Q(fixing_doctor=False))
        app_without_d = Appointment.objects.filter(
            Q(patient__locations__region=doctor_region) & Q(patient__type_pacient=2) & Q(fixing_doctor=False))

        doctors = Doctor.objects.filter(region=doctor_region)
        patient = Patient.objects.filter(Q(locations__region=doctor_region))
        inform_list = list(np.zeros(19))

        # 1. Sex
        inform_list[0] = len(patients.filter(sex=1))
        inform_list[1] = len(patients.filter(sex=2))

        # 2. Years
        from dateutil.relativedelta import relativedelta
        years = [(0, 18), (18, 30), (30, 45), (45, 70), (70, 120)]
        for idx, year in enumerate(years):
            inform_list[idx + 2] = len(patients.filter(pathology=True, date_of_birth__gt=(datetime.now() - relativedelta(years=year[1])), date_of_birth__lte=(datetime.now() - relativedelta(years=year[0]))))
            inform_list[idx + 14] = len(patients.filter(pathology=False, date_of_birth__gt=(datetime.now() - relativedelta(years=year[1])),
                                date_of_birth__lte=(datetime.now() - relativedelta(years=year[0]))))
        # 3. Locations
        locate = Location.objects.filter(region=doctor_region)
        # for idx, loc in enumerate(locate):
        #     inform_list[7] = dict([loc, len(patients.filter(locations=loc))])

        patients_locate = []
        for idx, loc in enumerate(locate):
            patients_locate.append({
                'key': loc.location,
                'value': len(patients.filter(locations=loc)),
            })
            # patients_locate[loc.location] = len(patients.filter(locations=loc))
        inform_list[7] = patients_locate

        # 4. Patology
        inform_list[10] = len(patients.filter(sex=1, pathology=False))
        inform_list[11] = len(patients.filter(sex=1, pathology=True))
        inform_list[12] = len(patients.filter(sex=2, pathology=False))
        inform_list[13] = len(patients.filter(sex=2, pathology=True))

        return render(
            request,
            'index.html',
            context={
                'doctor': doctor,
                'doctors': doctors if doctors is not None else [],
                'patients': patient if patient is not None else [],
                'doctor_list_patient': patient if patient is not None else [],
                "inform_list_m": inform_list[0],
                "inform_list_f": inform_list[1],
                "inform_list_18_t": inform_list[2],
                "inform_list_30_t": inform_list[3],
                "inform_list_45_t": inform_list[4],
                "inform_list_60_t": inform_list[5],
                "inform_list_70_t": inform_list[6],
                "inform_list_l": inform_list[7],
                "inform_list_p1": inform_list[10],
                "inform_list_p2": inform_list[11],
                "inform_list_p3": inform_list[12],
                "inform_list_p4": inform_list[13],
                "inform_list_18_f": inform_list[14],
                "inform_list_30_f": inform_list[15],
                "inform_list_45_f": inform_list[16],
                "inform_list_60_f": inform_list[17],
                "inform_list_70_f": inform_list[18],
                'patient_with': patient_with,
                'patient_without': patient_without,
                'app_with_d': app_with_d,
                'app_without_d': app_without_d,
            }
        )
    else:
        patients_with_diabetes = Appointment.objects.filter(doctor=doctor, patient__type_pacient=1, checked=False)
        patients_without_diabetes = Appointment.objects.filter(doctor=doctor, patient__type_pacient=2, checked=False)
        export_patients_with_diabetes = Appointment.objects.filter(doctor=doctor, patient__type_pacient=1, export_csv=False)
        export_patients_without_diabetes = Appointment.objects.filter(doctor=doctor, patient__type_pacient=2, export_csv=False)
        return render(
            request,
            'index.html',
            context={
                'doctor': doctor,
                'patients_with_diabetes': patients_with_diabetes,
                'patients_without_diabetes': patients_without_diabetes,
                'doctor_list_patient': Appointment.objects.filter(doctor=doctor),
                'list_patient': Patient.objects.all(),
                'hospitals': Location.objects.all(),
                'export_p_d': export_patients_with_diabetes,
                'export_p_no_d': export_patients_with_diabetes
            }
        )


def filter_chart(request):
    data_to = request.POST.get('data_to')
    data_from = request.POST.get('data_from')
    doctor = Doctor.objects.get(user=request.user)
    patient = Patient.objects.filter(appointment_last__gt=data_from, appointment_last__lt=data_to)
    return get_personal_area(
        request=request,
        doctor=doctor,
        patients=patient)


def authorization(request):
    if request.method == 'POST':
        username = request.POST['login']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is None:
            return render(
                request,
                'authorization.html',
                context={
                    'message': 'error'
                }
            )
        else:
            login(request, user)
            return redirect('home')
    else:
        doctor_info = request.user
        if doctor_info != 'AnonymousUser':
            try:
                doctor_info = Doctor.objects.get(user=doctor_info)
            except:
                pass

        return render(
            request,
            'authorization.html',
            context={
                'doctor_info': doctor_info
            }
        )


def task(request):
    list_patients = request.POST.getlist('patients')
    id_doctor = request.POST.get('doctor')
    doctor = Doctor.objects.filter(id=id_doctor).first()
    list_patients = ",".join(list_patients)
    list_patients = list_patients.split(',')
    for i in list_patients:
        appointment = Appointment.objects.get(id=i)
        appointment.fixing_doctor = True
        appointment.doctor = doctor
        appointment.save()
    return redirect('home')


def relogin(request):
    if 'input' in request.GET.dict():
        return redirect('home')
    else:
        logout(request)
        return redirect('authorization')


def back(request):
    return redirect('home')


def index(request):
    doctor = Doctor.objects.get(user=request.user)
    patient = Patient.objects.filter(Q(locations__region=doctor.region))
    return get_personal_area(
        request=request,
        doctor=doctor,
        patients=patient
    )


def save_report(request):
    post = request.POST.dict()
    appointment = request.POST.get('appointment')
    patient = request.POST.get('patient')
    reports = request.POST['report']
    appointment = Appointment.objects.get(id=appointment)
    pacient = Patient.objects.get(id=patient)
    appointment.checked = True
    for idx, data in enumerate(Eye_grounds.objects.filter(appointment=appointment)):
        key = f'exampleRadios{idx + 1}'
        if key in post:

            data.class_doctor = int(post[f'exampleRadios{idx + 1}'])
            data.pathology_doctor = 1 if int(post[f'exampleRadios{idx + 1}']) != 1 and int(post[f'exampleRadios{idx + 1}']) != 6 else 0
            if data.pathology_doctor == 1:
                appointment.pathology = True
            data.save()
        else:
            print(f'Ключ {key} не найден в post')
    doctor = Doctor.objects.get(user=request.user)
    pacient.pathology = appointment.pathology
    appointment.report = reports
    appointment.save()
    pacient.save()
    return redirect('home')
    # patients_with_diabetes = doctor.patients.filter(type_pacient=1)
    # patients_without_diabetes = doctor.patients.filter(type_pacient=2)
    # return render(
    #     request,
    #     'index.html',
    #     context={
    #         'doctor': doctor,
    #         'patients_with_diabetes': patients_with_diabetes,
    #         'patients_without_diabetes': patients_without_diabetes,
    #     }
    # )


def block_modal_pacient(request):
    return render(request, 'modal_pacient.html')


def get_data_appointment(
        appointment
):
    inform = []

    for count, data in enumerate(Eye_grounds.objects.filter(appointment=appointment)):
        try:
            dicom = pydicom.dcmread(data.img_path, force=True)
            if dicom.PatientBirthDate == '':
                patient_birthdate = None
            else:
                patient_birthdate = dicom.PatientBirthDate
                year = int(patient_birthdate[:4])
                month = int(patient_birthdate[4:6])
                day = int(patient_birthdate[6:])
                # patient_birthdate = datetime.date(year, month, day)
                patient_birthdate = date(year, month, day)
            patient_birthdate = patient_birthdate
            if dicom.StudyDate == '':
                study_date = None
            else:
                study_date = dicom.StudyDate
                year = int(study_date[:4])
                month = int(study_date[4:6])
                day = int(study_date[6:])
                # study_date = datetime.datetime(year, month, day)
                study_date = date(year, month, day)
            study_date = study_date
            pixel_array = dicom.pixel_array
            color_space = dicom.PhotometricInterpretation
            if color_space == 'RGB':
                _, im_arr = cv2.imencode('.png',  cv2.cvtColor(pixel_array, cv2.COLOR_RGB2BGR))
            else:
                _, im_arr = cv2.imencode('.png', cv2.cvtColor(pixel_array, cv2.COLOR_YCR_CB2RGB))
            im_bytes = im_arr.tobytes()
            im_b64 = base64.b64encode(im_bytes)
            im_b64_str = im_b64.decode("utf8")
            format = '%d.%m.%Y'

            inform.append(
                {
                    'count': count + 1,
                    'patient_sex': str(dicom.PatientSex),
                    'patient_name': str(dicom.PatientName),
                    'patient_ID': str(dicom.PatientID),
                        # 'patient_orientation': patient_orientation,
                    'patient_birthdate': str(patient_birthdate),
                    'study_date': str(study_date),
                    'data_id': data.id,
                    'score': data.score * 100,
                    'class_doc': str(data.class_doctor),
                    'pathology_ml': str(data.pathology_ml),
                    'class_ml': str(data.class_ml),
                    'data_mask': '/static/im.png',
                    'mask_path': str(data.mask_path),
                    'image': 'data:image/png;base64,{}'.format(im_b64_str),
                }
            )
        except FileNotFoundError:
            print(f"Файл не найден: {data.img_path}")
            continue

    return inform

def get_appointment(
        request,
        patient,
):
    doctor = Doctor.objects.get(user=request.user)
    patient = Patient.objects.get(id=patient)
    appointment = Appointment.objects.filter(patient=patient).latest('date')
    appointment_old = Appointment.objects.filter(patient=patient).order_by('-date')[1:]

    inform = []

    if appointment is not None:
        inform = get_data_appointment(appointment)

    return render(
        request,
        'appointment.html',
        context={
            'doctor': doctor,
            'patient': patient,
            'appointment': appointment,
            'inform': inform,
            'appointments': Appointment.objects.filter(patient=patient) if Appointment.objects.filter(patient=patient) is not None else [],
            'classes_list': classes_list,
            "appointment_old": appointment_old,
        }
    )


def get_check_appointment(
        request,
        id_appointment,
):
    doctor = Doctor.objects.get(user=request.user)
    appointment = Appointment.objects.get(id=id_appointment)
    patient = appointment.patient
    appointment_old = Appointment.objects.filter(patient=patient).order_by('-date')[1:]
    inform = []

    if appointment is not None:
        inform = get_data_appointment(appointment)

    return render(
        request,
        'appointment.html',
        context={
            'doctor': doctor,
            'patient': patient,
            'appointment': appointment,
            'inform': inform,
            'appointments': Appointment.objects.filter(patient=patient) if Appointment.objects.filter(patient=patient) is not None else [],
            'classes_list': classes_list,
            "appointment_old": appointment_old,
        }
    )


def get_image(request):
    eye_id = request.GET.get('eye_id')
    try:
        eye = Eye_grounds.objects.get(id=eye_id)
        dicom = pydicom.dcmread(eye.img_path, force=True)

        pixel_array = dicom.pixel_array
        color_space = dicom.PhotometricInterpretation
        
        if color_space == 'RGB':
            _, im_arr = cv2.imencode('.png', cv2.cvtColor(pixel_array, cv2.COLOR_RGB2BGR))
        else:
            _, im_arr = cv2.imencode('.png', cv2.cvtColor(pixel_array, cv2.COLOR_YCR_CB2RGB))
        
        im_bytes = im_arr.tobytes()
        im_b64 = base64.b64encode(im_bytes)
        im_b64_str = im_b64.decode("utf8")

        return JsonResponse({
            'image': 'data:image/png;base64,{}'.format(im_b64_str)
        })
    except Eye_grounds.DoesNotExist:
        return JsonResponse({'error': 'Eye not found'}, status=404)
    except FileNotFoundError:
        return JsonResponse({'error': 'File not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_data_appointment_old(appointments, inform):
    inform_old = []
    number_app = 0
    for appointment in appointments:
        number_app +=1 
        for count, data in enumerate(Eye_grounds.objects.filter(appointment=appointment)):
            try:
                dicom = pydicom.dcmread(data.img_path, force=True)
                pixel_array = dicom.pixel_array

                inform_old.append(
                    {   
                        'number_app': number_app, 
                        'eye_id': str(data.id),
                        'count': count + 1,
                    }
                )
            except FileNotFoundError:
                print(f"Файл не найден: {data.img_path}")
                continue  
    # for item in inform:
    #     for item_old in inform_old:
    #         if item_old['count'] == item['count']:
    #             if 'apointment_old' not in item or item['apointment_old'] is None:
    #                 print(item_old)
    #                 item['apointment_old'] = []
    #             item['apointment_old'].append(item_old)

    return inform_old

def old_appointment(request, patient):

    doctor = Doctor.objects.get(user=request.user)
    appointment_id = request.POST.get('appointment_id')
       
    if appointment_id is None:

        patient = Patient.objects.get(id=patient)
        appointment = Appointment.objects.filter(patient=patient).last()
        appointment_old = Appointment.objects.filter(patient=patient).exclude(id=appointment.id) if appointment else Appointment.objects.filter(patient=patient)

        inform = get_data_appointment(appointment) if appointment else []
        inform_old = get_data_appointment_old(appointment_old, inform) if appointment else []

        return render(
            request,
            'appointment.html',
            context={
                'doctor': doctor,
                'patient': patient,
                'appointment': appointment,
                'inform': inform,
                'classes_list': classes_list,
                'check': 'check',
                "appointment_old": appointment_old,
                "inform_old": inform_old,
            }
        )
    else:
        appointment = Appointment.objects.get(id=appointment_id)
        appointment_old = Appointment.objects.filter(patient=patient).exclude(id=appointment.id) if appointment else Appointment.objects.filter(patient=patient)
        inform = []
        if appointment is not None:
            inform = get_data_appointment(appointment)
            inform_old = get_data_appointment_old(appointment_old, inform)

        return render(
            request,
            'appointment.html',
            context={
                'doctor': doctor,
                'patient': patient,
                'appointment': appointment,
                'inform': inform,
                'classes_list': classes_list,
                'check': 'check',
                "appointment_old": appointment_old,
                "inform_old": inform_old,
            })


def add_appointment(patient, dicom_path, mask_path, study_date, class_ml, score=0.0):
    # Проверяем, существует ли уже назначение для данного пациента и даты
    appointment, created = Appointment.objects.get_or_create(
        patient=patient,
        date=study_date,
        defaults={'score': score}
    )
    
    # Если назначение уже существует и новый балл больше старого, обновляем его
    if not created and score > appointment.score:
        appointment.score = score
        appointment.save()
    
    # Создаем запись в Eye_grounds
    data = Eye_grounds(
        appointment=appointment,
        img_path=dicom_path,
        mask_path=mask_path,
        class_ml=class_ml,
        pathology_ml=class_ml,
        score=score,
    )
    data.save()


def modal_pacient(request, id_appointment):
    doctor = Doctor.objects.get(user=request.user)
    appointment = Appointment.objects.get(id=id_appointment)
    patient = appointment.patient
    inform = []
    if appointment is not None:
        inform = get_data_appointment(appointment)

    return HttpResponse(
        json.dumps({
            "result": True,
            "modal_list": render_to_string(
                'modal_pacient.html',
                context={
                    'doctor': doctor,
                    'patient': patient,
                    'appointment': appointment,
                    'inform': inform,
                    'appointments': Appointment.objects.filter(patient=patient) if Appointment.objects.filter(patient=patient) is not None else [],
                    'classes_list': classes_list,
                }
            ),
        }), content_type="application/json")


def inference(dicom, pixel_array):

    color_space = dicom.PhotometricInterpretation
    if color_space == 'RGB':
        im_arr = cv2.cvtColor(pixel_array, cv2.COLOR_RGB2BGR)
    else:
        im_arr = cv2.cvtColor(pixel_array, cv2.COLOR_YCR_CB2RGB)

    results = model_clas(im_arr)

    for result in results:

        top1_class_index = result.probs.top1
        top1_confidence = result.probs.top1conf.item()
        top1_class_name = result.names[top1_class_index]
    print('top1_class_index', top1_class_index, '/n',
          'top1_confidence', top1_confidence, '/n'
          'top1_class_name', top1_class_name, '/n'
    )    
    if (top1_class_name == 'good'):
        res_DR = model(im_arr)
        for r in res_DR:
            top1_class_index_DR = r.probs.top1
            top1_confidence_DR = r.probs.top1conf.item()
            top1_class_name_DR = r.names[top1_class_index]
        if (top1_confidence_DR >= 0.55):
            score = top1_confidence_DR
            class_ml = 1
        else:
            score = top1_confidence_DR
            class_ml = 0
    elif (top1_class_name == 'bad'):
        class_ml = 2
        score = 0
    else:
        class_ml = 2
        score = 0   
    return score, class_ml


def read_dicom(dicom):
    patient_sex = dicom.PatientSex
    patient = dicom.PatientName
    ac_number = dicom.PatientID
    patient = str(patient).split("^")
    patient_name = patient[0]
    patient_surname = patient[1]
    if len(patient) >= 3:
        patient_patronymic = patient[2]
    else:
        patient_patronymic = '-'
    device = dicom.DeviceSerialNumber

    if dicom.PatientBirthDate == '':
        if dicom.DeviceSerialNumber == '11110011':
            study_date = dicom.StudyDate
            year = int(study_date[:4])
            month = int(study_date[4:6])
            day = int(study_date[6:])
            patient_birthdate = date(year, month, day)
        else:
            patient_birthdate = date.today()
    else:
        patient_birthdate = dicom.PatientBirthDate
        year = int(patient_birthdate[:4])
        month = int(patient_birthdate[4:6])
        day = int(patient_birthdate[6:])
        patient_birthdate = date(year, month, day)
    patient_birthdate = patient_birthdate

    if dicom.StudyDate == '':
        study_date = date.today()
    else:
        study_date = dicom.StudyDate
        year = int(study_date[:4])
        month = int(study_date[4:6])
        day = int(study_date[6:])
        study_date = date(year, month, day)
    study_date = study_date

    return patient_sex, patient_name, patient_surname, patient_patronymic, device, patient_birthdate, study_date, ac_number

def process_appointment(dicom_path):

    if len(Eye_grounds.objects.filter(img_path=dicom_path)) == 0:
        dicom = pydicom.dcmread(dicom_path, force=True)
        if hasattr(dicom, 'pixel_array'):
            try:
                patient_sex, patient_name, patient_surname, patient_patronymic, device, patient_birthdate, study_date, ac_number = read_dicom(dicom)
                pixel_array = dicom.pixel_array
                score, class_ml = inference(dicom, pixel_array)
                color_mask = inference(
                    Image.open(img_path)
                )
                masks_uuid 
                mask_path = color_mask.save('orthanc_db/masks')

                patient_search = Patient.objects.filter(
                    first_name=patient_name,
                    surname=patient_surname,
                    patronymic=patient_patronymic,
                    date_of_birth=patient_birthdate
                )

                if len(patient_search) > 0:
                    add_appointment(
                        patient=patient_search[0],
                        study_date=study_date,
                        dicom_path=dicom_path,
                        mask_path=mask_path,
                        class_ml=class_ml,
                        score=score,
                    )
                    print("Новый прием", add_appointment)
                else:
                    if Location.objects.filter(number_id=device):
                        locat = Location.objects.get(number_id=device)
                    else:
                        locat = Location.objects.get(number_id=3319581040677)
                    patient_create = Patient(
                        first_name=patient_name,
                        surname=patient_surname,
                        patronymic=patient_patronymic,
                        date_of_birth=patient_birthdate,
                        sex=1 if patient_sex == 'M' else 2,  # TODO: refactoring
                        locations=locat,
                        type_pacient=1,
                    )

                    if ac_number[0] == "q" or ac_number[0] == "Q":
                        patient_create.type_pacient = 2
                    else:
                        patient_create.type_pacient = 1
                    patient_create.save()
                    add_appointment(
                        patient=patient_create,
                        dicom_path=dicom_path,
                        mask_path=mask_path,
                        study_date=study_date,
                        class_ml=class_ml,
                        score=score,
                    )
                    message_create = Message_save_dicom(
                        message='Save',
                        dicom_path=dicom_path,
                    )
                    message_create.save()
                    print('Сохранено')
            except Exception as ex:
                logging.error(f"Error processing {dicom_path}: {ex}")
                message_create = Message_save_dicom(
                    message='Error',
                    dicom_path=dicom_path,
                )
                message_create.save()
                pass
    else:
        print("Ошибка чтения", dicom_path)
        pass


def appointment_search(request):
    logging.debug("start appointment_search")
    bd_dir = '/var/lib/orthanc/db-v6'
    dicom_count = 0

    for idx, appointment_dir in enumerate(os.listdir(bd_dir)):
        if os.path.isdir(os.path.join(bd_dir, appointment_dir)) and appointment_dir != 'WebViewerCache':
            for dicom_dir in os.listdir(os.path.join(bd_dir, appointment_dir)):
                dicom_files = os.listdir(os.path.join(bd_dir, appointment_dir, dicom_dir))
                for dicom_file in dicom_files:
                    dicom_path = os.path.join(bd_dir, appointment_dir, dicom_dir, dicom_file)
                    if len(Eye_grounds.objects.filter(img_path=dicom_path)) == 0:
                        dicom = pydicom.dcmread(dicom_path, force=True)
                        if hasattr(dicom, 'pixel_array'):
                            try:
                                process_appointment(dicom_path)
                                dicom_count += 1
                            except Exception as ex:
                                print('Error', ex)
                                pass
    return HttpResponse(f"Appointment search completed. Total DICOM count: {dicom_count}", status=200)


def progress_bar(request):
    global prog_bar_val
    if request.method == 'GET':
        data = prog_bar_val
        return JsonResponse({'status': data})


def delete_check(request, id_patient):
    pacient = Patient.objects.get(id=id_patient)
    pacient.checked = False
    pacient.save()
    return redirect('home')


def delegate(request, id_patient):
    pacient = Patient.objects.get(id=id_patient)
    doctor = Doctor.objects.get(user=request.user)
    doctor.patients.remove(pacient)
    doctor.save()
    return redirect('home')


def homes(request):
    return render(request, 'home.html')

def download_excel(request):
    if request.method == 'POST':
        selected_patients = request.POST.getlist('selected_patients')
        # Получение данных выбранных пациентов
        patients_data = []
        for id in selected_patients:
            # patient = Patient.objects.get(id=patient_id)
            zakluchenie = Appointment.objects.get(id=id)
            zakluchenie.export_csv = True
            zakluchenie.save()
            patients_data.append({
                'Больница': zakluchenie.patient.locations,
                'Фамилия': zakluchenie.patient.first_name,
                'Имя': zakluchenie.patient.surname,
                'Отчество': zakluchenie.patient.patronymic,
                'ДР': zakluchenie.patient.date_of_birth.date(),
                'ДП': zakluchenie.date.date(),
                'Score': round(zakluchenie.score, 2),
                'Заключение': zakluchenie.report,
            })
        # Создание DataFrame из данных пациентов
        df = pd.DataFrame(patients_data)
        df = df.sort_values(by=['Фамилия', 'Имя'])

        # Создание Excel-файла с помощью pandas
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Пациенты', index=False)

        worksheet = writer.sheets['Пациенты']
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:D', 15)
        worksheet.set_column('E:F', 12)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 25)

        writer.save()
        output.seek(0)

        # Создание HTTP-ответа с Excel-файлом для скачивания
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=patients.xlsx'
        response.write(output.getvalue())

        return response


@csrf_exempt
def api_dicom(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        bd_dir = '/var/lib/orthanc/db-v6'
        mas = list(data['file_path'])
        dicom_path = bd_dir + '/' + mas[0] + mas[1] + '/' + mas[2] + mas[3] + '/' + data['file_path']
        if not Eye_grounds.objects.filter(img_path=dicom_path).exists():
            dicom = pydicom.dcmread(dicom_path, force=True)
            if hasattr(dicom, 'pixel_array'):
                try:
                    process_appointment(dicom_path)
                    response_data = {
                        'message': 'DICOM path received successfully'
                    }
                    return JsonResponse(response_data, status=200)
                except Exception as ex:
                    print('Error', ex)
                    return JsonResponse({'error': str(ex)}, status=500)

        return JsonResponse({'message': 'DICOM already exists'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def json_data_appoints(request, id_patient):

    appointment = Appointment.objects.get(id=id_patient)
    patient = Patient.objects.get(appointments=appointment)
    appointments = [appointment] + [a for a in patient.appointments.all() if a != appointment]
    response = {}
    if patient.appointments.exists():
        for index, item in enumerate(appointments):
            inform = get_data_appointment(item)
            response[f'appointment{index}'] = inform
    return JsonResponse(response)

def employee_json(request):
    patients = Patient.objects.all()
    data = [patient.get_data() for patient in patients]
    response = {'data': data}
    return JsonResponse(response)

def migrate_data(request):
    for reg in Region_api.objects.all():
        print(reg.region)
        if not Region.objects.filter(region=reg.region).exists():
          reg_api = Region(
              number_id=reg.number_id,
              region=reg.region,
          )
          reg_api.save()
    for log in Location_api.objects.all():
        reg = Region.objects.get(region=log.region)
        if not Location.objects.filter(number_id=log.number_id).exists():
          log = Location(
                number_id = log.number_id,
                location = log.location,
                region = reg,
          )
          log.save()
        # Перенос данных из Doctor в Doctor_api
    for doctor in Doctor_api.objects.all():
        reg = Region.objects.get(number_id=doctor.region.number_id)
        if not Doctor.objects.filter(user=doctor.user, post=doctor.post).exists():
            doctor = Doctor(
                user=doctor.user,
                first_name=doctor.first_name,
                surname=doctor.surname,
                patronymic=doctor.patronymic,
                post=doctor.post,
                region=reg
            )
            doctor.save()
        else:
            doctor = Doctor.objects.get(user=doctor.user, post=doctor.post) 

    for patient in Patient_api.objects.all():
        if patient.locations is not None:
            loc = Location.objects.get(number_id=patient.locations.number_id)
        if not Patient.objects.filter(first_name=patient.first_name,
                                            surname=patient.surname,
                                            patronymic=patient.patronymic).exists():
            
            patient = Patient(

                first_name=patient.first_name,
                surname=patient.surname,
                patronymic=patient.patronymic,
                sex=patient.sex,
                pathology=patient.pathology,
                date_of_birth=patient.date_of_birth,
                appointment_last=patient.appointment_last,
                locations=loc,
                checked=patient.checked,
                type_pacient=patient.type_pacient
            )
            patient.save()
        else:
            patient = Patient.objects.get(first_name=patient.first_name,
                                            surname=patient.surname,
                                            patronymic=patient.patronymic)  

    for apointment in Appointment_api.objects.all():
        patient_ = Patient.objects.get(first_name=apointment.patient.first_name,
                            surname=apointment.patient.surname,
                            patronymic=apointment.patient.patronymic)  
        if not Appointment.objects.filter(patient=patient, date=apointment.date).exists():
            doctor = Doctor.objects.get(user=apointment.patient.doctor.user)
            apointment = Appointment(
                patient = patient_,
                doctor=doctor,
                date = apointment.date,
                score = apointment.score,
                report = apointment.report,
                pathology = apointment.pathology,
                checked = apointment.checked,
                fixing_doctor=apointment.patient.fixing_doctor,
            )
            apointment.save()       
        else:
            apointment = Appointment.objects.get(patient=patient, date = apointment.date) 

    for eye in Eye_grounds_api.objects.all():

        patient = Patient.objects.get(first_name=eye.appointment.patient.first_name,
                                      surname=eye.appointment.patient.surname,
                                      patronymic=eye.appointment.patient.patronymic)
        try:
            appointment = Appointment.objects.get(patient=patient, date=eye.appointment.date)
            if not Eye_grounds.objects.filter(img_path=eye.img_path).exists():
                eye = Eye_grounds(
                appointment = appointment,
                img_path = eye.img_path,
                mask_path = eye.mask_path,
                class_ml = eye.class_ml,
                score = eye.score,
                pathology_ml = eye.pathology_ml,
                pathology_doctor = eye.pathology_doctor,
                )
                eye.save()   
        except Appointment.DoesNotExist:
            print(f"Appointment not found for patient {patient} on date {eye.appointment.date}")
        except Exception as e:
            print(f"An error occurred: {e}")
    return JsonResponse({'status': 'Data migration completed'})\

def patient_list(request):

    filters = {
        'pathology': request.GET.get('pathology', ''),
        'hospital': request.GET.get('hospital', ''),
        'surname': request.GET.get('surname', ''),
        'first_name': request.GET.get('first_name', ''),
        'patronymic': request.GET.get('patronymic', '')
    }
    list_patient = Patient.objects.all()
    list_hospital = Location.objects.all()  
 
    if filters['hospital']:
        list_hospital = list_hospital.filter(location__icontains=filters['hospital'])
        list_patient = list_patient.filter(locations__in=list_hospital)   
    if filters['surname']:
        list_patient = list_patient.filter(surname__icontains=filters['surname'])
    if filters['first_name']:
        list_patient = list_patient.filter(first_name__icontains=filters['first_name'])
    if filters['patronymic']:
        list_patient = list_patient.filter(patronymic__icontains=filters['patronymic'])

    paginator = Paginator(list_patient, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        patients_data = [
            {
                'hospital': str(patient.locations),
                'surname': patient.surname,
                'first_name': patient.first_name,
                'patronymic': patient.patronymic,
                'appointment_last': patient.appointment_last.strftime('%d-%m-%Y'),
                'id': patient.id,
                'appointment': str(Appointment.objects.filter(patient=patient))
            }
            for patient in page_obj
        ]

        return JsonResponse({
            'patients': patients_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
        })


def app_check(request):
    app_list = Appointment.objects.all()
    a_list = []
    for app in app_list:
        if len(Appointment.objects.filter(patient=app.patient, date=app.date)) > 1:
            a_list.append(app)
    print(a_list)        
    return JsonResponse({
        'app': str(a_list),
    })      