from datetime import datetime
import uuid
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone


class Region_api(models.Model):
    number_id = models.IntegerField(default=None)
    region = models.CharField(max_length=200)

    def __str__(self):
        return '%s' % self.region


class Location_api(models.Model):
    number_id = models.IntegerField(default=None)
    location = models.CharField(max_length=200)
    region = models.ForeignKey(Region_api, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return '%s' % self.location


class Doctor_api(models.Model):
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
    region = models.ForeignKey(Region_api, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return '%s %s %s (%s)' % (self.surname, self.first_name, self.patronymic, self.post)


class Patient_api(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(Doctor_api, on_delete=models.CASCADE, blank=True, null=True)
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
    locations = models.ForeignKey(Location_api, on_delete=models.SET_NULL, blank=True, null=True)
    checked = models.BooleanField(default=False)
    fixing_doctor = models.BooleanField(default=False)
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

        for appointment in self.appointments.all():
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


class Appointment_api(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient_api, on_delete=models.CASCADE, blank=True)
    date = models.DateTimeField(default=datetime.now)
    score = models.FloatField(default=None, null=True)
    report = models.TextField(default=None, null=True)
    pathology = models.BooleanField(default=False, null=True)
    checked = models.BooleanField(default=False, null=True)

    def __str__(self):
        try:
            return '%s %s %s %s' % (
            Patient_api.objects.get(appointments=self).first_name, Patient_api.objects.get(appointments=self).surname,
            self.date, self.pathology)
        except:
            return f'{self.date}'


class Eye_grounds_api(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(Appointment_api, on_delete=models.CASCADE, blank=True)
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



