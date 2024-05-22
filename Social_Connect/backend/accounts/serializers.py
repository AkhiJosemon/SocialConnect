from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenRefreshSerializer
from rest_framework import serializers
from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken, Token,AccessToken

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','email','password']
        extra_kwargs = {
            'password':{ 'write_only':True}
        }
        
    
    def create(self,validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
            instance.save()
            return instance
        else:
            raise serializers.ValidationError({"password": "password is not valid"})
        

class userserializer(serializers.ModelSerializer):
     class Meta:
          model=User
          fields=['id','username','display_pic','first_name','last_name','email','is_active','is_staff','is_superuser']



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', )


class AllUserSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email',  'display_pic']


