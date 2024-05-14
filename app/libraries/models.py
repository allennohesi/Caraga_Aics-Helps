from django.db import models
from django.utils import timezone
from app.models import AuthUser
import os, uuid

def get_signatories_file(instance, filename):
    ext = filename.split('.')[-1]
    filename_start = filename.replace('.'+ext,'')
    filename = "%s__%s.%s" % (uuid.uuid4(),filename_start, ext)
    return os.path.join('signatories', filename)

class SignatoriesTbl(models.Model):
    signatories = models.ForeignKey(AuthUser, models.DO_NOTHING)
    signature_file = models.FileField(upload_to=get_signatories_file,verbose_name=(u'File'))
    status = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_signatories'


class Category(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    acronym = models.CharField(max_length=50, blank=True, null=True)
    updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    status = models.BooleanField(blank=True, null=True)
    date_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'lib_category_sector'


class ModeOfAdmission(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    acronym = models.CharField(max_length=50, blank=True, null=True)
    updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    status = models.BooleanField(blank=True, null=True)
    date_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'tbl_mode_of_admission'


class ModeOfAssistance(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    acronym = models.CharField(max_length=50, blank=True, null=True)
    updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    status = models.BooleanField(blank=True, null=True)
    date_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'tbl_mode_of_assistance'



class ServiceProvider(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    acronym = models.CharField(max_length=50, blank=True, null=True)
    contact_number=models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    status = models.BooleanField(blank=True, null=True)
    date_updated = models.DateTimeField(default=timezone.now)
    category = models.CharField(max_length=255, blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'lib_service_provider_profile'


class FocalServiceProvider(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    status = models.BooleanField(blank=True, null=True)
    service_provider = models.ForeignKey('ServiceProvider', models.DO_NOTHING)
    contact_number = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_focal_service_provider'


class SubCategory(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    acronym = models.CharField(max_length=50, blank=True, null=True)
    updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    status = models.BooleanField(blank=True, null=True)
    date_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'lib_category_sub'


class CivilStatus(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    status = models.BooleanField(blank=True, null=True)
    date_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'lib_civil_status'

class LibAssistanceType(models.Model):
    type_name = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    is_active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_assistance_type'

class TypeOfAssistance(models.Model):
    type_assistance = models.ForeignKey(LibAssistanceType, models.DO_NOTHING)
    name = models.CharField(max_length=255, blank=True, null=True)
    acronym = models.CharField(max_length=50, blank=True, null=True)
    updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    status = models.BooleanField(blank=True, null=True)
    date_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'lib_assistance_category'

class SubModeofAssistance(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    acronym = models.CharField(max_length=50, blank=True, null=True)
    updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    status = models.BooleanField(blank=True, null=True)
    date_updated = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(ModeOfAssistance, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'lib_assistance_sub_category'


class AssistanceProvided(models.Model):
    provided_name = models.CharField(max_length=255, blank=True, null=True)
    assistance_sub_type = models.ForeignKey(SubModeofAssistance, models.DO_NOTHING)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_assistance_provided'

class Relation(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    status = models.BooleanField(blank=True, null=True)
    date_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'lib_relation'


class Sex(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    status = models.BooleanField(blank=True, null=True)
    date_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'lib_sex'


class Suffix(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    status = models.BooleanField(blank=True, null=True)
    date_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'tbl_suffix'


class Tribe(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    status = models.BooleanField(blank=True, null=True)
    date_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'lib_tribe'


class UserSuffix(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    suffix = models.ForeignKey('Suffix', models.DO_NOTHING)

    class Meta:
        db_table = 'tbl_user_suffix'


class region(models.Model):
    region_code = models.CharField(max_length=64, unique=True)
    region_name = models.CharField(max_length=64, unique=True)
    acronym = models.CharField(max_length=64, unique=True)
    is_active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'lib_location_regions'


class Province(models.Model):
    prov_name = models.CharField(max_length=64, unique=True)
    prov_code = models.CharField(max_length=64, unique=True)
    region_code = models.ForeignKey(region, models.DO_NOTHING, to_field='region_code')
    is_active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'lib_location_provinces'


class City(models.Model):
    city_name = models.CharField(max_length=64, unique=True)
    city_code = models.CharField(max_length=24, unique=True)
    prov_code = models.ForeignKey(Province, models.DO_NOTHING, to_field='prov_code')
    is_active = models.IntegerField()
    is_urban = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'lib_location_citymun'


class Barangay(models.Model):
    brgy_name = models.CharField(max_length=128)
    city_code = models.ForeignKey(City, models.DO_NOTHING, to_field='city_code')
    brgy_code = models.CharField(max_length=64, unique=True)
    is_active = models.IntegerField()
    urb_rur = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'lib_location_brgy'


class FileType(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.ForeignKey('AuthUser', models.DO_NOTHING)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(default=timezone.now)
    is_required = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_file_type'


class ServiceAssistance(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.ForeignKey('AuthUser', models.DO_NOTHING)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    is_specify = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_service_assistance'


class Purpose(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.ForeignKey('AuthUser', models.DO_NOTHING)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_purpose'


class FundSource(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.ForeignKey('AuthUser', models.DO_NOTHING)
    status = models.IntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_fund_source'

class PriorityLine(models.Model):
    priority_name = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_priority_line'


class medicine(models.Model):
    medicine_name = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_medicines'

class occupation_tbl(models.Model):
    occupation_name = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_occupation'

class presented_id(models.Model):
    created = models.ForeignKey('AuthUser', models.DO_NOTHING)
    presented = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_presented_id'
