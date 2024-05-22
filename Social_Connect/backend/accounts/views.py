from django.shortcuts import render
from .serializers import UserRegisterSerializer,userserializer,UserSerializer,AllUserSerializer
from rest_framework import status
from rest_framework import permissions,status,generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenRefreshSerializer
from rest_framework.exceptions import AuthenticationFailed,ParseError
from rest_framework_simplejwt.tokens import RefreshToken,BlacklistedToken, OutstandingToken
from .models import  User
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.utils.crypto import get_random_string
from . models import User
import random
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.http import JsonResponse


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['first_name'] = user.first_name
        # ...
        
        return token

class RegisterView(APIView):
    def post(self,request):
        serializer = UserRegisterSerializer(data=request.data)
        email_id= request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        print(request.data)
        if password != confirm_password:
            return Response({"error": "Passwords don't match"}, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer.is_valid():
            print("working..")
            serializer.save()
            user=User.objects.get(email=email_id)
            user.is_active=False
            length=6
            digits = "0123456789"
            otp = ''.join(random.choice(digits) for _ in range(length))
            user.OTP=otp
            print(otp)
            user.save()

            return (send_otp_email(email_id, otp))
        else:
            print("not working ..")
        return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
            
        
            

class OtpVerify(APIView):
    def post(self, request):
        otp = int(request.data.get("OTP", None))  # Corrected syntax for getting data from request
        email = request.data.get("email", None)  # Corrected syntax for getting data from request
        print(otp)
        if not otp or not email:  # Check if both OTP and email are provided
            return Response({"error": "OTP and email are required."}, status=status.HTTP_400_BAD_REQUEST)
            print("no otp")
        try:
            user = User.objects.get(email=email)
            print(user.OTP)
            if user.OTP == otp:
                user.is_active = True
                user.save()
                print("otp....")
                return Response({"message": "OTP verified successfully. User activated."},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Invalid OTP."},
                                status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)
        
    
def send_otp_email(email, otp):
    """Send OTP to the user's email."""
    subject = 'Your OTP for Verification'
    message = f'Your OTP is: {otp}'
    from_email = 'socialconnect'  # Sender's email address
    recipient_list = [email]  # List of recipient email addresses
    print("otp")
    send_mail(subject, message, from_email, recipient_list)

    print(subject, message, from_email, recipient_list)
    return Response({"message":"OTP send"},status=status.HTTP_200_OK)


class LoginView(APIView):
    def post(self,request):
       
        try:
            
            email = request.data['email']
            password =request.data['password']
            print(email,password)
        
        except KeyError:
            raise ParseError('All Fields Are Required')
        
        if not User.objects.filter(email=email).exists():
            print('no mail')
            raise AuthenticationFailed('Invalid Email Address')
        
        
        if not User.objects.filter(email=email,is_active=True).exists():
            print('not active')
            raise AuthenticationFailed('You are blocked by admin ! Please contact admin')
        print('hi')
        user = authenticate(username=email,password=password)
        print(user)
        if user is None:
            raise AuthenticationFailed('Invalid Password')
        
        refresh = RefreshToken.for_user(user)
        refresh['user']=user.id
        refresh["first_name"] = str(user.first_name)
        refresh['is_superuser'] = user.is_superuser
        refresh['email']=user.email
       
        content = {
                    'user_id':user.id,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'isAdmin':user.is_superuser,
                }
        print("login working ...")
        
        return Response(content,status=status.HTTP_200_OK)
    

class UserDetails(APIView): 
    
    permission_classes = [IsAuthenticated]
    def get(self, request):
            user = request.user
            data = {
            'name': user.first_name,  # Assuming the user's first name is stored here
            'time': user.last_login,  # Assuming you want to track the last login time
            'profile_pic': user.profile_pic.url  # Assuming you have a profile picture field in your User model
            }
            return Response(data,status=status.HTTP_200_OK)


class AllUserDetailsView(APIView):
    print("outide all user")
    permisssion_classes=[IsAuthenticated]
    def get(self,request):
        print("inside all User")
        current_user=request.user
        queryset= User.objects.exclude(pk=current_user.pk)
        serializer_class = AllUserSerializer(queryset, many=True)
        
        return Response(serializer_class.data,status=status.HTTP_200_OK)


class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        # print("insideget")
        # user = request.user
        # print(user.displa)
        # serialzier= UserSerializer(user)
        # return Response(serialzier.data,status=status.HTTP_200_OK)
        user = User.objects.get(id=request.user.id)
       
        data = UserSerializer(user).data
        try :
            profile_pic = user.display_pic
            if profile_pic:
                absolute_profile_pic_url = request.build_absolute_uri(profile_pic.url)
                data['profile_pic'] = absolute_profile_pic_url
                
        except:
            profile_pic = ''
            data['profile_pic']=''
            
        content = data
        return Response(content,status=status.HTTP_200_OK)

    # permission_classes = [IsAuthenticated]
    # def get(self, request):
        # user = User.objects.get(id=request.user.id)
       
        # data = UserSerializer(user).data
        # try :
        #     profile_pic = user.display_pic
        #     data['profile_pic'] = request.build_absolute_uri('/')[:-1]+profile_pic.url
        #     print(data['profile_pic'])
        # except:
        #     profile_pic = ''
        #     data['profile_pic']=''
            
        # content = data
        # return Response(content,status=status.HTTP_200_OK)

class SpecificUserDetails(APIView):
    permission_classes=[IsAuthenticated]
    print("outofSpecific")
    def get(self,request):
        print("insideofSpecific")

        user_id = request.GET.get('user_id')
        user_data = get_object_or_404(User, pk=user_id)
        
        serializer = userserializer(user_data)
        serialized_data = serializer.data
        print("specific",serialized_data)
        return Response(serialized_data)
    
class CurrentUser(APIView):
    permisssion_classes=[IsAuthenticated]
    def get(self,request):
        user=request.user
        serializer=UserSerializer(user)
        serializer_data=serializer.data
        return Response(serializer_data,status=status.HTTP_200_OK)


class EditUserView(APIView):
    permission_classes = [IsAuthenticated]
    def  post(self,request):
        print("inside EditUserView")
        user=request.user
        data = request.data
        print(data)
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        display_pic = request.data.get('display_pic')

        user.first_name = first_name
        user.last_name = last_name
        if display_pic:
             user.display_pic.save(display_pic.name, display_pic, save=True)
        user.save()
        return JsonResponse({'success': True, 'message': 'Profile updated successfully'})
    


class searchUserView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        query = request.GET.get('q','')
        if query:
            users = User.objects.filter(first_name__icontains=query) 
            user_data = [{"id": user.id, "username": user.username, "pro_pic":user.display_pic.url if user.display_pic else None } for user in users]
            return JsonResponse(user_data,safe=False)
        return JsonResponse([],safe=False)