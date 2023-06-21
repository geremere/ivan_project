from rest_framework import serializers

from app.product.models import User, Rate, RateHistory


class UserSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)

    class Meta:
        model = User
        fields = ("id", "name", "login", "department", "position", "image")


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = "__all__"


class RateHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RateHistory
        fields = "__all__"
