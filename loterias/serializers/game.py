from rest_framework import serializers

from loterias.models import Game


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ["id", "user", "numbers", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]
