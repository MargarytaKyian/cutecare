from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Category, Product, ReviewRating
from cart.forms import CartAddProductForm
from .forms import ReviewForm
from django.http import HttpResponseRedirect, HttpResponse

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
    review_form = ReviewForm()
    reviews = ReviewRating.objects.filter(product=product, status=True).order_by('-created_at')
    for rev in reviews:
        stars = []
        full = int(rev.rating)
        half = 1 if (rev.rating - full) >= 0.5 else 0
        empty = 5 - full - half
        stars += ['full'] * full
        stars += ['half'] * half
        stars += ['empty'] * empty
        rev.star_list = stars
    return render(request,
                  'main/product/detail.html',
                  {'product': product,
                   'cart_product_form':cart_product_form,
                   'reviews': reviews,
                    'review_form': review_form,
                  })


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


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank You! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank You! Your review has been submitted.')
                return redirect(url)