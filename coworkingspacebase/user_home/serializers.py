from watchers_app.models import TofaProductsRepository, TofaProductsOrder,TofaProductsOrderID
from rest_framework import serializers

class TofaProductsRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TofaProductsRepository
        fields = ['item_name', 'item_description', 'price']

class TofaProductsOrderSerializer(serializers.ModelSerializer):
    item_name = serializers.SlugRelatedField(
        slug_field='item_name',
        queryset=TofaProductsRepository.objects.all()
    )
    class Meta:
        model = TofaProductsOrder
        fields = ['item_name', 'count']
        read_only_fields = ['user']

    def validate_count(self, value):
        if value < 1:
            raise serializers.ValidationError("Count must be greater than 0.")
        return value

    def update(self, instance, validated_data):
        instance.count = validated_data.get('count', instance.count)
        instance.save()
        return instance
    
class TofaProductsOrderIDSerializer(serializers.ModelSerializer):
    class Meta:
        model= TofaProductsOrderID
        fields=['status','order_creation_time','table_number']

