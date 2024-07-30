from datetime import date, timedelta, datetime
import os
from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from app.libraries.models import CivilStatus, Suffix, Sex, Barangay, Relation, FundSource, ServiceProvider, FileType, \
    Category, SubCategory, Tribe, ModeOfAdmission, ModeOfAssistance,SubModeofAssistance, TypeOfAssistance, Purpose, \
    LibAssistanceType, PriorityLine, medicine, occupation_tbl, AssistanceProvided, presented_id
from app.models import AuthUser, AuthUserGroups, AuthGroup, AuthuserDetails
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator
from app.models import AuthUser
from django.db.models import Value, Sum, Count
from django.db.models import Q
import uuid

today = date.today()

class ClientBeneficiary(models.Model):
    last_name = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    suffix = models.ForeignKey(Suffix, models.DO_NOTHING, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    age = models.CharField(max_length=50, blank=True, null=True)
    sex = models.ForeignKey(Sex, models.DO_NOTHING)
    contact_number = models.CharField(max_length=50, blank=True, null=True)
    civil_status = models.ForeignKey(CivilStatus, models.DO_NOTHING)
    is_indi = models.BooleanField(blank=True, null=True)
    tribu = models.ForeignKey(Tribe, models.DO_NOTHING)
    barangay = models.ForeignKey(Barangay, models.DO_NOTHING,blank=False, null=False, to_field='brgy_code')
    street = models.CharField(max_length=255, blank=True, null=True)
    house_no = models.CharField(max_length=255, blank=True, null=True)
    village = models.CharField(max_length=255, blank=True, null=True)
    is_4ps = models.BooleanField(blank=True)
    number_4ps_id_number = models.CharField(db_column='4ps_id_number', max_length=50, blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    unique_id_number = models.CharField(max_length=50, unique=True)
    updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    is_validated = models.BooleanField(blank=True)
    registered_by = models.ForeignKey(AuthUser, models.DO_NOTHING, related_name='registered_by')
    date_of_registration = models.DateTimeField(default=timezone.now)
    occupation = models.ForeignKey(occupation_tbl, models.DO_NOTHING)
    salary = models.CharField(max_length=50, blank=True, null=True)
    presented = models.ForeignKey(presented_id, models.DO_NOTHING, blank=True, null=True)
    presented_id_no = models.CharField(max_length=255, blank=True, null=True)
    photo = models.FileField(upload_to='CIS/',default='photo/default.png')
    user_data = models.ForeignKey(AuthUser, models.DO_NOTHING, related_name='user_data')
    client_bene_fullname = models.CharField(max_length=255, blank=True, null=True)

    @property
    def get_client_fullname(self): #GI GAMIT SA SERIALIZER FOR VIEWING IN TABLE
        from app.libraries.models import Suffix

        data = Suffix.objects.filter(id=self.suffix_id).first()
        suffix_name = ""
        if data:
            suffix_name = data.name

        return "{} {}. {} {}".format(self.first_name, self.middle_name[:1], self.last_name,
                                     suffix_name) if self.middle_name else "{} {} {}".format(self.first_name,
                                                                                             self.last_name,
                                                                                             suffix_name)

    @property
    def get_client_fullname_formatted(self): #GI GAMIT NI SA ASSESSMENT VIEW
        from app.libraries.models import Suffix

        data = Suffix.objects.filter(id=self.suffix_id).first()
        suffix_name = ""
        if data:
            suffix_name = data.name

        return "{}, {} {} {}".format(self.last_name, self.first_name, self.middle_name[:1],
                                     suffix_name) if self.middle_name else "{}, {} {}".format(self.last_name,
                                                                                             self.first_name,
                                                                                             suffix_name)
    @property
    def full_name(self): #FOR FULL NAME NA CLEAN NO SWAPPING OF ARRANGEMENT
        from app.libraries.models import Suffix

        data = Suffix.objects.filter(id=self.suffix_id).first()
        suffix_name = ""
        if data:
            suffix_name = data.name
        return "{} {} {}, {}".format(self.first_name, self.middle_name, self.last_name, suffix_name)


    @property
    def get_client_address(self):
        return "{}, {}, {}".format(self.barangay.city_code.prov_code.prov_name, self.barangay.city_code.city_name, self.barangay.brgy_name)

    @property
    def get_age(self):
        today = date.today()
        return today.year - self.birthdate.year - (
                    (today.month, today.day) < (self.birthdate.month, self.birthdate.day))

    @property
    def get_picture(self):
        get_picture = uploadfile.objects.filter(client_bene_id=self.id).first()
        return get_picture.file_field1.url

    class Meta:
        managed = False
        db_table = 'tbl_client_beneficiary_information'

class ClientBeneficiaryUpdateHistory(models.Model):
    unique_id_number = models.ForeignKey('ClientBeneficiary', models.DO_NOTHING, to_field='unique_id_number')
    last_name = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    suffix = models.ForeignKey(Suffix, models.DO_NOTHING, blank=True, null=True)
    date_updated = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'tbl_client_beneficiary_update_history'


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename_start = filename.replace('.'+ext,'')
    filename = "%s__%s.%s" % (uuid.uuid4(),filename_start, ext)
    return os.path.join('CIS', filename)

class uploadfile(models.Model):
    file_field1 = models.FileField(
        upload_to=get_file_path,
        verbose_name=(u'File'),
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            MaxValueValidator(1024 * 1024)  # Limiting to 1 MB
        ]
    )
    client_bene = models.ForeignKey('ClientBeneficiary', models.DO_NOTHING)
    class Meta:
        managed = False
        db_table = 'tbl_transaction_file_field'

@receiver(models.signals.post_delete, sender=uploadfile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file_field1:
        if os.path.isfile(instance.file_field1.path):
            os.remove(instance.file_field1.path)

class ClientBeneficiaryFamilyComposition(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    suffix = models.ForeignKey(Suffix, models.DO_NOTHING)
    sex = models.ForeignKey(Sex, models.DO_NOTHING)
    relation = models.ForeignKey(Relation,models.DO_NOTHING)
    birthdate = models.DateField(default=timezone.now)
    occupation = models.ForeignKey('occupation_tbl', models.DO_NOTHING)
    salary = models.CharField(max_length=255, blank=True, null=True)
    clientbene = models.ForeignKey('ClientBeneficiary', models.DO_NOTHING)
    age = models.CharField(max_length=255, blank=True, null=True)

    @property
    def get_family_fullname_formatted(self):

        data = Suffix.objects.filter(id=self.suffix_id).first()
        suffix_name = ""
        if data:
            suffix_name = data.name
        return "{} {}. {} {}".format(self.first_name, self.middle_name[:1], self.last_name,
                                     suffix_name).upper() if self.middle_name else "{} {}. {}".format(self.first_name,
                                                                                                      self.last_name,
                                                                                                      suffix_name).upper()

    @property
    def get_age(self):
        today = date.today()
        return today.year - self.birthdate.year - (
                (today.month, today.day) < (self.birthdate.month, self.birthdate.day))

    class Meta:
        managed = False
        db_table = 'tbl_clientbene_family_roster'

class ErrorLogData(models.Model):
    error_log = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_transaction_error_log'

class Transaction(models.Model):
    tracking_number = models.CharField(max_length=255, unique=True)
    relation = models.ForeignKey(Relation, models.DO_NOTHING)
    client_category = models.ForeignKey(Category, models.DO_NOTHING, related_name='client_category')
    client_sub_category = models.ForeignKey(SubCategory, models.DO_NOTHING, related_name='client_subcategory')
    bene_category = models.ForeignKey(Category, models.DO_NOTHING, related_name='bene_category')
    bene_sub_category = models.ForeignKey(SubCategory, models.DO_NOTHING, related_name='bene_subcategory')
    mode_of_admission = models.ForeignKey(ModeOfAdmission, models.DO_NOTHING, blank=True, null=True)
    fund_source = models.ForeignKey(FundSource, models.DO_NOTHING, blank=True, null=True)
    purpose = models.ForeignKey(Purpose, models.DO_NOTHING, blank=True, null=True)
    lib_type_of_assistance = models.ForeignKey(LibAssistanceType, models.DO_NOTHING, blank=False, null=False)
    lib_assistance_category = models.ForeignKey(TypeOfAssistance, models.DO_NOTHING, blank=False, null=False)
    date_of_transaction = models.DateField(default=timezone.now) #default=today
    date_entried = models.DateTimeField()
    client = models.ForeignKey('ClientBeneficiary', models.DO_NOTHING, blank=False, null=False)
    bene = models.ForeignKey('ClientBeneficiary', models.DO_NOTHING, related_name='beneficiary',blank=False, null=False)
    swo = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=False, null=False)
    is_case_study = models.CharField(max_length=255, null=True)
    priority = models.ForeignKey(PriorityLine,models.DO_NOTHING, blank=True, null=True)
    is_return_new = models.CharField(max_length=255, blank=True, null=True)
    is_gl = models.CharField(max_length=255, blank=True, null=True)
    is_cv = models.CharField(max_length=255, blank=True, null=True)
    is_pcv = models.CharField(max_length=255, blank=True, null=True)
    is_onsite_offsite = models.CharField(max_length=255, blank=True, null=True)
    is_online = models.CharField(max_length=255, blank=True, null=True)
    is_walkin = models.CharField(max_length=255, blank=True, null=True)
    is_referral = models.CharField(max_length=255, blank=True, null=True)
    service_provider = models.ForeignKey(ServiceProvider, models.DO_NOTHING, blank=True, null=True)
    is_ce_cash = models.SmallIntegerField(blank=True, null=True)
    is_ce_gl = models.SmallIntegerField(blank=True, null=True)
    provided_hotmeal = models.SmallIntegerField(blank=True, null=True)
    provided_foodpack = models.SmallIntegerField(blank=True, null=True)
    provided_hygienekit = models.SmallIntegerField(blank=True, null=True)
    signatories = models.ForeignKey(AuthUser, models.DO_NOTHING, related_name='signatories')
    total_amount = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()
    swo_date_time_start = models.DateTimeField()
    swo_date_time_end = models.DateTimeField()
    dv_number = models.CharField(max_length=255, blank=True, null=True)
    dv_date = models.DateField()
    transaction_status = models.IntegerField(blank=True, null=True)
    requested_in = models.CharField(max_length=255, blank=True, null=True)
    is_pfa = models.SmallIntegerField(blank=True, null=True)
    is_swc = models.SmallIntegerField(blank=True, null=True)

    @property
    def get_action_action(self):
        status = TransactionStatus1.objects.filter(transaction_id=self.id).first()
        return status.status

    @property
    def get_remarks_action(self):
        status = TransactionStatus1.objects.filter(transaction_id=self.id).first()
        return status.status_remarks

    @property
    def get_verified(self):
        verified = TransactionStatus1.objects.filter(transaction_id=self.id).first()
        return verified.is_verified

    @property
    def get_swo(self):
        swo = TransactionStatus1.objects.filter(is_swo=1,transaction_id=self.id).first()
        return swo.is_swo

    @property
    def get_total(self):
        data = transaction_description.objects.filter(tracking_number_id=self.tracking_number).values('tracking_number').aggregate(total=Sum('total'))
        return data
    
    @property
    def get_finance_total(self):
        data = transaction_description.objects.filter(tracking_number_id=self.tracking_number).values('tracking_number').aggregate(total=Sum('total'))
        total = data['total'] if data['total'] is not None else 0.0  # Handle the case where total is None
        # Format the total with 2 decimal places and commas
        formatted_total = "{:,.2f}".format(total)
        return formatted_total
    
    @property
    def get_finance_status(self):
        status_data = "Unknown"  # Initialize with a default value
        status = TransactionStatus1.objects.filter(transaction=self).first()
        if status:
            if status.status == 1:
                status_data = "Pending"
            elif status.status == 2:
                status_data = "Ongoing"
            elif status.status == 3:
                status_data = "Complete assessment"
            elif status.status == 4:
                status_data = "Hold"
            elif status.status == 5:
                status_data = "Cancelled"
            elif status.status == 6:
                status_data = "Complete assessment"
            elif status.status == 7:
                status_data = "Ongoing"
        return status_data
    
    @property
    def swo_table(self):
        data = SocialWorker_Status.objects.filter(user_id=self.swo_id).first()
        return data.table

    @property
    def get_sp_data(self):#SERVICE PROVIDER DATA
        data = transaction_description.objects.filter(tracking_number_id=self.tracking_number).all()
        return data

    @property
    def assessment(self):
        data = AssessmentProblemPresented.objects.filter(transaction_id=self.id).first()
        return data.sw_assessment if data.sw_assessment else "N/a"
    
    @property
    def purpose(self):
        data = AssessmentProblemPresented.objects.filter(transaction_id=self.id).first()
        return data.problem_presented if data.problem_presented else "N/a"

    @property
    def date_time_transaction(self):
        data = TransactionStatus1.objects.filter(transaction_id=self.id).first()
        if data:
            return data.verified_time_start

    @property
    def date_time_assessment(self):
        data = TransactionStatus1.objects.filter(transaction_id=self.id).first()
        if data:
            return data.swo_time_end

    @property
    def finance_dv(self):
        from app.finance.models import finance_voucherData
        data = finance_voucherData.objects.filter(transactionStatus=self.id).first()
        return data.voucher.voucher_title if data else "N/a"
    
    @property
    def finance_dv_date(self):
        from app.finance.models import finance_voucherData
        data = finance_voucherData.objects.filter(transactionStatus=self.id).first()
        return data.voucher.date if data else "N/a"

    class Meta:
        managed = False
        db_table = 'tbl_transaction'

class transaction_description(models.Model):
    tracking_number = models.ForeignKey(Transaction, models.DO_NOTHING, to_field='tracking_number')
    provided_data = models.CharField(max_length=255, blank=True, null=True)
    regular_price = models.DecimalField(max_digits=19, decimal_places=2)
    regular_quantity = models.IntegerField()
    discount = models.DecimalField(max_digits=19, decimal_places=2)
    discount_price = models.DecimalField(max_digits=19, decimal_places=2)
    discount_quantity = models.IntegerField()
    total = models.DecimalField(max_digits=19, decimal_places=2)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)

    @property
    def get_total(self):
        data = transaction_description.objects.filter(tracking_number_id=self.tracking_number).values('tracking_number').annotate(total=Sum('total'))
        return data
        
    class Meta:
        managed = False
        db_table = 'tbl_transaction_provided'


class TransactionStatus1(models.Model):
    transaction = models.ForeignKey('Transaction', models.DO_NOTHING)
    queu_number = models.IntegerField()
    verified_time_start = models.DateTimeField()
    is_verified = models.IntegerField()
    verifier = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)
    verified_time_end = models.DateTimeField()
    swo_time_start = models.DateTimeField()
    is_swo = models.IntegerField()
    swo_time_end = models.DateTimeField()
    is_upload_photo = models.IntegerField()
    upload_time_end = models.DateTimeField()
    uploader_verifier = models.ForeignKey(AuthUser, models.DO_NOTHING, related_name='uploader_verifier')
    end_assessment = models.DateField()
    finance_status = models.SmallIntegerField(blank=True, null=True)
    status = models.IntegerField()
    status_remarks = models.CharField(max_length=255, blank=True, null=True)
    signatories_approved = models.SmallIntegerField(blank=True, null=True)
    transaction_status = models.IntegerField(blank=True, null=True)
    case_study_status = models.IntegerField()
    case_study_date = models.DateField()

    @property
    def get_total(self):
        #data = transaction_description.objects.filter(tracking_number_id=self.transaction.tracking_number).values('tracking_number').annotate(total=Sum('total'))
        calculate = transaction_description.objects.filter(tracking_number_id=self.transaction.tracking_number).aggregate(total_payment=Sum('total'))
        return calculate['total_payment'] 
    
    class Meta:
        managed = False
        db_table = 'tbl_transaction_status1'


