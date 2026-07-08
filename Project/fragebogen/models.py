from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

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
    kuerzel = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.vorname} {self.nachname} (Bezugsperson)"

class Fragebogen(models.Model):
    titel = models.CharField(max_length=200)

    def __str__(self):
        return self.titel

class FragebogenAbschnitt(models.Model):
    fragebogen = models.ForeignKey(Fragebogen, on_delete=models.CASCADE, related_name="abschnitte")
    titel = models.CharField(max_length=100)
    reihenfolge = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.fragebogen.titel} - {self.titel}"

class FrageVorlage(models.Model):
    text = models.TextField(max_length=500)

    def __str__(self):
        return self.text[:50]

class AbschnittFrage(models.Model):
    fragebogen_abschnitt = models.ForeignKey(FragebogenAbschnitt, on_delete=models.CASCADE, related_name="fragen")
    frage_vorlage = models.ForeignKey(FrageVorlage, on_delete=models.CASCADE, related_name="verwendungen")
    reihenfolge = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.fragebogen_abschnitt.titel}: {self.frage_vorlage.text[:30]}"

class FragebogenAntwort(models.Model):
    fragebogen = models.ForeignKey(Fragebogen, on_delete=models.CASCADE)
    jugendliche_person = models.ForeignKey(JugendlichePerson, on_delete=models.CASCADE, related_name="fragebogen_antworten")
    bewertet_von = models.CharField(max_length=20, choices=[('JugendlichePerson', 'Jugendliche Person'), ('Bezugsperson', 'Bezugsperson')])
    bezugsperson = models.ForeignKey(Bezugsperson, on_delete=models.CASCADE, null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.fragebogen.titel} - {self.jugendliche_person.vorname} {self.jugendliche_person.nachname}"

class AbschnittAntwort(models.Model):
    fragebogen_antwort = models.ForeignKey(FragebogenAntwort, on_delete=models.CASCADE, related_name="abschnitt_antworten")
    fragebogen_abschnitt = models.ForeignKey(FragebogenAbschnitt, on_delete=models.CASCADE)
    kommentar = models.TextField(blank=True)

    def __str__(self):
        return f"Antwort: {self.fragebogen_abschnitt.titel}"

class FrageAntwort(models.Model):
    abschnitt_antwort = models.ForeignKey(AbschnittAntwort, on_delete=models.CASCADE, related_name="antworten")
    frage = models.ForeignKey(AbschnittFrage, on_delete=models.CASCADE)
    antwort_wert = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)])
    motivations_wert = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)], null=True, blank=True)