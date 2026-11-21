from django.db import models


class Divisa(models.TextChoices):
    PEN = "PEN", "Soles"
    USD = "USD", "Dólares"
