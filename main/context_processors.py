from .models import Category

def common_data(request):
    categories = Category.objects.filter(available=True)
    return {
        'categories': categories,
    }