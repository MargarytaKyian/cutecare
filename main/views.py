from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Category, Product, ReviewRating
from cart.forms import CartAddProductForm
from .forms import ReviewForm
from decimal import Decimal
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Avg, Count, Q, Value, FloatField
from django.db.models.functions import Coalesce

# Create your views here.

def popular_list(request):
    products = Product.objects.filter(available=True)[:3]
    for product in products:
        average_rating = ReviewRating.objects.filter(product=product, status=True).aggregate(avg_rating=Avg('rating'))['avg_rating']
        product.avg_rating = average_rating if average_rating is not None else 0
        product.star_list = ['full'] * int(product.avg_rating) + ['empty'] * (5 - int(product.avg_rating))
    return render(request,
                  'main/index/index.html',
                  {'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product,
                                slug=slug,
                                available=True)
    cart_product_form = CartAddProductForm()
    review_form = ReviewForm()
    reviews = ReviewRating.objects.filter(product=product, status=True).order_by('-created_at')
    
    is_favorited = False
    if request.user.is_authenticated:
        if hasattr(request.user, 'favorites'):
            is_favorited = request.user.favorites.filter(product=product).exists()
    product_rating_stats = ReviewRating.objects.filter(product=product, status=True).aggregate(
        avg_rating=Coalesce(Avg('rating'), Value(0.0), output_field=FloatField()),
        review_count=Count('id')
    )

    if product_rating_stats['review_count'] > 0:
        product.avg_rating = product_rating_stats['avg_rating']
        full_stars_count = round(product.avg_rating) 
        product.star_list = []
        for i in range(1, 6): 
            if i <= full_stars_count:
                product.star_list.append('full')
            else:
                product.star_list.append('empty')
    else:
        product.avg_rating = 0.0 
        product.star_list = None

    for rev in reviews:
        stars = []
        full = int(rev.rating)
        has_half_star = 0
        decimal_part = rev.rating - full
        if decimal_part >= 0.75:
            full +=1
            empty_stars_for_review = 5 - full
        elif decimal_part >= 0.25:
            has_half_star = 1
            empty_stars_for_review = 5 - full - has_half_star
        else:
            empty_stars_for_review = 5 - full

        stars += ['full'] * full
        if has_half_star:
            stars.append('half')
        stars += ['empty'] * empty_stars_for_review
        rev.star_list = stars
    
    context = {
        'product': product,
        'cart_product_form': cart_product_form,
        'reviews': reviews,
        'review_form': review_form,
        'is_favorited': is_favorited,
    }
    return render(request, 'main/product/detail.html', context)


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



def popular_list(request):
    all_available_products = Product.objects.filter(available=True).annotate(
        calculated_avg_rating=Coalesce(
            Avg('reviewrating__rating',
                filter=Q(reviewrating__status=True)),
            Value(0.0),
            output_field=FloatField()
        )
    )

    top_three_products = all_available_products.order_by('-calculated_avg_rating')[:3]

    for product_item in top_three_products:
        product_item.avg_rating = product_item.calculated_avg_rating
        
        rating_value = product_item.avg_rating if product_item.avg_rating is not None else 0
        full_stars_count = int(round(rating_value))
        
        empty_stars_count = 5 - full_stars_count
        if empty_stars_count < 0:
            empty_stars_count = 0
            full_stars_count = 5
            
        product_item.star_list = ['full'] * full_stars_count + ['empty'] * empty_stars_count

        if request.user.is_authenticated:
            try:
                if hasattr(request.user, 'favorites'):
                     product_item.is_favorited = request.user.favorites.filter(id=product_item.id).exists()
                else:
                    product_item.is_favorited = False
            except AttributeError:
                product_item.is_favorited = False
        else:
            product_item.is_favorited = False
            
    cart_form = CartAddProductForm()

    context = {
        'products': top_three_products,
        'cart_product_form': cart_form,
    }
    
    return render(request, 'main/index/index.html', context)


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