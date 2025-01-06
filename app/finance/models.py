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
    with_without_dv = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True) #UPDATED DATA
    status = models.IntegerField()
    added_by = models.ForeignKey(AuthUser, models.DO_NOTHING, related_name='added_by') #ADDED BY IS ENCODED DATA
    date_added = models.DateField(default=timezone.now)
    date_updated = models.DateField()
    soa_total_amount = models.CharField(max_length=255, blank=True, null=True)
    dv_data = models.ForeignKey('disbursementVoucher', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'finance_voucher_tbl'

class finance_voucherData(models.Model):
    voucher = models.ForeignKey('finance_voucher', models.DO_NOTHING, blank=True, null=True)
    transactionStatus = models.ForeignKey(Transaction, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'finance_voucherdata_tbl'

class finance_outsideFo(models.Model):
    voucher = models.ForeignKey('finance_voucher', models.DO_NOTHING, blank=True, null=True)
    glnumber = models.CharField(max_length=255, blank=True, null=True)
    service_provider = models.ForeignKey(ServiceProvider, models.DO_NOTHING, blank=True, null=True)
    date_soa = models.DateField(blank=True, null=True)
    client_name = models.CharField(max_length=255, blank=True, null=True)
    assistance_type = models.CharField(max_length=255, blank=True, null=True)
    amount = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'finance_outsidefo_tbl'

class disbursementVoucher(models.Model):
    dv_tracking_code = models.CharField(max_length=255, blank=True, null=True)
    dv_name = models.CharField(max_length=255, blank=True, null=True)
    date_entried = models.DateField(default=timezone.now)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    sp = models.ForeignKey(ServiceProvider, models.DO_NOTHING, blank=True, null=True)
    amount = models.CharField(max_length=255, blank=True, null=True)
    dv_date = models.DateField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'finance_dv_tbl'

class disbursementVoucherData(models.Model):
    dv = models.ForeignKey(disbursementVoucher, models.DO_NOTHING, blank=True, null=True)
    soa = models.ForeignKey(finance_voucher, models.DO_NOTHING, blank=True, null=True)
    added_by = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)
    date_added = models.DateField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'finance_dv_data_tbl'

