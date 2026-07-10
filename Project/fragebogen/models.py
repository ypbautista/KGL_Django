from django.db import models
import uuid

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Person(models.Model):
    vorname = models.CharField(max_length=100)
    nachname = models.CharField(max_length=100)

    class Meta:
        abstract = True


class JugendlichePerson(Person):

    def __str__(self):
        return f"{self.vorname} {self.nachname}"


class Bezugsperson(Person):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="bezugsperson",
    )

    email = models.EmailField()

    kuerzel = models.CharField(
        max_length=10,
        blank=True,
    )

    def __str__(self):
        return f"{self.vorname} {self.nachname}"


class Fragebogen(models.Model):

    titel = models.CharField(
        max_length=200
    )

    def __str__(self):
        return self.titel


class FragebogenFall(models.Model):

    jugendliche_person = models.ForeignKey(
        JugendlichePerson,
        on_delete=models.CASCADE,
        related_name="faelle",
    )

    fragebogen = models.ForeignKey(
        Fragebogen,
        on_delete=models.CASCADE,
    )

    erstellt_am = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "jugendliche_person",
                    "fragebogen",
                ],
                name="unique_questionnaire_case",
            )
        ]

    def __str__(self):
        return (
            f"{self.jugendliche_person} - "
            f"{self.fragebogen}"
        )

    def selbsteinschaetzung(self):

        return self.einladungen.filter(
            bezugsperson__isnull=True
        ).first()


    def fremdeinschaetzung(self):

        return self.einladungen.filter(
            bezugsperson__isnull=False
        ).first()



class Einladung(models.Model):

    fall = models.ForeignKey(
        FragebogenFall,
        on_delete=models.CASCADE,
        related_name="einladungen",
    )

    code = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    benutzt = models.BooleanField(
        default=False
    )

    bezugsperson = models.ForeignKey(
        Bezugsperson,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )


    def __str__(self):

        if self.bezugsperson:
            return "Fremdeinschätzung"

        return "Selbsteinschätzung"



class FragebogenAntwort(models.Model):

    einladung = models.OneToOneField(
        Einladung,
        on_delete=models.CASCADE,
        related_name="antwort",
    )

    start_time = models.DateTimeField(
        auto_now_add=True
    )

    end_time = models.DateTimeField(
        null=True,
        blank=True,
    )


    def __str__(self):

        if self.einladung.bezugsperson:
            typ = "Fremdeinschätzung"
        else:
            typ = "Selbsteinschätzung"

        return (
            f"{typ} - "
            f"{self.einladung.fall.jugendliche_person}"
        )



class FragebogenAbschnitt(models.Model):

    fragebogen = models.ForeignKey(
        Fragebogen,
        on_delete=models.CASCADE,
        related_name="abschnitte",
    )

    titel = models.CharField(
        max_length=100
    )

    reihenfolge = models.PositiveIntegerField()


    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "fragebogen",
                    "reihenfolge",
                ],
                name="unique_section_order",
            )
        ]



class FrageVorlage(models.Model):

    text = models.TextField(
        max_length=500
    )


class AbschnittFrage(models.Model):

    fragebogen_abschnitt = models.ForeignKey(
        FragebogenAbschnitt,
        on_delete=models.CASCADE,
        related_name="fragen",
    )

    frage_vorlage = models.ForeignKey(
        FrageVorlage,
        on_delete=models.CASCADE,
    )

    reihenfolge = models.PositiveIntegerField()

    def __str__(self):
        return (
            f"{self.fragebogen_abschnitt.titel} - "
            f"Frage {self.reihenfolge}: "
            f"{self.frage_vorlage.text[:50]}"
        )



class AbschnittAntwort(models.Model):

    fragebogen_antwort = models.ForeignKey(
        FragebogenAntwort,
        on_delete=models.CASCADE,
        related_name="abschnitt_antworten",
    )

    fragebogen_abschnitt = models.ForeignKey(
        FragebogenAbschnitt,
        on_delete=models.CASCADE,
    )

    kommentar = models.TextField(
        blank=True
    )



class FrageAntwort(models.Model):

    abschnitt_antwort = models.ForeignKey(
        AbschnittAntwort,
        on_delete=models.CASCADE,
        related_name="antworten",
    )

    frage = models.ForeignKey(
        AbschnittFrage,
        on_delete=models.CASCADE,
    )

    antwort_wert = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(7),
        ]
    )

    def __str__(self):
        return (
            f"{self.abschnitt_antwort.fragebogen_antwort} | "
            f"{self.frage.frage_vorlage.text[:40]} "
            f"= {self.antwort_wert}/7"
        )