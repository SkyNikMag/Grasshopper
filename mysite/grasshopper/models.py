from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import json

class Athlet(models.Model):

    class Gender(models.TextChoices):
        MAN = 'MN', 'Мужчина'
        WOMAN = 'WN', 'Женщина'

    class Rank(models.TextChoices):
        FIRST = 'FR', '1 разряд'
        KMS = 'KM', 'КМС'
        MS = 'MS', 'МС'
        MSMK = 'MK', 'МСМК'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='athletes')
    name = models.CharField('ФИО спортсмена', max_length=250)
    gender = models.CharField(max_length=2,
                              choices=Gender.choices, verbose_name="Пол")

    rank = models.CharField(max_length=2,
                              choices=Rank.choices,
                              default=Rank.FIRST,
                            verbose_name="Разряд")


    date_birthday = models.DateField('Дата рождения спортсмена', null=False)
    team = models.CharField('Название команды', max_length=250)
    region = models.CharField('Регион', max_length=250)
    publish = models.DateTimeField(default=timezone.now)
    results = models.TextField(blank=True, null=True)  # Поле для хранения результатов
    average_result = models.FloatField(null=True, blank=True)
    total_result = models.IntegerField(null=True, blank=True)  # Новое поле для суммы результатов

    objects = models.Manager()

    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def get_results(self):
        if self.results:
            try:
                # Попытка загрузить данные из JSON
                results = json.loads(self.results)
                # Проверка, является ли результат списком
                if isinstance(results, list):
                    return results
                # Если результат - число, упаковать его в список
                return [results]
            except json.JSONDecodeError:
                # Обработка случаев с одиночным числом или некорректным JSON
                return [self.results] if isinstance(self.results, int) else []
        return []

    def set_results(self, results_list):
        self.results = json.dumps(results_list)
        self.average_result = sum(results_list) / len(results_list) if results_list else None
        self.total_result = sum(results_list)  # Обновляем сумму результатов
        self.save()

    def add_result(self, new_result):
        results = self.get_results()
        results.append(new_result)
        self.set_results(results)

    def __str__(self):
        return self.name

class Result(models.Model):
    athlet = models.ForeignKey(Athlet, on_delete=models.CASCADE, related_name='individual_results')
    score = models.PositiveIntegerField('Результат', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.athlet.name} - {self.score}'


