from watchers_app.models import TofaProductsRepository, TofaProductsOrder
from rest_framework import serializers

class TofaProductsRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TofaProductsRepository
        fields = ['item_name', 'item_description', 'price', 'item_quantity', 'category']


class TofaProductsOrderSerializer(serializers.ModelSerializer):
    item_name=TofaProductsRepositorySerializer(read_only=True)
    class Meta:
        model = TofaProductsOrder
        fields = ['item_name', 'count', 'table_number']
        read_only_fields = ['user', 'created_at', 'fullfilled_at', 'status']

    def validate_count(self, value):
        if value < 1:
            raise serializers.ValidationError("Count must be greater than 0.")
        return value

    def update(self, instance, validated_data):
        instance.count = validated_data.get('count', instance.count)
        instance.save()
        return instance
