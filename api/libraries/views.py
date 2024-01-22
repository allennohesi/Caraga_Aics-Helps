from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.libraries.serializers import CategorySerializer, MOASerializer, MOASSSerializer, ServiceProviderSerializer, \
    SubCategorySerializer, TypeOfAssistanceSerializer, RelationSerializer, SexSerializer, SuffixSerializer, \
    ProvinceSerializer, CitySerializer, BarangaySerializer, TribeSerializer, SignatoriesSerializer, FundSourceSerializer, \
    OccupationSerializer
from app.libraries.models import Category, ModeOfAdmission, ModeOfAssistance, ServiceProvider, SubCategory, \
    TypeOfAssistance, Relation, Sex, Suffix, Province, City, Barangay, Tribe, SignatoriesTbl, FundSource, occupation_tbl

class FundSourceViews(generics.ListAPIView):
    queryset = FundSource .objects.all()
    serializer_class = FundSourceSerializer
    permission_classes = [IsAuthenticated]

class SignatoriesViews(generics.ListAPIView):
    queryset = SignatoriesTbl .objects.all()
    serializer_class = SignatoriesSerializer
    permission_classes = [IsAuthenticated]

class CategoryViews(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class SubCategoryViews(generics.ListAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated]


class MOAViews(generics.ListAPIView):
    queryset = ModeOfAdmission.objects.all()
    serializer_class = MOASerializer
    permission_classes = [IsAuthenticated]


class MOASSViews(generics.ListAPIView):
    queryset = ModeOfAssistance.objects.all()
    serializer_class = MOASSSerializer
    permission_classes = [IsAuthenticated]


class ServiceProviderViews(generics.ListAPIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    permission_classes = [IsAuthenticated]


class TypeOfAssistanceViews(generics.ListAPIView):
    queryset = TypeOfAssistance.objects.all()
    serializer_class = TypeOfAssistanceSerializer
    permission_classes = [IsAuthenticated]


class RelationViews(generics.ListAPIView):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
    permission_classes = [IsAuthenticated]


class SexViews(generics.ListAPIView):
    queryset = Sex.objects.all()
    serializer_class = SexSerializer
    permission_classes = [IsAuthenticated]


class SuffixViews(generics.ListAPIView):
    queryset = Suffix.objects.all()
    serializer_class = SuffixSerializer
    permission_classes = [IsAuthenticated]


class TribeViews(generics.ListAPIView):
    queryset = Tribe.objects.all()
    serializer_class = TribeSerializer
    permission_classes = [IsAuthenticated]


class ProvinceViews(generics.ListAPIView):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    permission_classes = [IsAuthenticated]


class CityViews(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]


class BarangayViews(generics.ListAPIView):
    queryset = Barangay.objects.all()
    serializer_class = BarangaySerializer
    permission_classes = [IsAuthenticated]

class OccupationViews(generics.ListAPIView):
    queryset = occupation_tbl.objects.all().order_by('id')
    serializer_class = OccupationSerializer
    permission_classes = [IsAuthenticated]