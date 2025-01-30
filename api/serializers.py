from django.contrib.auth import authenticate
from api.models import Seller,  FoodCategory, Food, Table, Cart, Checkout
from rest_framework import serializers


class UserSerilizer(serializers.ModelSerializer):

    password1 = serializers.CharField(write_only = True)

    password2 = serializers.CharField(write_only = True)

    password = serializers.CharField(read_only = True)

    class Meta:

        model = Seller
        fields = ['id', 'username', 'email', 'password1', 'password2', 'seller_category', 'password']
        

    
    def create(self, validated_data):

        password1 = validated_data.pop('password1')

        password2 = validated_data.pop('password2')

        

        if password1 != password2:

            raise serializers.ValidationError('Password Mismatch')

        return Seller.objects.create_user(**validated_data, password = password1)


class SignInSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        data['user'] = user
        return data

class FoodCategorySerializer(serializers.ModelSerializer):

    class Meta:

        model = FoodCategory        
        fields= ['food_category_name', 'category_image', 'owner' ]
        read_only_field = ['id', 'created_date', 'is_active']
     
    def validate_name(self, value):

        if FoodCategory.objects.filter(food_category_name = value).exists():

            raise serializers.ValidationError("Category name already exists")
        
        return value


class FoodSerializer(serializers.ModelSerializer):

    class Meta:

        model = Food
        fields = "__all__"
        read_only_field = ['id', 'created_date', 'owner', 'is_active']
    
    
    def validate_name(self, value):

        if Food.objects.filter(food_name = value).exists():
            raise serializers.ValidationError("Food name already exists")    
        return value


class TableSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Table
        fields = ['id', 'table_number', 'is_occupied', 'owner']


class CartSerializer(serializers.ModelSerializer):
    food = serializers.CharField(source='food.food_name')
    image = serializers.ImageField(source='food.food_image') 
    table_number = serializers.IntegerField(source="table_number.table_number", read_only=True)
    food_price = serializers.DecimalField(source='food.price',max_digits=10, decimal_places= 2)

    class Meta:
        model = Cart
        fields =  ['id', 'food', 'quantity', 'image', 'table_number', 'food_price']

    def create(self, validated_data):
        # Extract nested data for related models
        food_name = validated_data.pop('food')['food_name']

        # Retrieve related objects
        food = Food.objects.get(food_name=food_name)

        # Create the Cart instance
        cart = Cart.objects.create(
            food=food,
            **validated_data
        )
        return cart
    
    def update(self, instance, validated_data):
        # Extract nested fields
        food_data = validated_data.pop('food', None)

        # Update food if provided
        if food_data:
            food_name = food_data.get('food_name')
            instance.food = Food.objects.get(food_name=food_name)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    # def get_total_price(self, obj):
    #     # Ensure that food_price and quantity are valid before calculating
    #     if obj.food and obj.quantity:
    #         return obj.food.price * obj.quantity
    #     return 0  # Default to 0 if either value is missing
    

class CheckoutSerializer(serializers.ModelSerializer):
    table_number = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    prep_time = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Checkout
        fields = ['id', 'table_number', 'items', 'prep_time', 'total_price']

    def get_table_number(self, obj):
        """
        Retrieves the table number from the first cart item.
        """
        cart_item = obj.cart.first()  # Get any cart item
        return cart_item.table_number.table_number if cart_item else None

    def get_items(self, obj):
        """
        Returns a list of food item names from the cart.
        """
        return [cart_item.food.food_name for cart_item in obj.cart.all()]

    def get_prep_time(self, obj):
        """
        Returns the highest preparation time among all food items in the cart.
        """
        times = [cart_item.food.time_taken for cart_item in obj.cart.all() if cart_item.food and cart_item.food.time_taken]
        return max(times) if times else 0  # Return highest prep time or 0 if empty

    def get_total_price(self, obj):
        """
        Returns the total price of all items in the cart.
        """
        return sum(cart_item.food.price * cart_item.quantity for cart_item in obj.cart.all() if cart_item.food and cart_item.quantity)
