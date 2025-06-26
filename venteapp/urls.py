from django.urls import path
from .views import ChatbotView, ChatbotConversationListView, ChatbotConversationDetailView, UserListView, AdminLogListView, facture_pdf, UserProfileView, EntrepriseSettingsView

urlpatterns = [
    path('', ChatbotView.as_view(), name='chatbot'),  # POST /api/chatbot/
    path('conversations/', ChatbotConversationListView.as_view(), name='chatbot-conversations'),  # GET /api/chatbot/conversations/
    path('conversations/<int:pk>/', ChatbotConversationDetailView.as_view(), name='chatbot-conversation-detail'),  # GET /api/chatbot/conversations/<id>/
    path('users/', UserListView.as_view(), name='user-list'),  # GET /api/users/ (admin only)
    path('admin-logs/', AdminLogListView.as_view(), name='admin-log-list'),  # GET /api/admin-logs/ (admin only)
    path('ventes/<int:vente_id>/facture-pdf/', facture_pdf, name='facture-pdf'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('entreprise-settings/', EntrepriseSettingsView.as_view(), name='entreprise-settings'),
] 