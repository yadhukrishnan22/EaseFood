from django.shortcuts import render, get_object_or_404
from rest_framework.generics import CreateAPIView
from api.serializers import UserSerilizer, SignInSerializer, FoodCategorySerializer, FoodSerializer, Seller, TableSerializer
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics
from api.models import FoodCategory, Food, Table
from rest_framework import status
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework import authentication, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken


class SignUpView(CreateAPIView):

    serializer_class = UserSerilizer


class SignInView(APIView):

    def post(self, request, *args, **kwargs):

        serializer = SignInSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.validated_data['user']
            
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                'access_token': access_token,
                'refresh_token': str(refresh),
                'user': user.username,
                'message': 'Login successfull'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class FoodCategoryCreateView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]  

    def get(self, request, *args, **kwargs):

        qs = FoodCategory.objects.filter(owner = request.user)
        serializer_instance = FoodCategorySerializer(qs, many=True)

        return Response(data= serializer_instance.data)
        
    def post(self, request, *args, **kwargs):

        serializer = FoodCategorySerializer(data = request.data)

        if serializer.is_valid():

            try:
                serializer.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            except IntegrityError:

                raise ValidationError({"message":"The category name already exists"})
                      
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FoodCategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = FoodCategorySerializer
    queryset = FoodCategory.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]  


class FoodCreateListView(generics.ListCreateAPIView):

    serializer_class = FoodSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]   

    def get(self, request, *args, **kwargs):

        qs = Food.objects.filter(owner = request.user)
        serializer_instance = FoodSerializer(qs, many = True)

        if serializer_instance:

            return Response(serializer_instance.data, status = status.HTTP_200_OK)        
        return Response(serializer_instance.error, status = status.HTTP_400_BAD_REQUEST)



class FoodRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = FoodSerializer
    queryset = Food.objects.all()
    permission_classes = [JWTAuthentication]


class TableCreateListView(APIView):
    
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]


    def get(self, request):
        user = request.user
        tables = Table.objects.filter(owner = user)
        return Response(TableSerializer(tables, many=True).data)

    def post(self, request, *args, **kwargs):
        user = request.user
        owner = user.id

        table_number = request.data.get('table_number')
        if not table_number:
            return Response({"error": "Table number is required."}, status=status.HTTP_400_BAD_REQUEST)

        table = Table.objects.create(owner = user, table_number=table_number)
        table.save()
        

        return Response(TableSerializer(table).data, status=status.HTTP_201_CREATED)


class TableUpdateView(APIView):
    
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, table_id):
        user = request.user
        try:
            table = Table.objects.get(id=table_id, owner = user)
        except Table.DoesNotExist:
            return Response({"error": "Table not found."}, status=status.HTTP_404_NOT_FOUND)

        table_number = request.data.get('table_number')
        is_occupied = request.data.get('is_occupied')

        if table_number is not None:
            table.table_number = table_number
        if is_occupied is not None:
            table.is_occupied = is_occupied

        table.save()
        return Response(TableSerializer(table).data)


class TableDeleteView(APIView):
    
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, table_id):
        user = request.user
        try:
            table = Table.objects.get(id=table_id, owner = user)
        except Table.DoesNotExist:
            return Response({"error": "Table not found."}, status=status.HTTP_404_NOT_FOUND)

        table.delete()
        return Response({"message": "Table deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class FoodCategoryMenuView(APIView):

    def get(self, request, *args, **kwargs):

        pin = kwargs.get('pin')     
        try:
            owner = get_object_or_404(Seller, pin = pin)    
        except:
            return Response({"detail":"seller not found"}, status=status.HTTP_400_BAD_REQUEST)
        

        food_category = FoodCategory.objects.filter(owner = owner)
        food_category_serializer = FoodCategorySerializer(food_category, many=True)

        # tables = Table.objects.filter(owner = owner)
        # tables_serializer_instance = TableSerializer(tables, many=True)

        return Response({
            "seller":owner.username, 
            "food_category":food_category_serializer.data})


class FoodMenuView(APIView):

    def get(self, request, *args, **kwargs):

        pin = kwargs.get('pin')
        
        try:
            owner = get_object_or_404(Seller, pin = pin)    
        except:
            return Response({"detail":"seller not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        food_items = Food.objects.filter(owner = owner)
        food_serializer_instance = FoodSerializer(food_items, many=True)

        # food_category = FoodCategory.objects.filter(owner = owner)
        # food_category_serializer = FoodCategorySerializer(food_category, many=True)

        # tables = Table.objects.filter(owner = owner)
        # tables_serializer_instance = TableSerializer(tables, many=True)

        return Response({
            "seller":owner.username,
            "food_items":food_serializer_instance.data
            })

class TableMenuView(APIView):

    def get(self, request, *args, **kwargs):

        pin = kwargs.get('pin')
        
        try:
            owner = get_object_or_404(Seller, pin = pin)    
        except:
            return Response({"detail":"seller not found"}, status=status.HTTP_400_BAD_REQUEST)

        tables = Table.objects.filter(owner = owner)
        tables_serializer_instance = TableSerializer(tables, many=True)

        return Response({
            "seller":owner.username,            
            "tables":tables_serializer_instance.data})







    

