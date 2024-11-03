import random
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
import gpxpy
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='post_pics', null=True, blank=True)
    gpx_file = models.FileField(upload_to='gpx_files', null=True, blank=True)
    gpx_data = models.BinaryField(null=True, blank=True)  # BinaryField dla danych GPX
    distance = models.FloatField(null=True, blank=True)  # Pole dla dystansu
    time_taken = models.CharField(max_length=20, null=True, blank=True)  # Pole dla czasu pokonania trasy
    avg_heart_rate = models.IntegerField(null=True, blank=True)  # Średnie tętno
    calories = models.IntegerField(null=True, blank=True)  # Spalone kalorie
    avg_speed = models.FloatField(null=True, blank=True)  # Średnia prędkość
    cadence = models.IntegerField(null=True, blank=True)  # Kadencja
    max_heart_rate = models.IntegerField(null=True, blank=True)  # Maksymalne tętno
    avg_power = models.FloatField(null=True, blank=True)  # Średnia moc
    max_power = models.FloatField(null=True, blank=True)  # Maksymalna moc
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('sporthub-detail', kwargs={'pk': self.pk})

    def process_gpx_file(self):
        # Sprawdzenie, czy plik GPX istnieje
        if self.gpx_file:
            # Wczytaj dane GPX
            gpx_data = self.gpx_file.read()
            gpx = gpxpy.parse(gpx_data)

            # Obliczanie dystansu
            self.distance = gpx.length_3d() / 1000  # Dystans w kilometrach

            # Obliczanie czasu trwania
            start_time = gpx.get_time_bounds().start_time
            end_time = gpx.get_time_bounds().end_time
            if start_time and end_time:
                duration = end_time - start_time
                self.time_taken = str(duration)
                # Obliczanie średniej prędkości
                self.avg_speed = self.distance / (duration.total_seconds() / 3600)  # km/h

    def generate_default_data(self):
        """jeżeli brak danych"""
        if self.distance is None:
            self.distance = random.uniform(5.0, 50.0)  # km

        if self.time_taken is None:
            self.time_taken = self._generate_random_time()

        if self.avg_speed is None and self.distance and self.time_taken:
            self.avg_speed = self.calculate_avg_speed()

        if self.avg_heart_rate is None:
            self.avg_heart_rate = self.generate_random_heart_rate()

        if self.calories is None:
            self.calories = self.generate_random_calories()

        if self.cadence is None:
            self.cadence = random.randint(60, 100)  # rpm

        if self.max_heart_rate is None:
            self.max_heart_rate = random.randint(150, 200)  # bpm

        if self.avg_power is None:
            self.avg_power = self.generate_random_avg_power()

        if self.max_power is None:
            self.max_power = self.generate_random_max_power()

    def _generate_random_time(self):
        """Generate a random time string in HH:MM:SS format."""
        hours = random.randint(0, 2)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def calculate_avg_speed(self):
        """Calculate average speed if distance and time_taken are available."""
        if self.distance and self.time_taken:
            try:
                time_seconds = self._parse_time_to_seconds(self.time_taken)
                return self.distance / (time_seconds / 3600)  # km/h
            except ValueError:
                return 0
        return 0

    def _parse_time_to_seconds(self, time_str):
        """Convert time string to seconds."""
        time_parts = time_str.split(':')
        if len(time_parts) == 2:  # HH:MM format
            return int(time_parts[0]) * 3600 + int(time_parts[1]) * 60
        elif len(time_parts) == 3:  # HH:MM:SS format
            return int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
        return 0

    def generate_random_heart_rate(self):
        return random.randint(120, 180)

    def generate_random_calories(self):
        return random.randint(300, 800)

    def generate_random_avg_power(self):
        return round(random.uniform(200, 300), 2)

    def generate_random_max_power(self):
        return random.randint(300, 500)

    def save(self, *args, **kwargs):
        """Override save method to process GPX file and generate default data if fields are empty."""
        if self.gpx_file:
            self.process_gpx_file()
        self.generate_default_data()
        super().save(*args, **kwargs)
