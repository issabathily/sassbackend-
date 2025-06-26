from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .models import Client, Produit, Vente, VenteProduit, Depense, MouvementStock, ChatbotConversation, ChatbotMessage, AdminLog, EntrepriseSettings
from .serializers import (
    ClientSerializer, ProduitSerializer, VenteSerializer, VenteProduitSerializer, DepenseSerializer, MouvementStockSerializer, ChatbotConversationSerializer, ChatbotMessageSerializer, AdminLogSerializer, EntrepriseSettingsSerializer
)
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import difflib
import random
from rest_framework.decorators import action, api_view, permission_classes
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
try:
    from weasyprint import HTML
except ImportError:
    HTML = None  # Pour éviter l'erreur si non installé
import traceback

# Create your views here.

class UserQuerySetMixin:
    def get_queryset(self):
        base_qs = super().get_queryset()
        return base_qs.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ClientViewSet(UserQuerySetMixin, viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

class ProduitViewSet(UserQuerySetMixin, viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    permission_classes = [IsAuthenticated]

class VenteViewSet(UserQuerySetMixin, viewsets.ModelViewSet):
    queryset = Vente.objects.all()
    serializer_class = VenteSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        produits_data = request.data.pop('produits', [])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vente = serializer.save(user=request.user)
        # Créer les VenteProduit associés
        for p in produits_data:
            VenteProduit.objects.create(
                vente=vente,
                produit_id=p['produit'],
                quantite=p['quantite'],
                prixUnitaire=p['prixUnitaire']
            )
        headers = self.get_success_headers(serializer.data)
        return Response(self.get_serializer(vente).data, status=status.HTTP_201_CREATED, headers=headers)

class VenteProduitViewSet(viewsets.ModelViewSet):
    queryset = VenteProduit.objects.all()
    serializer_class = VenteProduitSerializer
    permission_classes = [IsAuthenticated]

class DepenseViewSet(UserQuerySetMixin, viewsets.ModelViewSet):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer
    permission_classes = [IsAuthenticated]

class MouvementStockViewSet(UserQuerySetMixin, viewsets.ModelViewSet):
    queryset = MouvementStock.objects.all()
    serializer_class = MouvementStockSerializer
    permission_classes = [IsAuthenticated]

class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        return user

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get('token')
        print('Token reçu:', token)
        google_url = f'https://oauth2.googleapis.com/tokeninfo?id_token={token}'
        r = requests.get(google_url)
        print('Réponse Google:', r.status_code, r.text)
        if not token:
            return Response({'error': 'Token manquant'}, status=400)
        # Vérifier le token auprès de Google
        if r.status_code != 200:
            return Response({'error': 'Token Google invalide'}, status=400)
        data = r.json()
        email = data.get('email')
        if not email:
            return Response({'error': 'Email Google non trouvé'}, status=400)
        from django.contrib.auth.models import User
        user, created = User.objects.get_or_create(username=email, defaults={'email': email})
        # Générer un JWT
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Ajouter les champs personnalisés
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['email'] = user.email
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ChatbotConversationListView(generics.ListAPIView):
    serializer_class = ChatbotConversationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return ChatbotConversation.objects.filter(user=self.request.user).order_by('-created_at')

class ChatbotConversationDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ChatbotConversationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return ChatbotConversation.objects.filter(user=self.request.user)

class ChatbotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        import random
        question = request.data.get('question', '').lower().strip()
        user = request.user
        conversation_id = request.data.get('conversation_id')
        # Récupère ou crée la conversation
        if conversation_id:
            try:
                conversation = ChatbotConversation.objects.get(id=conversation_id, user=user)
            except ChatbotConversation.DoesNotExist:
                conversation = ChatbotConversation.objects.create(user=user)
        else:
            conversation = ChatbotConversation.objects.create(user=user)
        # Enregistre le message utilisateur
        ChatbotMessage.objects.create(conversation=conversation, sender='user', text=question)
        # Détection des salutations
        salutations = ["salut", "bonjour", "coucou", "hello", "yo", "hey"]
        reponses_salut = [
            "Salut ! Comment puis-je t'aider aujourd'hui ?",
            "Hello 👋 Que puis-je faire pour toi ?",
            "Coucou ! Besoin d'un rapport ou d'une info sur tes ventes ?",
            "Bonjour ! Je suis là pour t'aider avec tes données.",
            "Hey ! Dis-moi ce que tu veux savoir sur ton ERP.",
            "Bienvenue ! Tu veux voir tes stocks ou tes clients ?"
        ]
        if any(s in question for s in salutations):
            bot_answer = random.choice(reponses_salut)
            ChatbotMessage.objects.create(conversation=conversation, sender='bot', text=bot_answer)
            return Response({"answer": bot_answer, "conversation_id": conversation.id})
        # Liste de questions/réponses possibles
        faq = [
            (["nombre de clients", "combien de clients", "total clients"], lambda: f"Vous avez {Client.objects.filter(user=user).count()} clients enregistrés."),
            (["produits en stock", "stock total", "combien de produits"], lambda: f"Il y a {sum(p.stock for p in Produit.objects.filter(user=user))} produits en stock au total."),
            (["dernière vente", "derniere vente", "vente récente", "derniere transaction"], lambda: self._last_vente(user)),
        ]
        for keywords, answer_func in faq:
            for kw in keywords:
                if kw in question or difflib.get_close_matches(kw, [question], n=1, cutoff=0.8):
                    bot_answer = answer_func()
                    ChatbotMessage.objects.create(conversation=conversation, sender='bot', text=bot_answer)
                    return Response({"answer": bot_answer, "conversation_id": conversation.id})
        suggestions = []
        for keywords, _ in faq:
            for kw in keywords:
                if difflib.SequenceMatcher(None, kw, question).ratio() > 0.5:
                    suggestions.append(kw)
        if suggestions:
            bot_answer = f"Je n'ai pas compris, mais vouliez-vous demander : {', '.join(suggestions)} ?"
            ChatbotMessage.objects.create(conversation=conversation, sender='bot', text=bot_answer)
            return Response({"answer": bot_answer, "conversation_id": conversation.id})
        bot_answer = "Désolé, je n'ai pas compris la question. Essayez par exemple : 'nombre de clients', 'produits en stock', 'dernière vente'."
        ChatbotMessage.objects.create(conversation=conversation, sender='bot', text=bot_answer)
        return Response({"answer": bot_answer, "conversation_id": conversation.id})

    def _last_vente(self, user):
        vente = Vente.objects.filter(user=user).order_by('-date').first()
        if vente:
            return f"Dernière vente : {vente.total} FCFA le {vente.date.strftime('%d/%m/%Y')}"
        else:
            return "Aucune vente enregistrée."

class UserListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        user_id = request.data.get('id')
        if not user_id:
            return Response({'error': 'ID requis'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
            if user == request.user:
                return Response({'error': 'Impossible de supprimer votre propre compte.'}, status=status.HTTP_400_BAD_REQUEST)
            username = user.username
            user.delete()
            AdminLog.objects.create(user=request.user, action='Suppression utilisateur', details=f'Utilisateur: {username}')
            return Response({'success': True})
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        user_id = request.data.get('id')
        if not user_id:
            return Response({'error': 'ID requis'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
            is_staff = request.data.get('is_staff')
            is_superuser = request.data.get('is_superuser')
            before_staff = user.is_staff
            before_superuser = user.is_superuser
            if is_staff is not None:
                user.is_staff = is_staff
            if is_superuser is not None:
                user.is_superuser = is_superuser
            user.save()
            # Log l'action
            changes = []
            if is_staff is not None and is_staff != before_staff:
                changes.append(f"is_staff: {before_staff} → {is_staff}")
            if is_superuser is not None and is_superuser != before_superuser:
                changes.append(f"is_superuser: {before_superuser} → {is_superuser}")
            if changes:
                AdminLog.objects.create(user=request.user, action='Modification rôle utilisateur', details=f"Utilisateur: {user.username}, {', '.join(changes)}")
            return Response({'success': True})
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)

class AdminLogListView(generics.ListAPIView):
    queryset = AdminLog.objects.all().order_by('-date')
    serializer_class = AdminLogSerializer
    permission_classes = [IsAdminUser]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def facture_pdf(request, vente_id):
    try:
        if HTML is None:
            return Response({'error': 'WeasyPrint non installé'}, status=500)
        vente = Vente.objects.get(id=vente_id, user=request.user)
        produits = VenteProduit.objects.filter(vente=vente)
        client = vente.client
        # Récupère les paramètres entreprise de l'utilisateur
        entreprise = EntrepriseSettings.objects.filter(user=request.user).first()
        context = {
            'vente': vente,
            'produits': produits,
            'client': client,
            'entreprise': entreprise,
        }
        html_string = render_to_string('facture_template.html', context)
        pdf_file = HTML(string=html_string).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Facture_Vente_{vente.id}.pdf"'
        return response
    except Exception as e:
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=500)

class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EntrepriseSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        obj, created = EntrepriseSettings.objects.get_or_create(user=request.user)
        serializer = EntrepriseSettingsSerializer(obj)
        return Response(serializer.data)

    def put(self, request):
        obj, created = EntrepriseSettings.objects.get_or_create(user=request.user)
        data = request.data.copy()
        serializer = EntrepriseSettingsSerializer(obj, data=data, partial=True)
        if 'logo' in request.FILES:
            serializer.initial_data['logo'] = request.FILES['logo']
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
