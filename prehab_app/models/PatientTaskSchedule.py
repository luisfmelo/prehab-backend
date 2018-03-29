from django.db import models

from prehab_app.models.Task import Task
from prehab_app.models.Prehab import Prehab


class PatientTaskSchedule(models.Model):
    id = models.AutoField(primary_key=True)
    prehab_id = models.ForeignKey(Prehab, on_delete=models.CASCADE, db_column='prehab_id')
    week_number = models.IntegerField(blank=False, null=False)
    day_number = models.IntegerField(blank=False, null=False)
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE, db_column='task_id')
    expected_repetitions = models.IntegerField(blank=False, null=True)
    actual_repetitions = models.IntegerField(blank=False, null=True)
    status_id = models.IntegerField(blank=False, null=True, default=1)

    class Meta:
        managed = False
        db_table = 'patient_task_schedule'
        ordering = ['-id']