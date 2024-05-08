from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import gpxpy
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='post_pics', null=True, blank=True)
    gpx_file = models.FileField(upload_to='gpx_files', null=True, blank=True)
    gpx_data = models.BinaryField(null=True, blank=True)  # BinaryField dla danych GPX
    distance = models.FloatField(null=True, blank=True)  # Pole dla dystansu
    time_taken = models.CharField(max_length=20, null=True, blank=True)  # Pole dla czasu pokonania trasy
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('sporthub-detail', kwargs={'pk': self.pk})

    def process_gpx_file(self):
        if self.gpx_file:
            gpx_data = self.gpx_file.read()
            self.gpx_data = gpx_data  # Przechowywanie danych GPX jako binarne
            gpx = gpxpy.parse(gpx_data)
            self.distance = gpx.length_3d() / 1000  # Długość w kilometrach
            self.duration = gpx.get_duration()

            # Wygenerowanie obrazu śladu .gpx
            fig, ax = plt.subplots()
            for track in gpx.tracks:
                for segment in track.segments:
                    lons = [point.longitude for point in segment.points]
                    lats = [point.latitude for point in segment.points]
                    ax.plot(lons, lats, color='blue', alpha=0.7, linewidth=3)
            ax.set_title('GPX Track')
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.grid(True)
            # Zapisanie obrazu do pamięci
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close(fig)
            buffer.seek(0)
            # Zapisanie obrazu do pola ImageField
            self.image.save('gpx_track.png', Image.open(buffer), save=False)
