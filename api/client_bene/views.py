from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.client_bene.serializers import ClientBeneficiarySerializer
from app.requests.models import ClientBeneficiary


class ClientBeneficiaryViews(generics.ListAPIView):
    queryset = ClientBeneficiary.objects.all()
    serializer_class = ClientBeneficiarySerializer
    permission_classes = [IsAuthenticated]

class AdvanceFilterViews(generics.ListAPIView):
    serializer_class = ClientBeneficiarySerializer
    permission_classes = [IsAuthenticated]
    #__startswith
    def get_queryset(self):
        if self.request.query_params.get('fname') and self.request.query_params.get('lname') and self.request.query_params.get('bday'):
            queryset = ClientBeneficiary.objects.filter(last_name=self.request.query_params.get('lname'),
                                              first_name=self.request.query_params.get('fname'),
                                              birthdate=self.request.query_params.get('bday'),
                                              )
            return queryset
