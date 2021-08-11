
from django.contrib.auth import authenticate
from django.http.response import HttpResponse
from rest_framework import exceptions, serializers, status

import random
import string
from accounts.models import *

#create serializer

#user creation, resturant creation delivery creations via Phone otp
class RegisterviaPhoneSerializer(serializers.ModelSerializer):

    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    username = serializers.CharField(source = 'phone')
    
    class Meta:
        model = CustomUser
        fields = ('email','name', 'username', 'password', 'password2',)

    def create(self, validated_data):
        
        user = CustomUser(
            name=validated_data['name'],
            email=validated_data['email'],
            username=validated_data['phone'])
        
        password = validated_data['password']
        password2 = validated_data['password2']
        if password == password2:
            user.set_password(validated_data['password'])
            # user.is_active = False
            
        rr = 'KKAWA'
        S = 4
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=S))
        result = ''.join(rr + ran)
        
        user.user_id = result
        user.save()
        return user
                  

    def validate_password(self, data):
        if data.isalnum():
            raise serializers.ValidationError('password must have atleast one special character.')
        return data


#******************************************************************************************************************


""" Register via email serializer"""
class RegisterViaEmailSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    username = serializers.CharField(source = 'email')
    
    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'password', 'password2')

    def create(self, validated_data):
        user = CustomUser(
            name=validated_data['name'],
            username=validated_data['email'])
        
        print("usernameeeeeeeeeeeeeee",user)
        password = validated_data['password']
        password2 = validated_data['password2']
        if password == password2:
            user.set_password(validated_data['password'])
            
        rr = 'KKAWA'
        S = 4
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=S))
        result = ''.join(rr + ran)

        user.user_id = result
        user.save()
        return user

    def validate_password(self, data):
        if data.isalnum():
            raise serializers.ValidationError('password must have atleast one special character.')
        return data




#*****************************************************************************************************************

"""OTP Verify serializer"""


class OTPserializer(serializers.ModelSerializer):
    class Meta:
        model = verify
        fields = ('__all__')

#*****************************************************************


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers .CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        obj = CustomUser.objects.get(username=username)
        print("*********",obj)
        
        if obj.is_phone_verified == False:
            user = authenticate(username=username, password=password)
            print(user)
        
            if user:
                data['user'] = user
            else:
                msg = 'login failed'
                raise exceptions.ValidationError(msg)
                
        return data

#*********************************************************************************************************8


class UpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'phone')

#********************************************************************


class ForgetPasswordSerializer(serializers.Serializer):

    phone = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

#***********************************************************************************************************

class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = "__all__"


class StoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Store
        # fields = "__all__"
        exclude = ('gallery', )


class Restaurant_earningSerializer(serializers.ModelSerializer):

    class Meta:
        model = Restaurant_earning
        fields = "__all__"


class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Item_category
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        # fields = "__all__"
        exclude = ('image', )

class CartSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Cart
        fields = "__all__"


class WishlistSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Wishlist
        fields = "__all__"
        # exclude = ('user', )


class OrderSerializer(serializers.ModelSerializer):
    totalAmount = serializers.ReadOnlyField()
    class Meta:
        model = Order
        # fields = "user","items","totalAmount","couponEnabled","couponDetails",
        # "paymentMethods","paymentStatus","storeDetails","deliveryStatus","confirmToken"
        
        fields = "__all__"


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"
        # exclude = ('orderId', )


class DeliveryPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPartnerProfile
        fields = "__all__"
        # exclude = ('user', )


class CustomerSupportSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerSupport
        # fields = "__all__"
        exclude = ('token', )


class CustomerItemviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = "itemName", "price", "itemStore", "image"



class GallerySerializer(serializers.ModelSerializer):

    class Meta:
        model = Gallery
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = "__all__"


class ChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat    
        fields = "__all__"

class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = TicketGenerate    
        fields = "__all__"



# class RazorpaySerializer(serializers.ModelSerializer):

#     class Meta:
#         model = RazorpayModel
#         fields = "__all__"




