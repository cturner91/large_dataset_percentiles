from django.db import models


class ValueEntry(models.Model):
    value = models.FloatField()

    def __str__(self) -> str:
        return f'{self.id}: {self.value}'


class IndexedValueEntry(models.Model):
    value = models.FloatField(db_index=True)

    def __str__(self) -> str:
        return f'{self.id}: {self.value}'
