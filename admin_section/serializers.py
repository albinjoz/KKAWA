
from admin_section.models import RestaurantApproval,DeliveryPartnerApproval
from rest_framework import exceptions, serializers



class RestaurantApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantApproval
        fields = "__all__"

class DeliveryPartnerApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPartnerApproval
        fields = "__all__"