class AssessmentProblemPresented(models.Model):
    problem_presented = models.TextField(blank=True, null=True)
    sw_assessment = models.TextField(blank=True, null=True)
    other_requirements = models.TextField(blank=True, null=True)
    transaction = models.ForeignKey('Transaction', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'tbl_transaction_prob_assess'

def get_file_requirements(instance, filename):
    ext = filename.split('.')[-1]
    filename_start = filename.replace('.'+ext,'')
    filename = "%s__%s.%s" % (uuid.uuid4(),filename_start, ext)
    return os.path.join('Transaction_requirements', filename)

class requirements_client(models.Model):
    requirements_uploaded = models.FileField(upload_to=get_file_requirements,verbose_name=(u'File'))
    transaction = models.ForeignKey('Transaction', models.DO_NOTHING)
    class Meta:
        managed = False
        db_table = 'tbl_transaction_file_requirements'

class TransactionServiceAssistance(models.Model):
    transaction_id = models.IntegerField(blank=True, null=True)
    service_assistance_id = models.IntegerField(blank=True, null=True)
    specify = models.CharField(max_length=1024, blank=True, null=True)
    is_checked = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_transaction_service_assistance'


class Mail(models.Model):
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    date_sent = models.DateTimeField(default=timezone.now)
    received_by = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)
    is_read = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_mail'


