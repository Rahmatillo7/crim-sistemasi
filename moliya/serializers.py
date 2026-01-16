from rest_framework import serializers
from .models import Payment, Debt


from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.name', read_only=True)
    center_name = serializers.CharField(source='center.name', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'student',
            'student_name',
            'center',
            'center_name',
            'amount',
            'method',
            'status',
            'transaction_id',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DebtSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.name', read_only=True)

    class Meta:
        model = Debt
        fields = ['id', 'student', 'student_name', 'amount', 'due_date', 'status', 'description', 'created_at',
                  'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']