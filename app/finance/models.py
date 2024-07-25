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
    user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)
    status = models.IntegerField()
    added_by = models.ForeignKey(AuthUser, models.DO_NOTHING, related_name='added_by')
    date_added = models.DateField(default=timezone.now)
    date_updated = models.DateField()

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

class exporting_csv(models.Model):
    tracking_number = models.CharField(max_length=255, blank=True, null=True)
    client_surname = models.CharField(max_length=255, blank=True, null=True)
    client_first_name= models.CharField(max_length=255, blank=True, null=True)
    client_middle_name = models.CharField(max_length=255, blank=True, null=True)
    client_suffix = models.CharField(max_length=255, blank=True, null=True)
    age = models.CharField(max_length=255, blank=True, null=True)
    civil_status = models.CharField(max_length=255, blank=True, null=True)
    birthday = models.DateField()
    sex = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    barangay = models.CharField(max_length=255, blank=True, null=True)
    municipality = models.CharField(max_length=255, blank=True, null=True)
    district = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)

    bene_surname = models.CharField(max_length=255, blank=True, null=True)
    bene_first_name= models.CharField(max_length=255, blank=True, null=True)
    bene_middle_name = models.CharField(max_length=255, blank=True, null=True)
    bene_suffix = models.CharField(max_length=255, blank=True, null=True)
    bene_age = models.CharField(max_length=255, blank=True, null=True)
    bene_civil_status = models.CharField(max_length=255, blank=True, null=True)
    bene_birthday = models.DateField()
    bene_sex = models.CharField(max_length=255, blank=True, null=True)
    bene_street = models.CharField(max_length=255, blank=True, null=True)
    bene_barangay = models.CharField(max_length=255, blank=True, null=True)
    bene_municipality = models.CharField(max_length=255, blank=True, null=True)
    bene_district = models.CharField(max_length=255, blank=True, null=True)
    bene_province = models.CharField(max_length=255, blank=True, null=True)
    bene_region = models.CharField(max_length=255, blank=True, null=True)

    relation = models.CharField(max_length=255, blank=True, null=True)
    assistance_category = models.CharField(max_length=255, blank=True, null=True)
    amount_of_assistance = models.CharField(max_length=255, blank=True, null=True)
    mode_of_release = models.CharField(max_length=255, blank=True, null=True)
    source_of_referral = models.CharField(max_length=255, blank=True, null=True)
    source_of_fund = models.CharField(max_length=255, blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    date_transaction = models.DateField()
    swo_name = models.CharField(max_length=255, blank=True, null=True)
    service_provider = models.CharField(max_length=255, blank=True, null=True)
    gl_number = models.CharField(max_length=255, blank=True, null=True)
    dv_date = models.CharField(max_length=255, blank=True, null=True)
    dv_number = models.CharField(max_length=255, blank=True, null=True)
    status_of_transaction = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'finance_exporting_tbl'


