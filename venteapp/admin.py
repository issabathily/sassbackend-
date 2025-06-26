from django.contrib import admin

# Register your models here.
from .models import Vente,VenteProduit,MouvementStock,Client, Produit, ChatbotConversation, ChatbotMessage, AdminLog
admin.site.register(Vente)
admin.site.register(VenteProduit)
admin.site.register(MouvementStock)
admin.site.register(Client)
admin.site.register(Produit)
admin.site.register(ChatbotConversation)
admin.site.register(ChatbotMessage)
admin.site.register(AdminLog)