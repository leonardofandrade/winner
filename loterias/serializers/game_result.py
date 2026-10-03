from rest_framework import serializers

from loterias.models import GameResult


class GameResultSerializer(serializers.ModelSerializer):
    contest_number = serializers.IntegerField(source="contest.number", read_only=True)

    class Meta:
        model = GameResult
        fields = ["id", "game", "contest", "contest_number", "hits", "prize", "created_at"]
        read_only_fields = ["contest_number", "created_at"]
