from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    position = models.CharField(max_length=50)
    login = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    departments_filter = models.CharField(max_length=1000)
    black_list = models.CharField(max_length=1000)

    class Meta:
        db_table = "users"

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "department": self.department,
            "position": self.position,
            "login": self.login,
            "image": "http://localhost:8000/api/v1" + self.image.url if self.image is not None else None,
            "rates": [i.to_json() for i in RateHistory.objects.filter(user_id=self.id)]
        }


class Rate(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    speed = models.IntegerField(null=True, blank=True)
    quality = models.IntegerField(null=True, blank=True)
    benevolence = models.IntegerField(null=True, blank=True)
    reviewer_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="reviewer_user_id")
    assessed_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="assessed_user_id")
    date = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        db_table = "rates"

    def to_json(self):
        return {
            "id": self.id,
            "reviewer_user": self.reviewer_user.id,
            "assessed_user": self.assessed_user.id,
            "speed": self.speed,
            "quality": self.quality,
            "benevolence": self.benevolence
        }


class RateHistory(models.Model):
    class EFrequency(models.TextChoices):
        DAY = 'day'
        MONTH = 'month'
        WEEK = 'week'
        ALL_TIME = 'all_time'

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="history_user_id")
    frequency = models.CharField(
        max_length=8,
        choices=EFrequency.choices,
        default=EFrequency.DAY
    )
    speed = models.FloatField()
    quality = models.FloatField()
    benevolence = models.FloatField()

    class Meta:
        db_table = "rates_history"

    def to_json(self):
        return {
            self.frequency: {
                "speed": self.speed,
                "quality": self.quality,
                "benevolence": self.benevolence,
            }
        }
