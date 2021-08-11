import django_filters
from accounts.utils import Util
from django.http.response import HttpResponse
from django.db.models import Avg


from admin_section.models import DeliveryPartnerApproval, RestaurantApproval
from django.contrib.auth import login as djangologin
from django.contrib.auth import logout as djangologout
from django.contrib.sites.shortcuts import get_current_site

from django.http import Http404
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend

from kkawa import settings
from rest_framework.parsers import JSONParser
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import  AllowAny
from rest_framework.decorators import api_view,permission_classes

from accounts.models import *
from accounts.serializers import *
from accounts.sms import generate_otp, send_sms

import json
from django.shortcuts import render
import razorpay
from django.views.decorators.csrf import csrf_exempt
from uuid import uuid4
from django.shortcuts import get_object_or_404
# Create your views here.


# signing by social 
def social_reg(request):
      
    # render function takes argument  - request
    # and return HTML as response
    return render(request, "index.html")

# **********************END********************************

def home(request):
    if request.method == "POST":
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        paymenyId = request.POST.get('paymenyId')

        client = razorpay.Client(
            auth=("rzp_test_EeBEcAb99QUJDc ", "zIRD5SEv9yCtboBJF7R5p266"))
        client.order.create({'amount': amount, 'currency': 'INR','name': name,'paymenyId': paymenyId})

    return render(request, 'raz_index.html')
    # return HttpResponse("SUCCESS", status= status.HTTP_200_OK)  


@csrf_exempt
def success(request):
    return render(request, "success.html")

# **********************END*************************************************************************************

# CUSTOMER Register (Phone otp)

class CustomerRegisterView(APIView):

    def get(self, request, format=None):
        user = CustomUser.objects.filter(is_customer=True)
        serializer = RegisterviaPhoneSerializer(user, many=True)
        reply = {}
        reply['data'] = serializer.data
        return HttpResponse(reply, status= status.HTTP_200_OK)

    def post(self, request):
        serializer = RegisterviaPhoneSerializer(data=request.data)
        reply = {}
        try:
            if serializer.is_valid():
                usr_phn = serializer.validated_data['phone']
                serializer.save(username = usr_phn)
                random_otp = generate_otp()
                # msg_body = f''' Your One Time Password for verification  is {random_otp} .Thank you for registering with !KKAWA Food Delivery. Do not disclose the OTP to anyone.'''
                # send_sms(settings.account_sid, settings.auth_token,
                #         msg_body, '7034454905', usr_phn)

                v = verify(phone=usr_phn, ph_otp=random_otp, status=False)
                count = v.count
                v.count = count+1
                v.save()

                reply['Status'] = "Success"
                reply['message'] = "Please check the OTP sent"
                reply['Data'] = serializer.data
                return Response(reply,status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(serializer.errors)
            print(str(e))
            reply['message'] = "User registration failed"
            reply['data'] = serializer.errors
            return Response(reply, status=status.HTTP_400_BAD_REQUEST)


#customer vi email

class CustomerRegisterViaEmail(APIView):
    
    def get(self, request, format=None):
        user = CustomUser.objects.all()
        serializer = RegisterViaEmailSerializer(user, many=True)
        return Response(serializer.data,status= status.HTTP_200_OK)

    def post(self, request):
        serializer = RegisterViaEmailSerializer(data=request.data)
        reply = {}
        try:

            if serializer.is_valid(raise_exception=True):
                email = serializer.validated_data['email']
                serializer.save()
                user = CustomUser.objects.get(username=email)
                # print("uuuuuuuuuuuuusssssssssssseeeerrrr", user)
                random_otp = generate_otp()
                current_site = get_current_site(request)
                
                email_subject = 'OTP',
                {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(email)),
                }
                email_body = f''' Your One Time Password for verification  is {random_otp} .Thank you for registering with !KKAWA Food Delivery. Do not disclose the OTP to anyone.'''
                ' Use the link below to verify your email \n'
                data = {'email_body': email_body, 'to_email': user.email,
                        'email_subject': 'Verify your email'}

                Util.send_email(data)
                v = verify(email=email,ph_otp=random_otp, status=False)
                count = v.count
                v.count = count+1
                v.save()
                
                reply['status'] = "success"
                reply['message'] = "Please check the OTP sent"
                reply['data'] = serializer.data
                
                return Response(reply, status=status.HTTP_201_CREATED)
        except Exception as e:
            # print(e)
            # print(serializer.errors)
            return Response({
            "message": "User registration failed",
            "data": serializer.data
            }, status=status.HTTP_400_BAD_REQUEST)

# **********************END*****************************************************************************************


# RESTAURANT Register (Phone otp)

