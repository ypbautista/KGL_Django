import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Person(models.Model):
    vorname = models.CharField(max_length=100)
    nachname = models.CharField(max_length=100)

    class Meta:
        abstract = True


class JugendlichePerson(Person):

    class Meta:
        verbose_name = "Jugendliche Person"
        verbose_name_plural = "Jugendliche Personen"

    def __str__(self):
        return f"{self.vorname} {self.nachname}"


class Bezugsperson(Person):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="bezugsperson",
        null=True,  
        blank=True, 
    )

    email = models.EmailField()

    kuerzel = models.CharField(
        max_length=10,
        blank=True,
    )

    class Meta:
        verbose_name = "Bezugsperson"
        verbose_name_plural = "Bezugspersonen"

    def __str__(self):
        return f"{self.vorname} {self.nachname}"


class Fragebogen(models.Model):

    titel = models.CharField(
        max_length=200
    )

    class Meta:
        verbose_name = "Fragebogen"
        verbose_name_plural = "Fragebögen"

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
        ordering = ["-erstellt_am"]
        verbose_name = "Fragebogen-Fall"
        verbose_name_plural = "Fragebogen-Fälle"

    def __str__(self):
        return f"{self.jugendliche_person} - {self.fragebogen}"

    def selbsteinschaetzung(self):
        for einladung in self.einladungen.all():
            if einladung.bezugsperson_id is None:
                return einladung
        return None

    def fremdeinschaetzung(self):
        for einladung in self.einladungen.all():
            if einladung.bezugsperson_id is not None:
                return einladung
        return None


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

    class Meta:
        verbose_name = "Einladung"
        verbose_name_plural = "Einladungen"

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

    class Meta:
        verbose_name = "Fragebogen-Antwort"
        verbose_name_plural = "Fragebogen-Antworten"

    def __str__(self):
        if self.einladung.bezugsperson:
            typ = "Fremdeinschätzung"
        else:
            typ = "Selbsteinschätzung"

        return f"{typ} - {self.einladung.fall.jugendliche_person}"


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
        verbose_name = "Fragebogen-Abschnitt"
        verbose_name_plural = "Fragebogen-Abschnitte"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "fragebogen",
                    "reihenfolge",
                ],
                name="unique_section_order",
            )
        ]

    def __str__(self):
        return f"{self.fragebogen.titel} | Abschnitt: {self.titel}"


class FrageVorlage(models.Model):

    text = models.TextField(
        max_length=500
    )

    class Meta:
        verbose_name = "Frage-Vorlage"
        verbose_name_plural = "Frage-Vorlagen"

    def __str__(self):
        return self.text[:50] + "..." if len(self.text) > 50 else self.text


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

    class Meta:
        verbose_name = "Abschnitts-Frage"
        verbose_name_plural = "Abschnitts-Fragen"

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

    class Meta:
        verbose_name = "Abschnitts-Antwort"
        verbose_name_plural = "Abschnitts-Antworten"

    def __str__(self):
        return f"{self.fragebogen_antwort} -> {self.fragebogen_abschnitt.titel}"


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

    class Meta:
        verbose_name = "Frage-Antwort"
        verbose_name_plural = "Frage-Antworten"

    def __str__(self):
        return (
            f"{self.abschnitt_antwort.fragebogen_antwort} | "
            f"{self.frage.frage_vorlage.text[:40]} "
            f"= {self.antwort_wert}/7"
        )