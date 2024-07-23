from django.db import models
from django.utils import timezone
from django.db.models import Value, Sum, Count
from django.core.validators import FileExtensionValidator, MaxValueValidator
import uuid, os
from django.dispatch import receiver

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
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey('AuthUser', models.DO_NOTHING)
    date_updated = models.DateTimeField(default=timezone.now)
    fullname = models.CharField(max_length=150)

    @property
    def get_fullname(self):
        from app.libraries.models import UserSuffix

        data = UserSuffix.objects.filter(user_id=self.id).first()
        suffix_name = ""
        if data:
            suffix_name = data.suffix.name

        return "{} {}. {} {}".format(self.first_name, self.middle_name[:1], self.last_name, suffix_name) if self.middle_name else "{} {} {}".format(self.first_name, self.last_name, suffix_name)
    
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
    def get_role(self):
        return AuthUserGroups.objects.filter(user_id=self.id).first().group.name

    @property
    def get_picture(self):
        data = AuthuserProfile.objects.filter(user_id=self.id).first()
        if data:
            return data.profile_pict.url
        return None

    # @property
    # def test(self):
    #     from app.requests.models import Transaction
    #     checking = Transaction.objects.filter(swo_id=self.id).all()
    #     return checking

    class Meta:
        managed = False
        db_table = 'auth_user'



class AuthuserDetails(models.Model):
    from app.libraries.models import Barangay

    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    barangay = models.ForeignKey(Barangay, models.DO_NOTHING, to_field='brgy_code')

    class Meta:
        managed = False
        db_table = 'auth_user_details'
        
def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename_start = filename.replace('.'+ext,'')
    filename = "%s__%s.%s" % (uuid.uuid4(),filename_start, ext)
    return os.path.join('PROFILE_PICTURE', filename)

class AuthuserProfile(models.Model):
    from app.libraries.models import Barangay

    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    profile_pict = models.FileField(
        upload_to=get_file_path,
        verbose_name=(u'File'),
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            MaxValueValidator(1024 * 1024)  # Limiting to 1 MB
        ]
    )

    class Meta:
        managed = False
        db_table = 'auth_user_profile'

@receiver(models.signals.post_delete, sender=AuthuserProfile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.profile_pict:
        if os.path.isfile(instance.profile_pict.path):
            os.remove(instance.profile_pict.path)


class AuthtokenToken(models.Model):
    key = models.CharField(primary_key=True, max_length=40)
    created = models.DateTimeField()
    user = models.OneToOneField(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'authtoken_token'
        
class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    @property
    def count_hmeals(self):
        from app.requests.models import Transaction
        hotmeals = Transaction.objects.annotate(total=Count('provided_hotmeal')).filter(provided_hotmeal=1, swo_id=self.user.id)
        return hotmeals.count()

    @property
    def food_pack(self):
        from app.requests.models import Transaction
        food_pack = Transaction.objects.annotate(total=Count('provided_hotmeal')).filter(provided_foodpack=1, swo_id=self.user.id)
        return food_pack.count()

    @property
    def hygienekit(self):
        from app.requests.models import Transaction
        hygienekit = Transaction.objects.annotate(total=Count('provided_hotmeal')).filter(provided_hygienekit=1, swo_id=self.user.id)
        return hygienekit.count()

    class Meta:
        managed = False
        db_table = 'auth_user_groups'


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)

class AuthFeedback(models.Model):
    subject = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    mood = models.CharField(max_length=255)
    date_created = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_feedback'

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


class SocialaccountSocialaccount(models.Model):
    provider = models.CharField(max_length=30)
    uid = models.CharField(max_length=191)
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    extra_data = models.TextField()
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialaccount'
        unique_together = (('provider', 'uid'),)


class SocialaccountSocialapp(models.Model):
    provider = models.CharField(max_length=30)
    name = models.CharField(max_length=40)
    client_id = models.CharField(max_length=191)
    secret = models.CharField(max_length=191)
    key = models.CharField(max_length=191)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp'


class SocialaccountSocialappSites(models.Model):
    id = models.BigAutoField(primary_key=True)
    socialapp = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING)
    site = models.ForeignKey(DjangoSite, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp_sites'
        unique_together = (('socialapp', 'site'),)


class SocialaccountSocialtoken(models.Model):
    token = models.TextField()
    token_secret = models.TextField()
    expires_at = models.DateTimeField(blank=True, null=True)
    account = models.ForeignKey(SocialaccountSocialaccount, models.DO_NOTHING)
    app = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialtoken'
        unique_together = (('app', 'account'),)



