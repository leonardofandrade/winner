from rest_framework import serializers

from loterias.models import GameResult


class GameResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameResult
        fields = ["id", "game", "contest", "hits", "prize", "created_at"]
        read_only_fields = ["created_at"]
