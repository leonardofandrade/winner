from rest_framework import serializers

from loterias.models import Contest


class ContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = [
            "id",
            "number",
            "draw_date",
            "winning_numbers",
            "prize_pool",
            "accumulated",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
