from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Category, Product, ReviewRating
from cart.forms import CartAddProductForm
from .forms import ReviewForm
from decimal import Decimal
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Avg, Count, Q, Value, FloatField, Min, Max
from django.db.models.functions import Coalesce

# Create your views here.


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
    sort_by = request.GET.get('sort_by', 'default')
    price_max_filter_str = request.GET.get('price_max')
    selected_rating_filter_str = request.GET.get('rating_filter')

    category = None
    categories = Category.objects.filter(available=True)
    products_qs = Product.objects.filter(available=True).prefetch_related('images', 'reviewrating_set')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, available=True)
        products_qs = products_qs.filter(category=category)

    qs_for_slider_range = products_qs
    price_range_data = qs_for_slider_range.aggregate(min_val=Min('price'), max_val=Max('price'))
    
    slider_min_price = Decimal(price_range_data['min_val'] or 0)
    slider_max_price = Decimal(price_range_data['max_val'] or 2000)

    if slider_max_price <= slider_min_price :
        if slider_min_price > 0 :
            slider_max_price = slider_min_price + Decimal('100.00')
        else:
            slider_max_price = Decimal('2000.00')

    current_price_filter_value = slider_max_price 
    if price_max_filter_str:
        try:
            price_max_decimal = Decimal(price_max_filter_str)
            current_price_filter_value = max(slider_min_price, min(price_max_decimal, slider_max_price))
            products_qs = products_qs.filter(price__lte=price_max_decimal)
        except (ValueError, TypeError):
            pass

    products_qs = products_qs.annotate(
        avg_rating_val=Coalesce(
            Avg('reviewrating__rating', filter=Q(reviewrating__status=True)),
            Value(0.0),
            output_field=FloatField()
        ),
        reviews_count_val=Count('reviewrating', filter=Q(reviewrating__status=True), distinct=True)
    )

    current_rating_filter = None
    if selected_rating_filter_str:
        try:
            rating_threshold = float(selected_rating_filter_str)
            current_rating_filter = int(rating_threshold)
            products_qs = products_qs.filter(avg_rating_val__gte=rating_threshold)
        except ValueError:
            pass

    if sort_by == 'price_asc':
        products_qs = products_qs.order_by('price')
    elif sort_by == 'price_desc':
        products_qs = products_qs.order_by('-price')
    elif sort_by == 'name_asc':
        products_qs = products_qs.order_by('name')
    elif sort_by == 'rating_desc':
        products_qs = products_qs.order_by('-avg_rating_val', '-created') 
    else: 
        products_qs = products_qs.order_by('-created')

    paginator = Paginator(products_qs, 6) 
    current_page_products = paginator.get_page(page)

    for prod in current_page_products.object_list:
        prod.avg_rating = prod.avg_rating_val 
        prod.reviews_count = prod.reviews_count_val

        if prod.avg_rating is not None and prod.reviews_count > 0:
            full_stars = int(round(prod.avg_rating))
            full_stars = max(0, min(5, full_stars)) 
            prod.star_list = ['full'] * full_stars + ['empty'] * (5 - full_stars)
        else:
            prod.star_list = ['empty'] * 5
            prod.avg_rating = 0.0

        prod.is_favorited = False
        if request.user.is_authenticated:
            if hasattr(request.user, 'favorites'):
                prod.is_favorited = request.user.favorites.filter(product=prod).exists()

    sort_labels = {
        'default': 'За замовчуванням',
        'price_asc': 'Ціна: за зростанням',
        'price_desc': 'Ціна: за спаданням',
        'rating_desc': 'За рейтингом',
        'name_asc': 'За назвою (А-Я)',
    }
    selected_sort_label = sort_labels.get(sort_by, 'За замовчуванням')
    
    cart_product_form = CartAddProductForm()

    context = {
        'category': category,
        'categories': categories,
        'products': current_page_products,
        'slug_url': category_slug,
        'selected_sort_option': sort_by,
        'selected_sort_label': selected_sort_label,
        'slider_min_price': slider_min_price,
        'slider_max_price': slider_max_price,
        'current_price_filter': current_price_filter_value,
        'current_rating_filter': current_rating_filter,
        'cart_product_form': cart_product_form,
    }
    return render(request, 'main/product/list.html', context)


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

        product_item.is_favorited = False
        if request.user.is_authenticated:
            if hasattr(request.user, 'favorites'):
                product_item.is_favorited = request.user.favorites.filter(product=product_item).exists()
            
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
    page = request.GET.get('page', 1)
    query = request.GET.get('q', '').strip()

    products_qs = Product.objects.filter(name__icontains=query, available=True) if query else Product.objects.none()

    products_qs = products_qs.annotate(
        avg_rating_val=Coalesce(
            Avg('reviewrating__rating', filter=Q(reviewrating__status=True)),
            Value(0.0),
            output_field=FloatField()
        ),
        reviews_count_val=Count('reviewrating', filter=Q(reviewrating__status=True), distinct=True)
    )

    paginator = Paginator(products_qs, 6)
    current_page_products = paginator.get_page(page)

    for prod in current_page_products.object_list:
        prod.avg_rating = prod.avg_rating_val
        prod.reviews_count = prod.reviews_count_val

        if prod.avg_rating is not None and prod.reviews_count > 0:
            full_stars = int(round(prod.avg_rating))
            full_stars = max(0, min(5, full_stars))
            prod.star_list = ['full'] * full_stars + ['empty'] * (5 - full_stars)
        else:
            prod.star_list = ['empty'] * 5
            prod.avg_rating = 0.0

        prod.is_favorited = False
        if request.user.is_authenticated:
            if hasattr(request.user, 'favorites'):
                prod.is_favorited = request.user.favorites.filter(product=prod).exists()

    cart_product_form = CartAddProductForm()

    return render(request, 'main/product/search_results.html', {
        'products': current_page_products,
        'query': query,
        'cart_product_form': cart_product_form,
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
            

def about_view(request):
    return render(request, 'main/about/about.html')