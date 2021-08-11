from accounts.models import DeliveryPartnerProfile, Store
from admin_section.models import DeliveryPartnerApproval, RestaurantApproval
from admin_section.serializers import DeliveryPartnerApprovalSerializer, RestaurantApprovalSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
# Create your views here.


class RestaurantApprovalView(APIView):

    def get(self, request, format=None):
        snippets = RestaurantApproval.objects.all()
        serializer = RestaurantApprovalSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        store_id = request.data.get("store_id")
        if store_id is None:
            return Response({"store_id is required"}, status=status.HTTP_200_OK)
        restaurant = RestaurantApproval.objects.get(store_id=store_id)
        store = Store.objects.get(store_id=store_id)
        restaurant.approved = True
        store.approved = True
        restaurant.save()
        store.save()
        return Response({"Approved"}, status=status.HTTP_200_OK)


class DeliveryPartnerApprovalView(APIView):

    def get(self, request, format=None):
        snippets = DeliveryPartnerApproval.objects.all()
        serializer = DeliveryPartnerApprovalSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        userId = request.data.get("user")
        if userId is None:
            return Response({"userId is required"}, status=status.HTTP_200_OK)
        partner = DeliveryPartnerApproval.objects.get(userId=userId)
        profile = DeliveryPartnerProfile.objects.get(userId=userId)
        partner.approved = True
        profile.approved = True
        partner.save()
        profile.save()
        return Response({"Approved"}, status=status.HTTP_200_OK)
