from rest_framework import serializers

from app.libraries.models import Category, ModeOfAdmission, ModeOfAssistance, ServiceProvider, SubCategory, \
    TypeOfAssistance, Relation, Sex, Province, City, Barangay, Tribe, SignatoriesTbl, FundSource, occupation_tbl


class FundSourceSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(source='updated_by.get_fullname', read_only=True, default=None)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)
    class Meta:
        model = FundSource
        fields = '__all__'

class SignatoriesSerializer(serializers.ModelSerializer):
    signatories = serializers.CharField(source='signatories.get_fullname', read_only=True, default=None)
    class Meta:
        model = SignatoriesTbl
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(source='updated_by.get_fullname', read_only=True, default=None)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(source='updated_by.get_fullname', read_only=True, default=None)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = SubCategory
        fields = '__all__'


class MOASerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(source='updated_by.get_fullname', read_only=True, default=None)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = ModeOfAdmission
        fields = '__all__'


class MOASSSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(source='updated_by.get_fullname', read_only=True, default=None)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = ModeOfAssistance
        fields = '__all__'


class ServiceProviderSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(source='updated_by.get_fullname', read_only=True, default=None)
    focal_person = serializers.CharField(source='get_focal_person', read_only=True, default=None)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = ServiceProvider
        fields = '__all__'


class TypeOfAssistanceSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(source='updated_by.get_fullname', read_only=True, default=None)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = TypeOfAssistance
        fields = '__all__'


class RelationSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(source='updated_by.get_fullname', read_only=True, default=None)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = Relation
        fields = '__all__'


class SexSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(source='updated_by.get_fullname', read_only=True, default=None)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = Sex
        fields = '__all__'


class SuffixSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(source='updated_by.get_fullname', read_only=True, default=None)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = Sex
        fields = '__all__'


class TribeSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(source='updated_by.get_fullname', read_only=True, default=None)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = Tribe
        fields = '__all__'


class ProvinceSerializer(serializers.ModelSerializer):
    region = serializers.CharField(source='region_code.region_name', read_only=True)
    updated_by = serializers.CharField(source='updated_by.get_fullname', read_only=True, default=None)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = Province
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(source='updated_by.get_fullname', read_only=True, default=None)
    province = serializers.CharField(source='prov_code.prov_name', read_only=True)
    region = serializers.CharField(source='prov_code.region_code.region_name', read_only=True)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = City
        fields = '__all__'


class BarangaySerializer(serializers.ModelSerializer):
    city = serializers.CharField(source='city_code.city_name', read_only=True)
    province = serializers.CharField(source='city_code.prov_code.prov_name', read_only=True)
    prov_code = serializers.CharField(source='city_code.prov_code.prov_code', read_only=True)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = Barangay
        fields = '__all__'

class OccupationSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(source='user.get_fullname', read_only=True, default=None)

    class Meta:
        model = occupation_tbl
        fields = '__all__'