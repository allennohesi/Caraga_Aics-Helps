from datetime import date
import os
from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from app.libraries.models import CivilStatus, Suffix, Sex, Barangay, Relation, FundSource, ServiceProvider, FileType, \
    Category, SubCategory, Tribe, ModeOfAdmission, ModeOfAssistance,SubModeofAssistance, TypeOfAssistance, Purpose, \
    LibAssistanceType, PriorityLine, medicine, occupation_tbl, AssistanceProvided, presented_id

from app.requests.models import TransactionStatus1,Transaction
from app.models import AuthUser
from django.db.models import Value, Sum, Count
today = date.today()


class finance_voucher(models.Model):
    voucher_code = models.CharField(max_length=255, blank=True, null=True)
    voucher_title = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField()
    remarks = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'finance_voucher_tbl'

class finance_voucherData(models.Model):
    voucher = models.ForeignKey('finance_voucher', models.DO_NOTHING, blank=True, null=True)
    transactionStatus = models.ForeignKey(Transaction, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'finance_voucherdata_tbl'

