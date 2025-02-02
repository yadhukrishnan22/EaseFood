from django.shortcuts import render, get_object_or_404
from rest_framework.generics import CreateAPIView
from api.serializers import (UserSerilizer, SignInSerializer, FoodCategorySerializer, FoodSerializer, Seller,
                              TableSerializer, CartSerializer, CheckoutSerializer)
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics
from api.models import FoodCategory, Food, Table, Cart, Checkout
from rest_framework import status
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework import authentication, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
# import razorpay


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
                'pin':user.pin,
                'owner':user.id,
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



class CartGetAPIView(APIView):
    # Get all cart items
    def get(self, request,table_id):
        id = Table.objects.get(id=table_id)
        carts = Cart.objects.filter(table_number=id)
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CartAPIView(APIView):
    # Add a new item to the cart
    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update a cart item
    def put(self, request, pk, *args, **kwargs):
        # Get the existing Cart object
        cart_instance = get_object_or_404(Cart, pk=pk)
        serializer = CartSerializer(cart_instance, data=request.data, partial=False)
        
        if serializer.is_valid():
            serializer.save()
            # Refresh the instance to get updated related fields like food_name
            cart_instance.refresh_from_db()
            updated_serializer = CartSerializer(cart_instance)
            return Response(updated_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a cart item
    def delete(self, request, pk):
        try:
            cart_item = Cart.objects.get(pk=pk)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response({"message": "Cart item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

class UpdateCartQuantityAPIView(APIView):
    def post(self, request, *args, **kwargs):
    
        cart_id = request.data.get("cart_id")
        action = request.data.get("action")

        try:
            cart_item = Cart.objects.get(id=cart_id)

            if action == "+":
                cart_item.quantity += 1
                cart_item.save()
            
            elif action == "-":
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()  # Remove item if quantity reaches 0
                    return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)

            return Response({
                "cart_id": cart_item.id,
                "new_quantity": cart_item.quantity
            }, status=status.HTTP_200_OK)

        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CheckoutListCreateView(APIView):
    """
    View to list all checkouts or create a new checkout.
    """
    def get(self, request):
        checkouts = Checkout.objects.all()
        serializer = CheckoutSerializer(checkouts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new checkout instance.
        - Retrieves cart items for the table.
        - Links the cart items to the checkout.
        - Returns the checkout details.
        """
        table_number = request.data.get("table_number")  # Get table number from request

        # Get all cart items linked to this table
        cart_items = Cart.objects.filter(table_number__table_number=table_number)

        if not cart_items.exists():
            return Response({"error": "No cart items found for this table."}, status=status.HTTP_400_BAD_REQUEST)

        # Create checkout instance and link cart items
        checkout = Checkout.objects.create()
        checkout.cart.set(cart_items)  # Add cart items to checkout

        serializer = CheckoutSerializer(checkout)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CheckoutDetailView(APIView):
    """
    View to retrieve or delete a checkout instance.
    """
    def get(self, request, pk):
        """
        Retrieve a single checkout by ID.
        """
        checkout = get_object_or_404(Checkout, id=pk)
        serializer = CheckoutSerializer(checkout)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Delete a checkout instance.
        """
        checkout = get_object_or_404(Checkout, id=pk)
        checkout.delete()
        return Response({"message": "Checkout deleted successfully."}, status=status.HTTP_204_NO_CONTENT)   

