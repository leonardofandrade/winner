from rest_framework import serializers

from loterias.models import Game

_MIN_NUMBERS = 15
_MAX_NUMBERS = 20
_MIN_VALUE = 1
_MAX_VALUE = 25


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ["id", "user", "numbers", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]

    def validate_numbers(self, value: list) -> list:
        if not isinstance(value, list) or not all(isinstance(n, int) for n in value):
            raise serializers.ValidationError("numbers deve ser uma lista de inteiros.")
        if len(value) < _MIN_NUMBERS or len(value) > _MAX_NUMBERS:
            raise serializers.ValidationError(
                f"Um jogo precisa ter entre {_MIN_NUMBERS} e {_MAX_NUMBERS} dezenas."
            )
        if any(n < _MIN_VALUE or n > _MAX_VALUE for n in value):
            raise serializers.ValidationError("Todas as dezenas devem estar entre 1 e 25.")
        if len(set(value)) != len(value):
            raise serializers.ValidationError("As dezenas não podem se repetir.")
        return sorted(value)
