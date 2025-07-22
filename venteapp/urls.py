from django.urls import path
from .views import ChatbotView, ChatbotConversationListView, ChatbotConversationDetailView, UserListView, AdminLogListView, facture_pdf, UserProfileView, EntrepriseSettingsView, ventes_par_mois, ventes_par_jour, produits_populaires, stock_par_categorie, tendances_ventes
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),  # POST /api/chatbot/
    path('chatbot/conversations/', ChatbotConversationListView.as_view(), name='chatbot-conversations'),  # GET /api/chatbot/conversations/
    path('chatbot/conversations/<int:pk>/', ChatbotConversationDetailView.as_view(), name='chatbot-conversation-detail'),  # GET /api/chatbot/conversations/<id>/
    path('users/', UserListView.as_view(), name='user-list'),  # GET /api/users/ (admin only)
    path('admin-logs/', AdminLogListView.as_view(), name='admin-log-list'),  # GET /api/admin-logs/ (admin only)
    path('ventes/<int:vente_id>/facture-pdf/', facture_pdf, name='facture-pdf'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('entreprise-settings/', EntrepriseSettingsView.as_view(), name='entreprise-settings'),
    path('ventes-par-mois/', ventes_par_mois, name='ventes-par-mois'),
    path('ventes-par-jour/', ventes_par_jour, name='ventes-par-jour'),
    path('produits-populaires/', produits_populaires, name='produits-populaires'),
    path('stock-par-categorie/', stock_par_categorie, name='stock-par-categorie'),
    path('tendances-ventes/', tendances_ventes, name='tendances-ventes'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 