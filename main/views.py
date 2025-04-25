from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Category, Product
from cart.forms import CartAddProductForm

# Create your views here.

def popular_list(request):
    products = Product.objects.filter(available =True)[:3]
    return render(request,
                  'main/index/index.html',
                  {'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product,
                                slug=slug,
                                available=True)
    cart_product_form = CartAddProductForm
    return render(request,
                  'main/product/detail.html',
                  {'product': product,
                   'cart_product_form':cart_product_form})


def product_list(request, category_slug=None):
    page = request.GET.get('page', 1)
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available =True)
    paginator = Paginator(products, 10)
    current_page = paginator.page(int(page))
    if category_slug:
        category = get_object_or_404(Category,
                                     slug=category_slug)
        paginator = Paginator(products.filter(category=category), 10)
        current_page = paginator.page(int(page))
    return render(request,
                  'main/product/list.html',
                  {'category': category,
                   'categories': categories,
                   'products': current_page,
                   'slug_url': category_slug})


def autocomplete(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse([], safe=False)
    qs = Product.objects.filter(name__icontains=q, available=True)[:10]
    data = [
        {
            'name': prod.name,
            'url': prod.get_absolute_url()
        }
        for prod in qs
    ]
    return JsonResponse(data, safe=False)

def product_search(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.filter(name__icontains=query, available=True) if query else Product.objects.none()
    return render(request, 'main/product/search_results.html', {
        'products': products,
        'query': query
    })