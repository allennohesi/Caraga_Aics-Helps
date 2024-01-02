# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    updated_by_id = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    branch_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class AuthtokenToken(models.Model):
    key = models.CharField(primary_key=True, max_length=40)
    created = models.DateTimeField()
    user = models.OneToOneField(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'authtoken_token'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DjangoSite(models.Model):
    domain = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'django_site'


class LibAssistanceCategory(models.Model):
    type_assistance = models.ForeignKey('LibAssistanceType', models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    acronym = models.CharField(max_length=255, blank=True, null=True)
    updated_by_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_assistance_category'


class LibAssistanceProvided(models.Model):
    provided_name = models.CharField(max_length=150, blank=True, null=True)
    assistance_sub_type_id = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_assistance_provided'


class LibAssistanceSubCategory(models.Model):
    category_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    acronym = models.CharField(max_length=255, blank=True, null=True)
    updated_by_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_assistance_sub_category'


class LibAssistanceType(models.Model):
    type_name = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_assistance_type'


class LibCategorySector(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    acronym = models.CharField(max_length=50, blank=True, null=True)
    updated_by_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_category_sector'


class LibCategorySub(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    acronym = models.CharField(max_length=255, blank=True, null=True)
    updated_by_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_category_sub'


class LibCivilStatus(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_civil_status'


class LibFileAttachmentType(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    is_required = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_file_attachment_type'




class LibLetterProvided(models.Model):
    letter_name = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_letter_provided'


class LibLocationBrgy(models.Model):
    brgy_name = models.CharField(max_length=100)
    city_code = models.ForeignKey('LibLocationCitymun', models.DO_NOTHING)
    brgy_code = models.CharField(max_length=9)
    brgy_mode = models.IntegerField(blank=True, null=True)
    urb_rur = models.IntegerField()
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_location_brgy'
        unique_together = (('id', 'city_code'),)


class LibLocationCitymun(models.Model):
    city_code = models.CharField(max_length=9)
    city_name = models.CharField(max_length=100)
    prov_code = models.ForeignKey('LibLocationProvinces', models.DO_NOTHING)
    is_urban = models.IntegerField(db_column='is_Urban', blank=True, null=True)  # Field name made lowercase.
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_location_citymun'
        unique_together = (('id', 'city_code'),)


class LibLocationProvinces(models.Model):
    prov_code = models.CharField(max_length=9)
    prov_name = models.CharField(max_length=60)
    region_code = models.ForeignKey('LibLocationRegions', models.DO_NOTHING)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_location_provinces'
        unique_together = (('id', 'prov_code'),)


class LibLocationRegions(models.Model):
    region_code = models.CharField(max_length=9)
    region_name = models.CharField(max_length=60)
    acronym = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_location_regions'
        unique_together = (('id', 'region_code'),)


class LibMedicines(models.Model):
    medicine_name = models.CharField(max_length=100, blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_medicines'


class LibOccupation(models.Model):
    occupation_name = models.CharField(max_length=150, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_occupation'


class LibPriorityLine(models.Model):
    priority_name = models.CharField(max_length=50, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_priority_line'


class LibRelation(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_relation'


class LibServiceProviderProfile(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    acronym = models.CharField(max_length=50, blank=True, null=True)
    contact_number = models.IntegerField(blank=True, null=True)
    updated_by_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_service_provider_profile'


class LibSex(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_sex'


class LibTribe(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_tribe'


class TblClientBeneficiaryInformation(models.Model):
    last_name = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    suffix_id = models.IntegerField(blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    sex_id = models.IntegerField(blank=True, null=True)
    contact_number = models.CharField(max_length=50, blank=True, null=True)
    civil_status_id = models.IntegerField(blank=True, null=True)
    is_indi = models.IntegerField(blank=True, null=True)
    tribu_id = models.IntegerField(blank=True, null=True)
    barangay_id = models.IntegerField(blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    house_no = models.CharField(max_length=255, blank=True, null=True)
    village = models.CharField(max_length=255, blank=True, null=True)
    is_4ps = models.IntegerField(blank=True, null=True)
    number_4ps_id_number = models.CharField(db_column='4ps_id_number', max_length=50, blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    unique_id_number = models.CharField(max_length=50, blank=True, null=True)
    updated_by_id = models.IntegerField(blank=True, null=True)
    is_validated = models.IntegerField(blank=True, null=True)
    registered_by_id = models.IntegerField(blank=True, null=True)
    date_of_registration = models.DateTimeField(blank=True, null=True)
    occupation_id = models.IntegerField(blank=True, null=True)
    salary = models.CharField(max_length=50, blank=True, null=True)
    photo = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_client_beneficiary_information'


class TblClientbeneFamilyRoster(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    suffix_id = models.IntegerField(blank=True, null=True)
    sex_id = models.IntegerField(blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    relation_id = models.IntegerField(blank=True, null=True)
    occupation_id = models.IntegerField(blank=True, null=True)
    salary = models.FloatField(blank=True, null=True)
    clientbene_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_clientbene_family_roster'


class TblFocalServiceProvider(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    service_provider_id = models.IntegerField(blank=True, null=True)
    contact_number = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_focal_service_provider'


class TblMail(models.Model):
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    date_sent = models.DateTimeField(blank=True, null=True)
    received_by_id = models.IntegerField(blank=True, null=True)
    is_read = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_mail'


class TblModeOfAdmission(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    acronym = models.CharField(max_length=255, blank=True, null=True)
    updated_by_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_mode_of_admission'


class TblPurpose(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_purpose'


class TblSubToa(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    acronym = models.CharField(max_length=255, blank=True, null=True)
    updated_by_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    type_of_assistance_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_sub_toa'


class TblSuffix(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_suffix'


class TblTransaction(models.Model):
    tracking_number = models.CharField(max_length=255)
    relation_id = models.IntegerField(blank=True, null=True)
    bene_category_id = models.IntegerField(blank=True, null=True)
    bene_sub_category_id = models.IntegerField(blank=True, null=True)
    problem_presented = models.TextField(blank=True, null=True)
    sw_assessment = models.TextField(blank=True, null=True)
    mode_of_admission_id = models.IntegerField(blank=True, null=True)
    lib_type_of_assistance_id = models.IntegerField(blank=True, null=True)
    lib_assistance_category_id = models.IntegerField(blank=True, null=True)
    fund_source_id = models.IntegerField(blank=True, null=True)
    purpose_id = models.IntegerField(blank=True, null=True)
    date_of_transaction = models.DateTimeField(blank=True, null=True)
    client_id = models.IntegerField(blank=True, null=True)
    bene_id = models.IntegerField(blank=True, null=True)
    swo_id = models.IntegerField(blank=True, null=True)
    is_case_study = models.CharField(max_length=11, blank=True, null=True)
    priority_id = models.IntegerField(blank=True, null=True)
    date_entried = models.DateTimeField(blank=True, null=True)
    is_gl = models.IntegerField(blank=True, null=True)
    is_cv = models.IntegerField(blank=True, null=True)
    is_pcv = models.IntegerField(blank=True, null=True)
    is_return_new = models.IntegerField(blank=True, null=True)
    is_onsite_offsite = models.IntegerField(blank=True, null=True)
    is_online = models.IntegerField(blank=True, null=True)
    is_walkin = models.IntegerField(blank=True, null=True)
    is_referral = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    service_provider_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_transaction'
        unique_together = (('id', 'tracking_number'),)


class TblTransactionProvided(models.Model):
    tracking_number_id = models.CharField(max_length=50, blank=True, null=True)
    provided_id = models.IntegerField(blank=True, null=True)
    medicine_id = models.IntegerField(blank=True, null=True)
    service_provider_id = models.IntegerField(blank=True, null=True)
    regular_price = models.CharField(max_length=100, blank=True, null=True)
    regular_quantity = models.CharField(max_length=100, blank=True, null=True)
    discount_price = models.CharField(max_length=100, blank=True, null=True)
    discount_quantity = models.CharField(max_length=100, blank=True, null=True)
    total = models.CharField(max_length=100, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    is_serve = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_transaction_provided'


class TblTransactionStatus(models.Model):
    transaction_id = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    action = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_transaction_status'


class TblTransactionStatusFiles(models.Model):
    transaction_status_id = models.IntegerField(blank=True, null=True)
    attachment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_transaction_status_files'


class TblUploadAttachFile(models.Model):
    transaction_id = models.IntegerField(blank=True, null=True)
    file = models.TextField(blank=True, null=True)
    file_type_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_uploaded = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_upload_attach_file'


class TblUserSuffix(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    suffix_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_user_suffix'