class SocialWorker_Status(models.Model):
    user = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING)
    status = models.IntegerField(blank=True, null=True)
    table = models.CharField(max_length=255, blank=True, null=True)
    date_transaction = models.DateField()

    @property
    def get_address(self):
        data = AuthuserDetails.objects.filter(user_id=self.user).first()
        if data:
            return data.barangay.city_code.prov_code.prov_name
        return None

    @property
    def get_tracking(self):
        data = TransactionStatus1.objects.filter(
            transaction_id__swo_id=self.user,
            transaction_id__date_of_transaction=date.today(),
            status=2
        ).first()
        if data:
            return data.transaction.tracking_number
        return None

    @property
    def get_total(self):
        return TransactionStatus1.objects.filter(
            transaction_id__swo_id=self.user,
            transaction_id__date_of_transaction=date.today(),
            status=1
        ).count()

    @property
    def get_ongoing(self):
        return TransactionStatus1.objects.filter(
            transaction_id__swo_id=self.user,
            transaction_id__date_of_transaction=date.today(),
            status=2
        ).count()

    @property
    def get_complete(self):
        return TransactionStatus1.objects.filter(
            Q(transaction_id__swo_id=self.user) &
            Q(transaction_id__date_of_transaction=date.today()) &
            (Q(status=6) | Q(status=3))
        ).count()

    @property
    def case_study(self):
        return TransactionStatus1.objects.filter(
            Q(transaction_id__swo_id=self.user) &
            Q(transaction_id__date_of_transaction=date.today()) &
            Q(status__in=[3, 6]) &
            Q(transaction_id__is_case_study=2)
        ).count()

    class Meta:
        managed = False
        db_table = 'swo_status_tbl'