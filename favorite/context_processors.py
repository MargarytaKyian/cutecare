from .models import Favorite 

def favorite(request):
    if request.user.is_authenticated:
        user_favorites_queryset = request.user.favorites.all() 
        return {'favorite': user_favorites_queryset}

    return {'favorite': []}