class RestaurantRegisterView(APIView):
    
    def get(self, request, format=None):
        user = CustomUser.objects.filter(is_restaurant=True)
        serializer = RegisterviaPhoneSerializer(user, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RegisterviaPhoneSerializer(data=request.data)
        reply = {}
        if serializer.is_valid():
            usr_phn = serializer.validated_data['phone']
            serializer.save()
            random_otp = generate_otp()
            # msg_body = f''' Your One Time Password for verification  is {random_otp} .Thank you for registering with !KKAWA Food Delivery. Do not disclose the OTP to anyone.'''
            # send_sms(settings.account_sid, settings.auth_token,
            #          msg_body, '+18326647867', usr_phn)
            v = verify(phone=usr_phn, ph_otp=random_otp, status=False)
            count = v.count
            v.count = count+1
            v.save()
            
            reply['Status'] = "Success"
            reply['message'] = "Please check the OTP sent"
            reply['Data'] = serializer.data
            return Response(reply, status=status.HTTP_201_CREATED)

        reply['Status'] = "failed"
        reply['message'] = "User registration failed"
        reply['errorcode'] = serializer.errors
        reply['Data'] = serializer.data
        return Response(reply, status=status.HTTP_400_BAD_REQUEST)



#resturant vi email
class RestaurantRegisterViaEmail(APIView):
    
    def get(self, request, format=None):
        user = CustomUser.objects.all()
        serializer = RegisterViaEmailSerializer(user, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RegisterViaEmailSerializer(data=request.data)
        reply = {}
        try:

            if serializer.is_valid(raise_exception=True):
                email = serializer.validated_data['email']
                serializer.save()
                user = CustomUser.objects.get(username=email)
                # print("uuuuuuuuuuuuusssssssssssseeeerrrr", user)
                random_otp = generate_otp()
                current_site = get_current_site(request)
                
                email_subject = 'OTP',
                {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(email)),
                }
                email_body = f''' Your One Time Password for verification  is {random_otp} .Thank you for registering with !KKAWA Food Delivery. Do not disclose the OTP to anyone.'''
                ' Use the link below to verify your email \n'
                data = {'email_body': email_body, 'to_email': user.email,
                        'email_subject': 'Verify your email'}

                Util.send_email(data)
                v = verify(email=email,ph_otp=random_otp, status=False)
                count = v.count
                v.count = count+1
                v.save()
                
                reply['status'] = "success"
                reply['message'] = "Please check the OTP sent"
                reply['data'] = serializer.data
                
                return Response(reply, status=status.HTTP_201_CREATED)
        except Exception as e:
            # print(e)

            reply['status'] = "error"
            reply['message'] = "registration is failed. please try again "
            reply['error'] = serializer.errors
            return Response(reply, status=status.HTTP_400_BAD_REQUEST)


# **********************END******************************************************************************************



# DELIVERY Register (Phone otp)
class DeliveryRegisterView(APIView):
    
    def get(self, request, format=None):
        user = CustomUser.objects.filter(is_delivery=True)
        serializer = RegisterviaPhoneSerializer(user, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = RegisterviaPhoneSerializer(data=request.data)
        reply = {}
        if serializer.is_valid():
            usr_phn = serializer.validated_data['phone']
            serializer.save()
            random_otp = generate_otp()
            # msg_body = f''' Your One Time Password for verification  is {random_otp} .Thank you for registering with !KKAWA Food Delivery. Do not disclose the OTP to anyone.'''
            # send_sms(settings.account_sid, settings.auth_token,
            #          msg_body, '+18326647867', usr_phn)
            v = verify(phone=usr_phn, ph_otp=random_otp, status=False)
            count = v.count
            v.count = count+1
            v.save()
            
            reply['Status'] = "Success"
            reply['message'] = "Please check the OTP sent"
            reply['Data'] = serializer.data
            return Response(reply, status=status.HTTP_201_CREATED)

        reply['Status'] = "failed"
        reply['message'] = "User registration failed"
        reply['errorcode'] = serializer.errors
        reply['Data'] = serializer.data
        return Response(reply, status=status.HTTP_400_BAD_REQUEST)


#delivery register vi email
class DeliveryRegisterViaEmail(APIView):

    def get(self, request, format=None):
        user = CustomUser.objects.all()
        serializer = RegisterViaEmailSerializer(user, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RegisterViaEmailSerializer(data=request.data)
        reply = {}
        try:
            if serializer.is_valid():
                email = serializer.validated_data['email']
                serializer.save()
                user = CustomUser.objects.get(username=email)
                random_otp = generate_otp()
                current_site = get_current_site(request)
                email_subject = 'OTP',
                {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(email)),
                }
                email_body = f''' Your One Time Password for verification  is {random_otp} .Thank you for registering with !KKAWA Food Delivery. Do not disclose the OTP to anyone.'''
                ' Use the link below to verify your email \n'
                data = {'email_body': email_body, 'to_email': user.email,
                        'email_subject': 'Verify your email'}

                Util.send_email(data)
                v = verify(email=email, ph_otp=random_otp, status=False)
                count = v.count
                v.count = count+1
                v.save()
                print(serializer.data)
                reply['status'] = "success"
                reply['message'] = "Please check the OTP sent"
                reply['data'] = serializer.data
                return Response(reply, status=status.HTTP_201_CREATED)
        except Exception as e:
            # print(str(e))
            # print(serializer.errors)
            
            reply['message'] = "User registration failed"
            reply['data'] = serializer.data
            return Response(reply, status=status.HTTP_400_BAD_REQUEST)


# **********************END*********************************************************************************************

# OTP verification

class verifyOTPView(APIView):

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        otp_sent = request.data.get('ph_otp', False)
        if phone and otp_sent:
            old = verify.objects.filter(phone__iexact=phone)
            if old.exists():
                old = old.last()
                ph_otp = old.ph_otp
                user = CustomUser.objects.get(phone=phone)
                if str(otp_sent) == str(ph_otp):
                    # user ecomes active before function.
                    user.is_active = True
                    user.is_phone_verified = True
                    user.save()
                    old.status = True
                    old.save()
                    return Response({
                        'status': True,
                        'detail': 'OTP matched. Please proceed for registration.'
                    })
                else:
                    return Response({
                        'status': False,
                        'detail': 'OTP incorrect.'
                    })
            else:
                return Response({
                    'status': False,
                    'detail': 'First proceed via sending otp request.'
                })
        else:
            return Response({
                'status': False,
                'detail': 'Please provide both phone and otp for validations'
            })

# **********************END********************************

# Resend OTP
class ResendOTP(APIView):

    def post(self, request):
        usr_phn = request.POST.get('phone')
        v = verify.objects.get(phone=usr_phn)
        random_otp = generate_otp()
        msg_body = f''' Your One Time Password {random_otp} for verification.Thank you for registering with !KKAWA Food Delivery. Do not disclose the OTP to anyone.'''
        v.ph_otp = random_otp
        count = v.count
        v.count = count+1
        v.save()
        if v.count < 4:
            send_sms(settings.account_sid, settings.auth_token,
                     msg_body, '+18326647867', usr_phn)
            return Response(
                {
                    "message": "Please check the OTP sent"
                }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "User registration failed"
            }, status=status.HTTP_400_BAD_REQUEST)



# **********************END************************************************************************************
class Login(APIView):

    def post(self, request):
      
        serializer = LoginSerializer(data=request.data)
        reply = {}

        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            # print("****************************username",user)
            djangologin(request, user)
            
            token, created = Token.objects.get_or_create(user=user)
            request.session['token'] = token.key
            request.session['userid'] = user.id
    
            
            reply['status'] = "success"
            reply['message'] = 'You have successfully Logged in.'
            reply['user'] = user.id
            reply['token'] = token.key
            dict_obj = json.dumps(reply)
            return HttpResponse(dict_obj,status=status.HTTP_200_OK)
        
        else:
            reply['status'] = "failed"
            reply['message'] = "user not found"
            dict_obj = json.dumps(reply)
            print(str(serializer.errors))
            return HttpResponse(dict_obj, status= status.HTTP_400_BAD_REQUEST)


class Logout(APIView):

    def post(self, request):
        djangologout(request)
        return Response(
            {
                'message': 'You have Logged out successfully.'
            },
            status=status.status.HTTP_204_NO_CONTENT)


# **********************END*********************************************************************************

class ForgetPasswordView(APIView):

    def post(self, request, *args, **kwargs):
        query = CustomUser.objects.all()
        serializer = ForgetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            usr_phn = serializer.validated_data['phone']
            user = CustomUser.objects.filter(phone=usr_phn)
            print(user)
            if user:
                random_otp = generate_otp()
                msg_body = f''' Your One Time Password {random_otp} for verification.Thank you for registering with !KKAWA Food Delivery. Do not disclose the OTP to anyone.'''
                send_sms(settings.account_sid, settings.auth_token,
                         msg_body, '+18326647867', usr_phn)
                return Response({"message": "Please check the OTP sent"}, status=200)
        return Response({"message": "User does not exists"}, status=400)


# **********************END********************************


class ForgetPasswordOTPVerify(APIView):

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        otp_sent = request.data.get('ph_otp', False)
        if phone and otp_sent:
            old = verify.objects.filter(phone__iexact=phone)
            print("inside")
            if old.exists():
                old = old.last()
                ph_otp = old.ph_otp
                print(ph_otp)
                user = CustomUser.objects.get(phone=phone)
                print(user)
                if str(otp_sent) == str(ph_otp):
                    return Response({
                        'status': True,
                        'detail': 'OTP matched. Please proceed to change your password.'
                    })
                else:
                    return Response({
                        'status': False,
                        'detail': 'OTP incorrect.'
                    })
            else:
                return Response({
                    'status': False,
                    'detail': 'First proceed via sending otp request.'
                })
        else:
            return Response({
                'status': False,
                'detail': 'Please provide both phone and otp for validations'
            })

# **********************END***************************************************************************************


class PasswordChangeView(generics.UpdateAPIView):

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):

        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if serializer.data.get('new_password') == serializer.data.get('new_password2'):
                if not self.object.check_password(serializer.data.get('old_password')):
                    return Response({
                        'status': False,
                        'current_password': 'Does not match with our data',
                    }, status=status.HTTP_400_BAD_REQUEST)
                self.object.set_password(serializer.data.get('new_password'))
                self.object.password_changed = True
                self.object.save()
                return Response({
                    "status": True,
                    "detail": "Password has been successfully changed.",
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# **********************END**********************************************************************************************


#check user vi email

@api_view(['GET'])
@permission_classes([AllowAny])
def checkUser(request):
    reply = {}
    email = request.GET.get("email")
    user = CustomUser.objects.filter(username=email)
    
    if user :
        for li in user:
            reply['name'] = li.name
            reply['user_id'] = li.user_id
            reply['email'] = li.email
            reply['phone'] = li.phone
            dict_obj = json.dumps(reply)
        return HttpResponse(dict_obj, status= status.HTTP_200_OK)
    else:
        reply['message'] = "user not found"
        dict_obj = json.dumps(reply)
        return HttpResponse(dict_obj, status=status.HTTP_404_NOT_FOUND)



#checkuser vi id

@api_view(['GET'])
@permission_classes([AllowAny])
def checkUserId(request):
    reply = {}
    user_id = request.GET.get('user_id')
    user = CustomUser.objects.filter(user_id=user_id)
    
    if user is not None:
        for li in user:
            reply['name'] = li.name
            reply['user_id'] = li.user_id
            reply['email'] = li.email
            reply['phone'] = li.phone
            dict_obj = json.dumps(reply)
            return HttpResponse(dict_obj, status= status.HTTP_200_OK)
    else:
        reply['message'] = "user not found"
        dict_obj = json.dumps(reply)
        return HttpResponse(dict_obj, status=status.HTTP_404_NOT_FOUND)


# **********************END****************************************************************************

#user, store , delivery boy update and delete

class UserDetails(APIView):
    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404
    
    def patch(self, request, pk):
        instance = self.get_object(pk)

        # set partial=True to update a data partially
        serializer = UpdateSerializers(instance, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            reply = {}
            reply['Status'] = "Success"
            reply['Message'] = "Updated Successfully"
            reply['Data'] = serializer.data
            return Response(reply, status = status.HTTP_201_CREATED)
        return Response(data="Bad Request", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# **********************END****************************************************************************


class AddressView(APIView):

    def get(self, request, format=None):
        snippets = Address.objects.all()
        serializer = AddressSerializer(snippets, many=True)
        reply = {}
        reply['status'] = "success"
        reply['Data'] = serializer.data
        return HttpResponse(reply, status= status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = AddressSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            reply ={}
            reply['status'] = "success"
            reply['Data'] = serializer.data
            dict_obj = json.dumps(reply)
            return HttpResponse(dict_obj, status=status.HTTP_201_CREATED)
        return HttpResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AddressDetails(APIView):
    def get_object(self, pk):
        try:
            return Address.objects.get(pk=pk)
        except Address.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = AddressSerializer(snippet)
        reply ={}
        reply['status'] = "success"
        reply['Data'] = serializer.data
        return Response(reply,status =status.HTTP_200_OK)

    
    def patch(self, request, pk):
        instance = self.get_object(pk)

        # set partial=True to update a data partially
        serializer = AddressSerializer(instance, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            reply = {}
            reply['Status'] = "Success"
            reply['Message'] = "Updated Successfully"
            reply['Data'] = serializer.data
            # return Response(serializer.data, status = status.HTTP_201_CREATED)
            return Response(reply, status = status.HTTP_201_CREATED)
        return Response(data="Bad Request", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

  #**************************************************************************************************************

#adding store
class StoreView(APIView):

    def get(self, request, format=None):
        snippets = Store.objects.all()
        serializer = StoreSerializer(snippets, many=True)
        reply = {}
        reply['status'] = "success"
        reply['Data'] = serializer.data
        return Response(reply, status= status.HTTP_200_OK)

    def post(self, request, format=None):
        
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            store_id = serializer.validated_data["store_id"]
            print(store_id)
            name = serializer.validated_data["name"]
            # gallery = serializer.validated_data["gallery"]
            pincode = serializer.validated_data["pincode"]
            certificate_or_license = serializer.validated_data["certificate_or_license"]
            address = serializer.validated_data["address"]
            store_charge = serializer.validated_data["store_charge"]
            store_manager_name = serializer.validated_data["store_manager_name"]
            store_manager_email = serializer.validated_data["store_manager_email"]
            store_manager_phone = serializer.validated_data["store_manager_phone"]
            approved = serializer.validated_data["approved"]

            if approved == True:
                approval_request = RestaurantApproval(store_id=store_id, name=name,  pincode=pincode,
                                                    certificate_or_license=certificate_or_license,address= address, store_charge=store_charge,
                                                    store_manager_name=store_manager_name, store_manager_email=store_manager_email,
                                                    store_manager_phone=store_manager_phone, approved=approved)
                approval_request.save()
            reply ={}
            reply['status'] = "success"
            reply['Data'] = serializer.data
            return Response(reply, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoreDetail(APIView):

    def get_object(self, pk):
        try:
            return Store.objects.get(pk=pk)
        except Store.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = StoreSerializer(snippet)
        reply ={}
        reply['status'] = "success"
        reply['Data'] = serializer.data
        return Response(reply,status =status.HTTP_200_OK)

    
    def patch(self, request, pk):
        instance = self.get_object(pk)

        # set partial=True to update a data partially
        serializer = StoreSerializer(instance, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            reply = {}
            reply['Status'] = "Success"
            reply['Message'] = "Updated Successfully"
            reply['Data'] = serializer.data
            # return Response(serializer.data, status = status.HTTP_201_CREATED)
            return Response(reply, status = status.HTTP_201_CREATED)
        return Response(data="Bad Request", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# **********************END*******************************************************************************


@api_view(['GET'])
@permission_classes([AllowAny])

def StoreSearch(request):
    reply = {}
    name = request.GET.get("store")
    resturant = Store.objects.filter(name = name)
    
    if resturant is not None:
        for li in resturant:
            reply['Resturant Name'] = li.name
            reply['Description'] = li.description
            reply['Images'] = str(li.gallery)
            reply['Resturant phone'] = li.phone
            reply['Address'] = li.address
            reply['Pincode'] = li.pincode
            reply['Landmark'] = li.landmark
            reply['Delivery Radius'] = li.delivery_radius
            reply['StoreManager name'] = li.store_manager_name
            reply['StoreManager email'] = li.store_manager_email
            reply['StoreManagerphone'] = li.store_manager_phone
            
        dict_obj = json.dumps(reply)
        return HttpResponse(dict_obj, status= status.HTTP_200_OK)

    else:
        reply['message'] = "Resturant not found"
        dict_obj = json.dumps(reply)
        return HttpResponse(dict_obj,status = status.HTTP_404_NOT_FOUND)

    







class Restaurant_earningsView(APIView):

    def get(self, request, format=None):
        snippets = Restaurant_earning.objects.all()
        serializer = Restaurant_earningSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = Restaurant_earningSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            reply ={}
            reply['status'] = "success"
            reply['Data'] = serializer.data
            return Response(reply, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Restaurant_earningsDetail(APIView):

    def get_object(self, pk):
        try:
            return Restaurant_earning.objects.get(pk=pk)
        except Restaurant_earning.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = Restaurant_earningSerializer(snippet)
        reply ={}
        reply['status'] = "success"
        reply['Data'] = serializer.data
        return Response(reply,status = status.HTTP_200_OK)

    def patch(self, request, pk):
        instance = self.get_object(pk)

        # set partial=True to update a data partially
        serializer = Restaurant_earningSerializer(instance, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            reply = {}
            reply['Status'] = "Success"
            reply['Message'] = "Updated Successfully"
            reply['Data'] = serializer.data
            # return Response(serializer.data, status = status.HTTP_201_CREATED)
            return Response(reply, status = status.HTTP_201_CREATED)
        return Response(data="Bad Request", status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# **********************END********************************************************************************


class ItemCategoryView(APIView):

    def get(self, request, format=None):
        snippets = Item_category.objects.all()
        serializer = ItemCategorySerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ItemCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            reply ={}
            reply['status'] = "success"
            reply['Data'] = serializer.data
            return Response(reply, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemCategoryDetail(APIView):

    def get_object(self, pk):
        try:
            return Item_category.objects.get(pk=pk)
        except Item_category.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = ItemCategorySerializer(snippet)
        reply ={}
        reply['status'] = "success"
        reply['Data'] = serializer.data
        return Response(reply, status =status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = ItemCategorySerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk):
        instance = self.get_object(pk)

        # set partial=True to update a data partially
        serializer = ItemCategorySerializer(instance, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            reply = {}
            reply['Status'] = "Success"
            reply['Message'] = "Updated Successfully"
            reply['Data'] = serializer.data
            # return Response(serializer.data, status = status.HTTP_201_CREATED)
            return Response(reply, status = status.HTTP_201_CREATED)
        return Response(data="Bad Request", status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# **********************END**********************************************************************************


@api_view(['GET'])
@permission_classes([AllowAny])
def checkItems(request):
    reply = {}
    item_name = request.GET.get("items")
    items = Item.objects.filter(item_name=item_name)

    if items is not None:
        for li in items:
            
            reply['name'] = li.item_name
            reply['description'] = li.description
            reply['price'] = float(li.price)
            reply['item_store'] = str(li.itemStore) 
            reply['Item_category'] = str(li.ItemCategory)
            reply['image'] = str(li.image)
            reply['discount'] = float(li.discount)
            reply['tax'] = float(li.tax)
            
        dict_obj = json.dumps(reply)
        return HttpResponse(dict_obj, status= status.HTTP_200_OK)
    
    else:
        reply['message'] = "Item not found"
        reply['status'] = "error"
        dict_obj = json.dumps(reply)
        return HttpResponse(dict_obj,status = status.HTTP_404_NOT_FOUND)


class ItemView(APIView):

    def get(self, request, format=None):
        snippets = Item.objects.all()
        serializer = ItemSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ItemSerializer(data=request.data)
        
        
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                
                reply ={}
                reply['status'] = "success"
                reply['Data'] = serializer.data
                return Response(reply, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            print(str(e))
            reply ={}
            reply['status'] = "error"
            reply['error'] = serializer.errors
            return Response(reply, status=status.HTTP_400_BAD_REQUEST)


class ItemDetail(APIView):

    def get_object(self, pk):
        try:
            return Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = ItemSerializer(snippet)

        reply ={}
        reply['status'] = "success"
        reply['message'] = "items added to cart"
        reply['Data'] = serializer.data
        return Response(reply,status=status.HTTP_200_OK)


    def patch(self, request, pk):
        instance = self.get_object(pk)

        # set partial=True to update a data partially
        serializer = ItemSerializer(instance, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            reply = {}
            reply['Status'] = "success"
            reply['Message'] = "updated successfully"
            reply['Data'] = serializer.data
            # return Response(serializer.data, status = status.HTTP_201_CREATED)
            return Response(reply, status = status.HTTP_201_CREATED)
        return Response(data="Bad Request", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# **********************END****************************************************************************************


class SnippetFilter(django_filters.FilterSet):
    item_name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Item
        fields = ['item_name', 'price']


class CustomerItemsList(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = CustomerItemviewSerializer
    filterset_class = SnippetFilter
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['item_name', 'price']
    search_fields = ['item_name', ]


# **********************END********************************


class AddToCartAPI(APIView):
    def get(self, request, format=None):
        query = Cart.objects.all()
        serializer = CartSerializer(query, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = CartSerializer(data=request.data)

        user_id = request.data['user']
        user = CustomUser.objects.get(user_id=user_id)
        print("usrrrrname==========================",user)

        reply ={}
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                 
                # quantity = serializer.validated_data['quantity']
                # itemName = serializer.validated_data['item']
                # deliveryCharge = serializer.validated_data['deliveryCharge']
                # otherCharges = serializer.validated_data['otherCharges']
                # print("***********************************************",itemName)

                # item = Item.objects.get(item_name=itemName)
                # print( "ITEM PRICE+++++++++++======",item.price)

                # itemPrice = (item.price) * int(quantity)
                # print(itemPrice)

                # subTotal = float(deliveryCharge) + float(otherCharges)
                # print("subtotal====================",subTotal)
                # total = float(subTotal) + float(itemPrice)
                # print("total========================",total)

                reply['status'] = "success"
                reply['message'] = "items added to cart"
                reply['Data'] = serializer.data 

                return Response(reply, status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            print(serializer.errors)
            reply['status'] = "error"
            reply['message'] = serializer.errors
            return Response(reply, status=status.HTTP_400_BAD_REQUEST)


class CartDetails(APIView):

    def get_object(self, pk):
        try:
            return Cart.objects.get(pk=pk)
        except Cart.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        query = self.get_object(pk)
        serializer = CartSerializer(query)
        reply = {}
        reply['Data'] = serializer.data
        return Response(reply, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = CartSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        instance = self.get_object(pk)

        # set partial=True to update a data partially
        serializer = CartSerializer(instance, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            reply = {}
            reply['Status'] = "Success"
            reply['Message'] = "Updated Successfully"
            reply['Data'] = serializer.data
            return Response(reply, status = status.HTTP_201_CREATED)
        return Response(data="Bad Request", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# **********************END**********************************************************************************************


class CustomerOrderList(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # filterset_class = SnippetFilter
    # filter_backends = [DjangoFilterBackend, SearchFilter]
    # filterset_fields = ['item_name', 'price', 'veg_or_non']
    # search_fields = ['item_name', ]



#**************************************************************************************************************


class Wishlist(APIView):

    def get(self, request, format=None):
        snippets = Wishlist.objects.all()
        serializer = WishlistSerializer(snippets, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = WishlistSerializer(data=request.data)

        user_id = request.data['user']
        user = CustomUser.objects.get(user_id=user_id)
        print("usrrrrname==========================",user)
        try:

            if serializer.is_valid(raise_exception=True):
                serializer.save(user=user)
                reply ={}
                reply['status'] = "success"
                reply['Data'] = serializer.data
                return Response(reply, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(serializer.errors)
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)    


class WishlistDetail(APIView):

    def get_object(self, pk):
        try:
            return Wishlist.objects.get(pk=pk)
        except Wishlist.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = WishlistSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = WishlistSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()

            reply ={}
            reply['status'] = "success"
            reply['Data'] = serializer.data
            return Response(reply,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        instance = self.get_object(pk)

        # set partial=True to update a data partially
        serializer = WishlistSerializer(instance, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            reply = {}
            reply['Status'] = "Success"
            reply['Message'] = "Updated Successfully"
            reply['Data'] = serializer.data
            return Response(reply, status = status.HTTP_201_CREATED)
        return Response(data="Bad Request", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class OrderView(APIView):

    def get(self, request, format=None):
        snippets = Order.objects.all()
        serializer = OrderSerializer(snippets, many=True)
        return Response(serializer.data)

    
    def post(self, request, format=None):
        
        serializer = OrderSerializer(data=request.data)
        user_id = request.data['user']
        user = CustomUser.objects.get(user_id=user_id)
     
        # print("usrrrrname==========================",user)
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=user)
                reply ={}   
                reply['status'] = "success"
                reply['data'] = serializer.data
                return Response(reply, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            reply ={}   
            reply['status'] = "failed"
            reply['error'] = serializer.errors
            return Response(reply, status=status.HTTP_400_BAD_REQUEST)


class OrderDetail(APIView):

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = OrderSerializer(snippet)
        return Response(serializer.data)


    def patch(self, request, pk):
        instance = self.get_object(pk)

        # set partial=True to update a data partially
        serializer = OrderSerializer(instance, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            reply = {}
            reply['status'] = "Success"
            reply['message'] = "Updated Successfully"
            reply['data'] = serializer.data
            return Response(reply, status = status.HTTP_201_CREATED)
        reply = {}
        reply['status'] = "error"
        return Response(reply, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# **********************END*************************************************************************************88


class CardView(APIView):
    def get(self, request, format=None):
        snippets = Card.objects.all()
        serializer = CardSerializer(snippets, many=True)
        return Response(serializer.data)


    def post(self, request, format=None):
        serializer = CardSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            reply ={}
            reply['status'] = "success"
            reply['Data'] = serializer.data
            return Response(reply, status=status.HTTP_201_CREATED)
        else:
            reply ={}
            reply['status'] = "failed"
            reply['error'] = serializer.errors
            return Response(reply, status=status.HTTP_400_BAD_REQUEST)


class CardDetail(APIView):

    def get_object(self, pk):
        try:
            return Card.objects.get(pk=pk)
        except Card.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = CardSerializer(snippet)
        reply ={}
        reply['status'] = "success"
        reply['Data'] = serializer.data
        return Response(reply, status =status.HTTP_200_OK)

    def patch(self, request, pk):
        instance = self.get_object(pk)

        # set partial=True to update a data partially
        serializer = CardSerializer(instance, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            reply = {}
            reply['Status'] = "Success"
            reply['Message'] = "Updated Successfully"
            reply['Data'] = serializer.data
            return Response(reply, status = status.HTTP_201_CREATED)
        reply = {}
        reply['status'] = "error"
        return Response(reply, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



#******************************************************************************************************************8

class GalleryView(APIView):
    def get(self, request, format=None):
        snippets = Gallery.objects.all()
        serializer = GallerySerializer(snippets, many=True)
        return Response(serializer.data)


    def post(self, request, format=None):
        serializer = GallerySerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            reply ={}
            reply['status'] = "success"
            reply['Data'] = serializer.data
            return Response(reply, status=status.HTTP_201_CREATED)
        reply = {}
        reply['status'] = "error"
        reply['error'] = serializer.errors 
        return Response(reply, status=status.HTTP_400_BAD_REQUEST)



class GalleryDetail(APIView):

    def get_object(self, pk):
        try:
            return Gallery.objects.get(pk=pk)
        except Gallery.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = GallerySerializer(snippet)
        reply ={}
        reply['status'] = "success"
        reply['Data'] = serializer.data
        return Response(reply, status =status.HTTP_200_OK)


    def patch(self, request, pk):
        instance = self.get_object(pk)

        # set partial=True to update a data partially
        serializer = GallerySerializer(instance, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            reply = {}
            reply['Status'] = "Success"
            reply['Message'] = "Updated Successfully"
            reply['Data'] = serializer.data
            return Response(reply, status = status.HTTP_201_CREATED)
        return Response(data="Bad Request", status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#******************************************************************************************************************8


class InvoiceView(APIView):
    def get(self, request, format=None):
        snippets = Invoice.objects.all()
        serializer = InvoiceSerializer(snippets, many=True)
        return Response(serializer.data)


    def post(self, request, format=None):
        serializer = InvoiceSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            reply ={}
            reply['status'] = "success"
            reply['Data'] = serializer.data
            return Response(reply, status=status.HTTP_201_CREATED)
        reply = {}
        reply['status'] = "error"
        reply['error'] = serializer.errors 
        return Response(reply, status=status.HTTP_400_BAD_REQUEST)


class InvoiceDetail(APIView):

    def get_object(self, pk):
        try:
            return Invoice.objects.get(pk=pk)
        except Invoice.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = InvoiceSerializer(snippet)
        reply ={}
        reply['status'] = "success"
        reply['Data'] = serializer.data
        return Response(reply, status =status.HTTP_200_OK)


    def patch(self, request, pk):
        instance = self.get_object(pk)

        # set partial=True to update a data partially
        serializer = InvoiceSerializer(instance, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            reply = {}
            reply['Status'] = "Success"
            reply['Message'] = "Updated Successfully"
            reply['Data'] = serializer.data
            return Response(reply, status = status.HTTP_201_CREATED)
        return Response(data="Bad Request", status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#******************************************************************************************************************8

class ReviewView(APIView):

    def post(self, request, format=None):
        serializer = ReviewSerializer(data=request.data)
        user_id = request.data['user']
        user = CustomUser.objects.get(user_id=user_id)
        user_ratings = Review.objects.all().values('item').order_by('item').annotate(rating_average=Avg('rating'))
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save(user = user)
                
                reply ={}
                reply['status'] = "success"
                reply['rating'] = user_ratings
                # reply['Data'] = serializer.data   
                return Response(reply, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            reply = {}
            reply['status'] = "error"
            reply['error'] = str(e)
            return Response(reply, status=status.HTTP_400_BAD_REQUEST)

    def get(self,request):

        user_ratings = Review.objects.all().values('user').order_by('user').annotate(rating_average=Avg('rating'))
        print(user_ratings)
        reply ={}
        reply['status'] = "success"
        reply['data'] = user_ratings
        return Response(reply, status=status.HTTP_201_CREATED)


#******************************************************************************************************************

class ChatView(APIView):

    def get(self, request, format=None):
        snippets = Chat.objects.all()
        serializer = ChatSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ChatSerializer(data=request.data)
        # name = request.data['sender']
        # user = CustomUser.objects.get(name=name)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            reply ={}
            reply['status'] = "success"
            reply['Data'] = serializer.data
            return Response(reply, status=status.HTTP_201_CREATED)
        reply = {}
        reply['status'] = "error"
        reply['error'] = serializer.errors 
        return Response(reply, status=status.HTTP_400_BAD_REQUEST)


#******************************************************************

# class TicketView(APIView):

    # def get(self, request, format=None):
    #     snippets = TicketGenerate.objects.all()
    #     serializer = TicketSerializer(snippets, many=True)
    #     return Response(serializer.data)

    # def post(self, request, format=None):
    #     serializer = TicketSerializer(data=request.data)
        
    #     user_id = request.data['user']
    #     user = CustomUser.objects.get(user_id = user_id)

    #     sender = request.data['admin']
    #     sent = CustomUser.objects.get(name = sender)
       
    #     #  


    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save(userId= user,adminId = sent)
            
    #         reply ={}
    #         reply['status'] = "success"
    #         reply['Data'] = serializer.data
    #         return Response(reply, status=status.HTTP_201_CREATED)
    #     reply = {}
    #     reply['status'] = "error"
    #     reply['error'] = serializer.errors 
    #     return Response(reply, status=status.HTTP_400_BAD_REQUEST)


def message_list(request, userId=None, adminId=None):
    if request.method == 'GET':
        messages = TicketGenerate.objects.filter(userId=userId, adminId=adminId)
        serializer = TicketSerializer(messages, many=True)
        return Response(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = TicketSerializer(data=data)
        
        if serializer.is_valid():
            user_id = request.data['user']
            user = CustomUser.objects.get(name = user_id)
            admin_id = request.data['admin']
            admin = CustomUser.objects.get(name = admin_id)
            
            serializer.save(userId = user, adminId= admin)
            return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

#**************************************************************************************************

class DeliveryPartnerView(APIView):

    def get(self, request, format=None):
        snippets = DeliveryPartnerProfile.objects.all()
        serializer = DeliveryPartnerSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        serializer = DeliveryPartnerSerializer(data=request.data)
        user_id = request.data['user']
        user = CustomUser.objects.get(user_id=user_id)
        if serializer.is_valid(raise_exception=True):
            serializer.save(userId = user)

            vehicleType = serializer.validated_data["vehicleType"]
            city = serializer.validated_data["city"]
            locality = serializer.validated_data["locality"]
            workingHours = serializer.validated_data["workingHours"]
            panCardNumber = serializer.validated_data["panCardNumber"]
            uploadPanCard = serializer.validated_data["uploadPanCard"]
            nameAsOnPandcard = serializer.validated_data["nameAsOnPandcard"]
            aadarNumber = serializer.validated_data["aadarNumber"]
            dateOfBirth = serializer.validated_data["dateOfBirth"]
            fatherName = serializer.validated_data["fatherName"]
            address1 = serializer.validated_data["address1"]
            address2 = serializer.validated_data["address2"]
            district = serializer.validated_data["district"]
            state = serializer.validated_data["state"]
            pincode = serializer.validated_data["pincode"]
            licenseNumber = serializer.validated_data["licenseNumber"]
            dlexpiry = serializer.validated_data["dlexpiry"]
            dlUploadFront = serializer.validated_data["dlUploadFront"]
            dlUploadBack = serializer.validated_data["dlUploadBack"]
            vehicleNumber = serializer.validated_data["aadarNumber"]
            vehicleMake = serializer.validated_data["vehicleMake"]
            insuranceNumber = serializer.validated_data["insuranceNumber"]
            rcBookUpload = serializer.validated_data["rcBookUpload"]
            approved = serializer.validated_data["approved"]

            if approved == True:
                approval_request = DeliveryPartnerApproval(userId=user, vehicleType=vehicleType, city=city, locality=locality,
                                                        workingHours=workingHours, panCardNumber=panCardNumber,
                                                        uploadPanCard=uploadPanCard, nameAsOnPandcard=nameAsOnPandcard,
                                                        aadarNumber=aadarNumber,dateOfBirth= dateOfBirth,fatherName=fatherName,
                                                        address1=address1,address2=address2,district=district,state=state,
                                                        pincode=pincode,licenseNumber=licenseNumber,dlexpiry=dlexpiry,
                                                        dlUploadFront=dlUploadFront,dlUploadBack=dlUploadBack,vehicleNumber=vehicleNumber,
                                                        vehicleMake=vehicleMake,insuranceNumber=insuranceNumber,rcBookUpload=rcBookUpload,
                                                        approved=approved)
                approval_request.save()

            reply ={}
            reply['status'] = "success"
            reply['Data'] = serializer.data
            return Response(reply, status=status.HTTP_201_CREATED)
        reply = {}
        reply['status'] = "error"
        reply['error'] = serializer.errors 
        return Response(reply, status=status.HTTP_400_BAD_REQUEST)


    
class DeliveryPartnerDetails(APIView):
    
    def get_object(self, pk):
        try:
            return DeliveryPartnerProfile.objects.get(pk=pk)
        except DeliveryPartnerProfile.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = DeliveryPartnerSerializer(snippet)
        reply = {}
        reply['status'] = "success"
        reply['Data'] = serializer.data
        return Response(reply,status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = DeliveryPartnerSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()

            reply ={}
            reply['status'] = "success"
            reply['Data'] = serializer.data
            return Response(reply,status=status.HTTP_200_OK)
        reply ={}
        reply['status'] = "success"
        reply['Data'] = serializer.data
        return Response(reply, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        instance = self.get_object(pk)

        # set partial=True to update a data partially
        serializer = DeliveryPartnerSerializer(instance, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            reply = {}
            reply['Status'] = "Success"
            reply['Message'] = "Updated Successfully"
            reply['Data'] = serializer.data
            return Response(reply, status = status.HTTP_201_CREATED)
        reply = {}
        reply['status'] = "failed"
        reply['error'] = serializer.errors
        return Response(reply, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        reply = {}
        reply['status'] = "success"
        reply['message'] = "deleted successfully"
        return Response(reply,status=status.HTTP_204_NO_CONTENT)


# **********************END********************************



class CustomerSupportView(APIView):

    def get(self, request, format=None):
        snippets = CustomerSupport.objects.all()
        serializer = CustomerSupportSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        
        serializer = CustomerSupportSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            rand_token = uuid4()
            serializer.save(token = rand_token)

            reply ={}
            reply['status'] = "success"
            reply['Data'] = serializer.data
            return Response(reply, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerSupportDetail(APIView):

    def get_object(self, pk):
        try:
            return CustomerSupport.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = CustomerSupportSerializer(snippet)
        return Response(serializer.data)

    def patch(self, request, pk):
        instance = self.get_object(pk)

        # set partial=True to update a data partially
        serializer = CustomerSupportSerializer(instance, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            reply = {}
            reply['Status'] = "Success"
            reply['Message'] = "Updated Successfully"
            reply['Data'] = serializer.data

            return Response(reply, status = status.HTTP_201_CREATED)
        return Response(data="Bad Request", status=status.HTTP_400_BAD_REQUEST)