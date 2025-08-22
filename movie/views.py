from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie

import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64

# Create your views here.
def home(request):
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()

    return render(request, 'home.html', {'searchTerm':searchTerm, 'movies':movies ,'name': 'Esteban Salazar Orozco'})

def about(request):
    return render(request, 'about.html')

def singup(request):
    email = request.GET.get('email')
    return render(request, 'singup.html', {'email':email})

def statistics_view(request):
    matplotlib.use('Agg')
    
    # Gráfica de películas por año
    years = Movie.objects.values_list('year', flat=True).distinct().order_by('year')
    movie_counts_by_year = {}
    for year in years:
        if year:
            movies_in_year = Movie.objects.filter(year=year)
        else:
            movies_in_year = Movie.objects.filter(year__isnull=True)
            year = "None"
        count = movies_in_year.count()
        movie_counts_by_year[year] = count
    
    # Gráfica de películas por género (primer género)
    movies = Movie.objects.all()
    genre_counts = {}
    
    for movie in movies:
        if movie.genre:
            # Obtener solo el primer género (antes de la primera coma o espacio)
            first_genre = movie.genre.split(',')[0].split(';')[0].strip()
            if first_genre:
                genre_counts[first_genre] = genre_counts.get(first_genre, 0) + 1
    
    # Crear figura con dos subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Gráfica 1: Películas por año
    bar_width = 0.5
    bar_spacing = 0.5
    bar_positions = range(len(movie_counts_by_year))
    
    ax1.bar(bar_positions, movie_counts_by_year.values(), width=bar_width, align='center')
    ax1.set_title('Movies per Year')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Number of movies')
    ax1.set_xticks(bar_positions)
    ax1.set_xticklabels(movie_counts_by_year.keys(), rotation=90)
    
    # Gráfica 2: Películas por género
    if genre_counts:
        genre_names = list(genre_counts.keys())
        genre_values = list(genre_counts.values())
        
        # Ordenar por cantidad de películas (descendente)
        sorted_data = sorted(zip(genre_values, genre_names), reverse=True)
        genre_values, genre_names = zip(*sorted_data)
        
        ax2.bar(range(len(genre_names)), genre_values, width=0.6, align='center')
        ax2.set_title('Movies per Genre')
        ax2.set_xlabel('Genre')
        ax2.set_ylabel('Number of movies')
        ax2.set_xticks(range(len(genre_names)))
        ax2.set_xticklabels(genre_names, rotation=45, ha='right')
    
    # Ajustar el espaciado
    plt.tight_layout()
    
    # Guardar la gráfica en un objeto BytesIO
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    plt.close()

    # Convertir la gráfica a base64
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    # Renderizar la plantilla statistics.html con la gráfica
    return render(request, 'statistics.html', {'graphic': graphic})
