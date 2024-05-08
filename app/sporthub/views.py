from django.shortcuts import render
from django.http import HttpResponse
from .models import Post
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from math import ceil
import folium
import io
import gpxpy
import json

def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'sporthub/home.html', context)


def about(request):
    return render(request, 'sporthub/about.html', {'title': "About Page"})


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'sporthub/home.html'
    context_object_name = 'posts'
    ordering = ["-date_posted"]




import gpxpy
import io
import json

from django.views.generic import DetailView
import folium
import gpxpy

class PostDetailView(DetailView):
    model = Post
    template_name = 'sporthub/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        if post.gpx_data:
            gpx = gpxpy.parse(post.gpx_data)

            # Tworzenie mapy z trasą
            m = folium.Map()

            # Ograniczenie liczby punktów trasy do wyświetlenia
            route_points = gpx.tracks[0].segments[0].points[::35]  # Co 10 punktów

            # Dodanie punktów trasy do mapy
            for point in route_points:
                folium.Marker(
                    [point.latitude, point.longitude],
                    # icon=folium.Icon(icon_size=(10, 10))
                ).add_to(m)

            # Dostosowanie widoku mapy do obszaru zawierającego wszystkie punkty trasy
            if route_points:
                m.fit_bounds([[point.latitude, point.longitude] for point in route_points])

            # Konwersja mapy do HTML i przekazanie do kontekstu
            map_html = m.get_root().render()
            context['map_html'] = map_html

        return context



class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'image', 'gpx_file']

    def form_valid(self, form):
        form.instance.author = self.request.user
        gpx_file = self.request.FILES.get('gpx_file')

        if gpx_file:
            # Odczytaj zawartość pliku GPX i przetwórz ją
            gpx_data = gpx_file.read()
            gpx = gpxpy.parse(gpx_data)

            # Oblicz dystans trasy w kilometrach
            distance_km = gpx.length_3d() / 1000

            # Oblicz czas trasy w sekundach
            time_taken = gpx.get_duration()

            # Przelicz czas na godziny: minuty: sekundy
            hours, remainder = divmod(time_taken, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_taken_str = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))

            # Zapisz dane do modelu Post
            form.instance.gpx_data = gpx_data
            form.instance.distance = distance_km
            form.instance.time_taken = time_taken_str

        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'image']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
