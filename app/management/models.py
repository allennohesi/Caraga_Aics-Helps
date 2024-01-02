from datetime import date

from django.db import models
from django.utils import timezone

from app.libraries.models import CivilStatus, Suffix, Sex, Barangay, Relation, FundSource, ServiceProvider, FileType
from app.models import AuthUser


class ClientBeneficiary(models.Model):
    last_name = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    suffix = models.ForeignKey(Suffix, models.DO_NOTHING)
    birthdate = models.DateField(blank=True, null=True)
    sex = models.ForeignKey(Sex, models.DO_NOTHING)
    contact_number = models.CharField(max_length=50, blank=True, null=True)
    civil_status = models.ForeignKey(CivilStatus, models.DO_NOTHING)
    is_indi = models.IntegerField(blank=True, null=True)
    tribu = models.CharField(max_length=150, blank=True, null=True)
    barangay = models.ForeignKey(Barangay, models.DO_NOTHING)
    street = models.CharField(max_length=255, blank=True, null=True)
    house_no = models.CharField(max_length=255, blank=True, null=True)
    village = models.CharField(max_length=255, blank=True, null=True)
    is_4ps = models.BooleanField(blank=True)
    number_4ps_id_number = models.CharField(db_column='4ps_id_number', max_length=50, blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    unique_id_number = models.CharField(max_length=50, blank=True, null=True)
    updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    is_validated = models.BooleanField(blank=True)
    registered_by = models.ForeignKey(AuthUser, models.DO_NOTHING, related_name='registered_by')
    date_of_registration = models.DateTimeField(default=timezone.now)
    occupation = models.CharField(max_length=1024, blank=True, null=True)
    salary = models.CharField(max_length=50, blank=True, null=True)

    @property
    def get_client_fullname(self):
        from app.libraries.models import UserSuffix

        data = UserSuffix.objects.filter(user_id=self.id).first()
        suffix_name = ""
        if data:
            suffix_name = data.suffix.name

        return "{} {}. {} {}".format(self.first_name, self.middle_name[:1], self.last_name,
                                     suffix_name) if self.middle_name else "{} {} {}".format(self.first_name,
                                                                                             self.last_name,
                                                                                             suffix_name)

    @property
    def get_client_fullname_formatted(self):
        from app.libraries.models import UserSuffix

        data = UserSuffix.objects.filter(user_id=self.id).first()
        suffix_name = ""
        if data:
            suffix_name = data.suffix.name

        return "{}, {} {} {}".format(self.last_name, self.first_name, self.middle_name[:1],
                                     suffix_name).upper() if self.middle_name else "{}, {} {}".format(self.last_name,
                                                                                             self.first_name,
                                                                                             suffix_name).upper()

    @property
    def get_client_address(self):
        return "{}, {}, {}".format(self.barangay.city_code.prov_code.name, self.barangay.city_code.name, self.barangay.name).upper()

    @property
    def get_age(self):
        today = date.today()
        return today.year - self.birthdate.year - (
                    (today.month, today.day) < (self.birthdate.month, self.birthdate.day))

    class Meta:
        managed = False
        db_table = 'tbl_client_beneficiary'


class ClientBeneficiaryFamilyComposition(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    suffix = models.ForeignKey(Suffix, models.DO_NOTHING)
    birthdate = models.DateField(blank=True, null=True)
    occupation = models.CharField(max_length=1024, blank=True, null=True)
    salary = models.CharField(max_length=50, blank=True, null=True)
    clientbene = models.ForeignKey('ClientBeneficiary', models.DO_NOTHING)

    @property
    def get_family_fullname_formatted(self):
        from app.libraries.models import UserSuffix

        data = UserSuffix.objects.filter(user_id=self.id).first()
        suffix_name = ""
        if data:
            suffix_name = data.suffix.name

        return "{}, {} {} {}".format(self.last_name, self.first_name, self.middle_name[:1],
                                     suffix_name).upper() if self.middle_name else "{}, {} {}".format(self.last_name,
                                                                                                      self.first_name,
                                                                                                      suffix_name).upper()

    @property
    def get_age(self):
        today = date.today()
        return today.year - self.birthdate.year - (
                (today.month, today.day) < (self.birthdate.month, self.birthdate.day))

    class Meta:
        managed = False
        db_table = 'tbl_clientbene_family_composition'


class Transaction(models.Model):
    tracking_number = models.CharField(max_length=255, blank=True, null=True)
    relation = models.ForeignKey(Relation, models.DO_NOTHING)
    client_category_id = models.IntegerField(blank=True, null=True)
    client_sub_category_id = models.IntegerField(blank=True, null=True)
    bene_category_id = models.IntegerField(blank=True, null=True)
    bene_sub_category_id = models.IntegerField(blank=True, null=True)
    problem_presented = models.TextField(blank=True, null=True)
    sw_assessment = models.TextField(blank=True, null=True)
    mode_of_admission_id = models.IntegerField(blank=True, null=True)
    mode_of_assistance_id = models.IntegerField(blank=True, null=True)
    sub_assistance = models.ForeignKey(SubModeofAssistance,models.DO_NOTHING, blank=True, null=True)
    fund_source = models.ForeignKey(FundSource, models.DO_NOTHING)
    amount_of_assistance = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    purpose_id = models.IntegerField(blank=True, null=True)
    type_of_assistance_id = models.IntegerField(blank=True, null=True)
    date_of_transaction = models.DateTimeField(default=timezone.now)
    client = models.ForeignKey('ClientBeneficiary', models.DO_NOTHING)
    bene = models.ForeignKey('ClientBeneficiary', models.DO_NOTHING, related_name='beneficiary')
    service_provider = models.ForeignKey(ServiceProvider, models.DO_NOTHING)

    @property
    def get_latest_status(self):
        details = TransactionStatus.objects.filter(transaction_id=self.id).order_by('-date_updated').first()
        if details.status == '0':
            return "<i class='fa fa-circle' style='color: #b0bec5'></i> Pending"
        if details.status == '1':
            return "<i class='fa fa-circle' style='color: #00b0ff'></i> Interviewed"
        if details.status == '2':
            return "<i class='fa fa-circle' style='color: #00e676f'></i> Reviewed and Approved"
        if details.status == '3':
            return "<i class='fa fa-circle' style='color: #ff9100'></i> Canceled"

    class Meta:
        managed = False
        db_table = 'tbl_transaction'


class TransactionStatus(models.Model):
    transaction = models.ForeignKey('Transaction', models.DO_NOTHING)
    status = models.IntegerField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    date_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'tbl_transaction_status'


class TransactionFiles(models.Model):
    transaction_id = models.IntegerField(blank=True, null=True)
    file = models.FileField(upload_to='requests/%Y/%m/%d')
    file_type = models.ForeignKey(FileType, models.DO_NOTHING)
    status = models.IntegerField(blank=True, null=True)
    date_uploaded = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'tbl_transaction_files'


class TransactionServiceAssistance(models.Model):
    transaction_id = models.IntegerField(blank=True, null=True)
    service_assistance_id = models.IntegerField(blank=True, null=True)
    specify = models.CharField(max_length=1024, blank=True, null=True)
    is_checked = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_transaction_service_assistance'