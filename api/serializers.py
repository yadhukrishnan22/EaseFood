from django.contrib.auth import authenticate
from api.models import Seller,  FoodCategory, Food, Table, Cart
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
    food_categories = serializers.CharField(source='food_category.food_category_name', read_only=True)
    foods = serializers.CharField(source='food.food_name', read_only=True)
    total_price = serializers.SerializerMethodField()  # Dynamically calculate total price
    preparation_time = serializers.SerializerMethodField()

    food_category = serializers.PrimaryKeyRelatedField(queryset=FoodCategory.objects.all())
    food = serializers.PrimaryKeyRelatedField(queryset=Food.objects.all())
    food_price = serializers.PrimaryKeyRelatedField(queryset=Food.objects.all())
    table_number = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all())

    class Meta:
        model = Cart
        fields =  ['id', 'food_categories', 'foods', 'table_number', 'quantity','preparation_time', 'status','total_price', 'food', 'food_category','food_price']
        
    def get_total_price(self, obj):
        # Ensure that food_price and quantity are valid before calculating
        if obj.food_price and obj.quantity:
            return obj.food_price.price * obj.quantity
        return 0  # Default to 0 if either value is missing
    
    def get_preparation_time(self, obj):
        # Return the preparation time of the associated food
        return obj.food.time_taken if obj.food else None