from rest_framework import serializers
from .models import Client, Produit, Vente, VenteProduit, Depense, MouvementStock, ChatbotConversation, ChatbotMessage, AdminLog, EntrepriseSettings

class ClientSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Client
        fields = '__all__'

class ProduitSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Produit
        fields = '__all__'

class VenteProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenteProduit
        fields = '__all__'

class VenteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    produits = VenteProduitSerializer(many=True, read_only=True)

    class Meta:
        model = Vente
        fields = '__all__'

class DepenseSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Depense
        fields = '__all__'

class MouvementStockSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = MouvementStock
        fields = '__all__'

class ChatbotMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotMessage
        fields = ['id', 'sender', 'text', 'timestamp']

class ChatbotConversationSerializer(serializers.ModelSerializer):
    messages = ChatbotMessageSerializer(many=True, read_only=True)
    class Meta:
        model = ChatbotConversation
        fields = ['id', 'title', 'created_at', 'messages']

class AdminLogSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')
    class Meta:
        model = AdminLog
        fields = ['id', 'user', 'action', 'details', 'date']

class EntrepriseSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntrepriseSettings
        fields = '__all__' 