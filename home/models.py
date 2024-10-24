from datetime import datetime
import uuid
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone
from multiselectfield import MultiSelectField

class Region(models.Model):
    number_id = models.IntegerField(default=None)
    region = models.CharField(max_length=200)

    def __str__(self):
        return '%s' % self.region


class Location(models.Model):
    number_id = models.IntegerField(default=None)
    location = models.CharField(max_length=200)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return '%s' % self.location

class Doctor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    first_name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    patronymic = models.CharField(max_length=200)
    postes = [
        (1, 'Доктор'),
        (2, 'Заведущий(ая)'),
        (3, 'Медсестра(брат)')
    ]
    post = models.PositiveIntegerField(choices=postes)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return '%s %s %s (%s)' % (self.surname, self.first_name, self.patronymic, self.post)

class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.CharField(max_length=200, blank=True, null=True) 

    first_name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    patronymic = models.CharField(max_length=200)
    sexes = [
        (1, 'Мужской'),
        (2, 'Женский'),
    ]
    sex = models.PositiveIntegerField(choices=sexes, default=1)
    pathology = models.BooleanField(default=False, null=True)
    date_of_birth = models.DateTimeField()
    appointment_last = models.DateTimeField(default=timezone.now)
    locations = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True)
    checked = models.BooleanField(default=False)
    
    t = [
        (1, 'Диабет'),
        (2, 'Без диабета')]
    type_pacient = models.PositiveIntegerField(choices=t, default=1)
    def __str__(self):
        return '%s %s %s' % (self.surname, self.first_name, self.patronymic)

    def get_data(self):
        appointments = []
        today = date.today()

        day = int(self.date_of_birth.strftime('%d'))
        month = int(self.date_of_birth.strftime('%m'))
        year = int(self.date_of_birth.strftime('%Y'))

        age = today.year - year - ((today.month, today.day) < (month, day))

        for appointment in Appointment.objects.filter(patient=self):
            appointments.append({
                'id': appointment.id,
                'date': appointment.date,
            })
        return {
            'locations': str(self.locations),
            'first_name': self.first_name,
            'surname': self.surname,
            'patronymic': self.patronymic,
            'appointments': appointments,
            'date_of_birth': self.date_of_birth.strftime('%Y-%m-%d'),
            'appointment_last': self.appointment_last.strftime('%Y-%m-%d'),
            'pathology': self.pathology,
            'age': age
        }

class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, blank=True)

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, blank=True, null=True)
    doctors = MultiSelectField(choices=[(doctor.id, str(doctor)) for doctor in Doctor.objects.all()], blank=True, null=True)

    date = models.DateTimeField(default=datetime.now)
    score = models.FloatField(default=None, null=True)
    report = models.TextField(default=None, null=True)
    pathology = models.BooleanField(default=False, null=True)
    checked = models.BooleanField(default=False, null=True)
    fixing_doctor = models.BooleanField(default=False)
    export_csv = models.BooleanField(default=False)
    def __str__(self):
        if self.patient:
            return f'{self.patient.first_name} {self.patient.surname} {self.date} {self.pathology}'
        return f'{self.date}'

class Eye_grounds(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, blank=True)
    img_path = models.CharField(max_length=200)
    mask_path = models.ImageField(upload_to='maskas/', blank=True, default=None, null=True)
    class_ml = models.CharField(max_length=200, default=None)
    class_doctor = models.IntegerField(default=6)
    score = models.FloatField(default=None, null=True)
    pathology_ml = models.IntegerField(default=None)
    pathology_doctor = models.IntegerField(default=None, null=True)

    @property
    def mask_path_url(self):
        if self.mask_path and hasattr(self.mask_path, 'url'):
            return self.mask_path.url
    def __str__(self):
        if self.appointment and self.appointment.patient:
            return f'{self.id} {self.appointment.patient.first_name} {self.appointment.patient.surname}'
        return super().__str__()
        
class Metrics(models.Model):
    Precision = models.FloatField(default=1000)
    Reccal = models.FloatField(default=1000)
    Accuracy = models.FloatField(default=1000)
    Specificity = models.FloatField(default=1000)
    TP = models.IntegerField(default=1000)
    TN = models.IntegerField(default=1000)
    FP = models.IntegerField(default=1000)
    FN = models.IntegerField(default=1000)
    Precision_B = models.FloatField(default=1000)
    Reccal_B = models.FloatField(default=1000)
    Accuracy_B = models.FloatField(default=1000)
    Specificity_B = models.FloatField(default=1000)
    TP_B = models.IntegerField(default=1000)
    TN_B = models.IntegerField(default=1000)
    FP_B = models.IntegerField(default=1000)
    FN_B = models.IntegerField(default=1000)
    def __str__(self):
        return '%s' % (self.id)

class Message_save_dicom(models.Model):
    message = models.CharField(max_length=200)
    dicom_path = models.CharField(max_length=200)
    date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    def __str__(self):
        return '%s %s %s' % (self.message, self.dicom_path, self.date)

