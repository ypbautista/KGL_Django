from django.db import models
from django.contrib.auth.models import User

class Person(models.Model):
    vorname = models.CharField(max_length=100)
    nachname = models.CharField(max_length=100)

    class Meta:
        abstract = True

class JugendlichePerson(Person):
    def __str__(self):
        return f"{self.vorname} {self.nachname} (Jugendliche Person)"

class Bezugsperson(Person):
    email = models.EmailField(max_length=254, blank=True, null=True)
    def __str__(self):
        return f"{self.vorname} {self.nachname} (Bezugsperson)"

class Fragebogen(models.Model):
    titel = models.CharField(max_length=200)
    
    def __str__(self):
        return self.titel

class Frage(models.Model):
    fragebogen = models.ForeignKey(Fragebogen, on_delete=models.CASCADE, related_name='fragen')
    text = models.TextField(max_length=500)
    kategorie = models.CharField(max_length=100)
    reihenfolge = models.IntegerField()


    def __str__(self):
        return self.text

class FragebogenAntworten(models.Model):
    JugendlichePerson = models.ForeignKey(JugendlichePerson, on_delete=models.CASCADE, related_name='responses')
    BEWERTET_VON_CHOICES = [
        ('JugendlichePerson', 'Jugendliche Person'),
        ('Bezugsperson', 'Bezugsperson'),
    ]
    bewertet_von = models.CharField(max_length=20, choices=BEWERTET_VON_CHOICES)
    Bezugsperson = models.ForeignKey(Bezugsperson, on_delete=models.CASCADE, null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fragebogen von {self.bewertet_von} für Jugendliche Person {self.JugendlichePerson}"

class PartResponse(models.Model):
    FragebogenAntworten = models.ForeignKey(FragebogenAntworten, on_delete=models.CASCADE, related_name='parts')
    frage = models.ForeignKey(Frage, on_delete=models.CASCADE)
    antwort_wert = models.IntegerField() 
    kommentar = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.frage.text[:20]}...: {self.antwort_wert}"