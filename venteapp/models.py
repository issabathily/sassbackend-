from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=30)
    email = models.EmailField()
    adresse = models.CharField(max_length=255)
    totalAchats = models.IntegerField(default=0)
    derniereVisite = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nom

class Produit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    categorie = models.CharField(max_length=100)
    prixAchat = models.IntegerField()
    prixVente = models.IntegerField()
    stock = models.IntegerField()
    stockMin = models.IntegerField()
    unite = models.CharField(max_length=30)

    def __str__(self):
        return self.nom

class Vente(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    total = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=[('en_cours', 'En cours'), ('terminee', 'Terminée'), ('annulee', 'Annulée')])

    def __str__(self):
        return f'Vente {self.id}'

class VenteProduit(models.Model):
    vente = models.ForeignKey(Vente, related_name='produits', on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prixUnitaire = models.IntegerField()

class Depense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    montant = models.IntegerField()
    categorie = models.CharField(max_length=100)
    date = models.DateTimeField()

class MouvementStock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=[('entree', 'Entrée'), ('sortie', 'Sortie')])
    quantite = models.IntegerField()
    motif = models.CharField(max_length=255)
    date = models.DateTimeField()
    stockAvant = models.IntegerField()
    stockApres = models.IntegerField()

class ChatbotConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.title or f"Conversation du {self.created_at.strftime('%d/%m/%Y %H:%M')}"

class ChatbotMessage(models.Model):
    conversation = models.ForeignKey(ChatbotConversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=[('user', 'Utilisateur'), ('bot', 'Bot')])
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.text[:30]}..."

class AdminLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date.strftime('%d/%m/%Y %H:%M')} - {self.user.username} : {self.action} ({self.details})"

class EntrepriseSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    site_web = models.CharField(max_length=255, blank=True)
    siret = models.CharField(max_length=30, blank=True)
    notes_facture = models.TextField(blank=True)

    def __str__(self):
        return self.nom
