from datetime import datetime
from pyclbr import Class

from django.contrib import messages
from django.contrib.auth import authenticate, login as loginUser, logout as logoutUser
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect

from app.forms import newUserForm, paymentForm
# Create your views here.
from app.forms import newUserForm, paymentForm, updateUserForm, createProductForm
from app.models import Product, Promotion, Comment, PaymentMethod, Payment, ShoppingCart, ShoppingCartItem, \
    Sold
from django.contrib.auth.models import User
from app.forms import *

from app.forms import CommentForm, ProductForm, PromotionForm
from django.db.models import Q
from django.core.paginator import Paginator
import time

carts = {}


def login(request):
    if request.user.is_authenticated:
        return render(request, 'login.html', {}) #1) No client validation  Before: return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('user')
            password = request.POST.get('pass')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                loginUser(request, user)
                messages.success(request, 'Welcome '+ username + '!')

                return redirect('login')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'login.html', context)


def signup(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already registered')
        return redirect('home')
    else:
        form = newUserForm()
        if request.method == 'POST':
            form = newUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                # messages (dict)
                messages.success(request, 'Account was created for ' + user)

                return redirect('login')

        return render(request, 'signup.html', {'form': form})


def logout(request):
    logoutUser(request)
    return redirect('shop')


def usersManagement(request):
    users = User.objects.values()
    return render(request, 'usersManagement.html', {'users': users})


def deleteUser(request, id):
    user = User.objects.get(id=id)
    user.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def updateUser(request):
    tparams = {}
    print(request.user)

    if request.user.is_authenticated:
        if request.method == 'POST':
            form = updateUserForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                username = data['username']
                email = data['email']
                curPass = data['currentPassword']
                #newPass = data['newPassword']
                #newRepeatedPass = data['repeatNewPassword']
                firstName = data['first_name']
                lastName = data['last_name']

                #if newPass != newRepeatedPass:
                #    form = updateUserForm()
                #    tparams['form'] = form
                #    tparams['error'] = "Inserted Passwords Are Not The Same"
                #    return render(request, 'updateUser.html', tparams)
                if request.user.check_password(curPass):

                    user = request.user
                    user.username = username
                    print(firstName)
                    user.first_name = firstName
                    user.last_name = lastName
                    user.email = email
                    #user.set_password(raw_password=newPass)
                    user.save()
                    messages.success(request, 'Username with name  {}  added.'.format(username))

                else:
                    form = updateUserForm()
                    tparams['form'] = form
                    tparams['error'] = "Incorrect Password"
                    return render(request, 'updateUser.html', tparams)

                return redirect('login')
        else:
            initial = { 'first_name':request.user.first_name,
                        'last_name': request.user.last_name,
                        'username':request.user.username,
                        'email': request.user.email,
                        'currentPassword': request.user.password,
                        'newPassword': request.user.password,
                        'repeatNewPassword':request.user.password,
                       }
            form = updateUserForm(initial=initial)

        tparams['form'] = form

        return render(request, 'updateUser.html', tparams)
    return redirect('login')


def productInfo(request, id):
    canRev = False
    product = Product.objects.get(id=id)
    comments = Comment.objects.filter(product=product)
    commentsRating = [c.rating for c in comments]
    avg = 0
    tparams = {}

    if commentsRating != []:
        avg = sum(commentsRating) / len(commentsRating)
    if request.user.is_authenticated:

        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                username = data['userName']
                email = data['userEmail']
                descr = data['description']
                rating = data['rating']

                com = Comment(userName=username, userEmail=email, description=descr, rating=rating)
                com.product = product
                com.save()
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        else:
            form = CommentForm()
        tparams = {}
        shoppingCarts = ShoppingCart.objects.filter(user_id=request.user.id)
        bought = []
        if shoppingCarts:
            for scs in shoppingCarts:
                scis = ShoppingCartItem.objects.filter(cart_id=scs.id)
                bought += [s.product for s in scis]

        if product in bought:
            canRev = True

        tparams['product'] = product
        tparams['comments'] = comments
        tparams['avg'] = round(avg, 1)
        tparams['comNo'] = len(comments)
        tparams['canReview'] = canRev
        tparams['form'] = form
        return render(request, 'productInfo.html', tparams)
    return redirect('login')


def productsManagement(request):
    if request.user.is_authenticated:
        products = None
        if request.user.is_superuser:
            products = Product.objects.all()
        else:
            products = Product.objects.filter(seller=request.user.get_username())
    form = {'products': products}

    return render(request, 'productsManagement.html', form)


def shop(request):
    return render(request, 'shop.html')


def createProduct(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = createProductForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.cleaned_data
                name = data['name']
                price = data['price']
                description = data['description']
                quantity = data['quantity']
                brand = data['brand']
                category = data['category']
                promotion = data['promotion']
                condition = data['condition']
                pr = Product()
                pr.name = name
                pr.condition = condition
                pr.price = price
                pr.description = description
                pr.image = request.FILES["image"]
                pr.quantity = quantity
                if not request.user.is_superuser:
                    seller = request.user.get_username()
                    pr.seller = seller
                stock = True
                if quantity == 0:
                    stock = False
                pr.stock = stock
                pr.brand = brand
                pr.category = category
                pr.promotion = promotion
                pr.save()
                return redirect('productsManagement')
            else:
                print(form.errors)
        else:
            form = createProductForm()

        return render(request, 'createProduct.html', {'form': form})
    return redirect('login')


def updateProduct(request, pk):
    pr = Product.objects.get(id=pk)
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.get_username() == pr.seller:
            if request.method == 'POST':
                form = createProductForm(request.POST, request.FILES)
                if form.is_valid():
                    data = form.cleaned_data
                    name = data['name']
                    price = data['price']
                    description = data['description']
                    quantity = data['quantity']
                    stock = True
                    if quantity == 0:
                        stock = False
                    brand = data['brand']
                    category = data['category']
                    promotion = data['promotion']
                    condition = data['condition']
                    pr.name = name
                    pr.price = price
                    pr.description = description
                    pr.image = request.FILES["image"]
                    pr.quantity = quantity
                    pr.stock = stock
                    pr.brand = brand
                    pr.condition = condition
                    pr.category = category
                    pr.promotion = promotion
                    pr.save()
                    return redirect('productsManagement')
            else:
                form = createProductForm(initial={
                    'name': pr.name,
                    'price': pr.price,
                    'description': pr.description,
                    'image': pr.image,
                    'quantity': pr.quantity,
                    'stock': pr.stock,
                    'brand': pr.brand,
                    'category': pr.category,
                    'promotion': pr.promotion,
                })
        return render(request, 'updateProduct.html', {'form': form})
    return redirect('login')


def deleteComment(request, id):
    comment = Comment.objects.get(id=id)
    comment.delete()
    return redirect('commentsManagement')


def commentsManagement(request):
    comments = Comment.objects.all()
    form = {'comments': comments}
    return render(request, 'commentsManagement.html', form)


def deleteProduct(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    return redirect('productsManagement')


def promotionsManagement(request):
    promotions = Promotion.objects.all()
    form = {'promotions': promotions}
    return render(request, 'promotionsManagement.html', form)

def promotions(request):
    promotions = Product.objects.exclude(promotion__isnull=True)

    form = {'promotions': promotions}
    return render(request, 'promotions.html', form)

def createPromotion(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        form = PromotionForm(request.POST)
        if form.is_valid():
            promotion = Promotion(name=form.cleaned_data["name"],
                                  discount=form.cleaned_data["discount"],
                                  description=form.cleaned_data["description"],
                                  deadline=form.cleaned_data["deadline"],
                                  )
            promotion.save()
            return redirect("promotionsManagement")
    else:
        form = PromotionForm()
    return render(request, 'createPromotion.html', {"form": form})


def updatePromotion(request, promotion_id):
    assert isinstance(request, HttpRequest)
    if request.method == "POST":
        form = PromotionForm(request.POST)
        if form.is_valid():
            promotion = Promotion.objects.get(id=promotion_id)
            promotion.name = form.cleaned_data["name"]
            promotion.discount = form.cleaned_data["discount"]
            promotion.description = form.cleaned_data["description"]
            promotion.deadline = form.cleaned_data["deadline"]
            promotion.save()
            return redirect("promotionsManagement")
    else:
        promotion = Promotion.objects.get(id=promotion_id)
        form = PromotionForm(initial={"name": promotion.name,
                                      "discount": promotion.discount,
                                      "description": promotion.description,
                                      "deadline": promotion.deadline,
                                      })
    return render(request, "updatePromotion.html", {"form": form})


def deletePromotion(request, id):
    promotion = Promotion.objects.get(id=id)
    promotion.delete()
    return redirect('promotionsManagement')


def searchProducts(request):
    time.sleep(3)

    productsBrands = Product.objects.order_by('brand').values_list('brand', flat=True).distinct()
    brands = {}
    for pB in productsBrands:
        brands[pB] = Product.objects.filter(brand=pB).count()

    listCategoriesAndBrands = Product.objects.order_by('category').values_list('category', 'brand').distinct()

    noResults = False
    productsFilter = {}
    for c in listCategoriesAndBrands:
        if c[0] not in productsFilter.keys():
            productsFilter[c[0]] = [c[1]]
        else:
            productsFilter[c[0]].append(c[1])
    sellers = list(set(Product.objects.values_list('seller', flat=True)))
    result = Product.objects.all()
    if request.method == 'POST':
        # home search images click
        if 'Smartphones' in request.POST:
            result = Product.objects.filter(category="Smartphones")
        if 'Televisions' in request.POST:
            result = Product.objects.filter(category="Televisions")
        if 'Drones' in request.POST:
            result = Product.objects.filter(category="Drones")
        if 'Computers' in request.POST:
            result = Product.objects.filter(category="Computers")

        if 'searchBar' in request.POST:
            query = request.POST['searchBar']
            result = Product.objects.filter(name__icontains=query)

        if 'brandsCategories' in request.POST or 'categories' in request.POST or 'stockCheck' in request.POST or 'promotionCheck' in request.POST \
                or 'usedCheck' in request.POST or 'newCheck' in request.POST or 'sellers' in request.POST:
            brandsLstCat = request.POST.getlist('brandsCategories', [])
            categories = request.POST.getlist('categories', [])
            stockCheck = request.POST.getlist('stockCheck', [])
            promotionCheck = request.POST.getlist('promotionCheck', [])
            usedCheck = request.POST.getlist('usedCheck', [])
            newCheck = request.POST.getlist('newCheck', [])
            sellers_ = request.POST.getlist('sellers', [])

            allProducts = Product.objects.all()

            if len(brandsLstCat) != 0:
                allProducts = allProducts.filter(brand__in = brandsLstCat)

            if len(categories)!=0:
                allProducts = allProducts.filter(category__in=categories)

            if len(stockCheck)!=0:
                allProducts = allProducts.filter(stock=True)
            if len(promotionCheck)!=0:
                allProducts = allProducts.exclude(promotion=None)
            if len(usedCheck)!=0:
                allProducts = allProducts.filter(condition='Used')
            if len(newCheck)!=0:
                allProducts = allProducts.filter(condition='New')
            if len(sellers_)!=0:
                print(sellers_)
                allProducts = allProducts.filter(seller__in=sellers_)
            result = allProducts





        if 'minPrice' in request.POST or 'maxPrice' in request.POST:
            print("maxPrice_")
            minPrice = request.POST.get('minPrice', 0)
            if minPrice == '':
                minPrice = 0
            maxPrice_ = request.POST.get('maxPrice', 10000000000000000000000000000000)
            if maxPrice_ == '':
                maxPrice_ = 10000000000000000000000




            allProds = result.exclude(promotion = None)
            resultSearch = [p for p in result.filter(promotion = None, price__range = [minPrice,maxPrice_])]
            for prod in allProds:
                actualPrice = prod.price - prod.price * prod.promotion.discount
                if actualPrice > float(minPrice) and actualPrice < float(maxPrice_):
                    resultSearch.append(prod)
            result = resultSearch


        if len(result) == 0:
            noResults = True

    paginator = Paginator(result, 9)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    tparams = {'productsFilter': productsFilter,
               'totalBrands': Product.objects.values('brand').distinct().count(),
               'totalCategories': Product.objects.values('category').distinct().count(),
               'brands': brands,
               'productsList': page_obj[0:2],
               'noResults': noResults,
               'sellers': sellers

               }

    return render(request, 'shop.html', tparams)


def home(request):
    assert isinstance(request, HttpRequest)
    recommendedProducts = Product.objects.all()[5:8]
    comments = Comment.objects.order_by('userEmail').distinct()


    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(userName=form.cleaned_data["userName"],
                              userEmail=form.cleaned_data["userEmail"],
                              description=form.cleaned_data["description"],
                              rating=form.cleaned_data["rating"],
                              commentDate=datetime.now(),
                              )
            comment.save()
            time.sleep(3)

            return redirect("home")
    else:
        form = CommentForm()
    return render(request, 'index.html',
                  {"form": form, "recommendedProducts": recommendedProducts, "comments": comments})


def account(request):
    if request.user.is_authenticated:
        shoppingCarts = ShoppingCart.objects.filter(user_id=request.user.id)
        print(shoppingCarts)
        creds = getCredits(request)

        if len(shoppingCarts) != 0:
            assoc = []
            for scs in shoppingCarts:
                scis = ShoppingCartItem.objects.filter(cart_id=scs.id)
                payment = Payment.objects.filter(shopping_cart=scs)[0]
                assoc.append((scis, payment))
            print(str(assoc))
            tparams = {'carts': assoc, 'credits': creds}

        else:
            tparams = {'cart': [], 'credits': creds}
        return render(request, 'account.html', tparams)
    return redirect('login')


def getCredits(request):
    if request.user.is_superuser:
        userProducts = Product.objects.filter(seller='TechOn')
        buyer = 'TechOn'
    else:
        username = request.user.get_username()
        userProducts = Product.objects.filter(seller=username)
        buyer = username

    credits = 0
    for pr in userProducts:
        sold = Sold.objects.filter(product=pr)
        for s in sold:
            credits += s.total

    payments = Payment.objects.filter(username=buyer)

    creditDiscount = 0
    for p in payments:
        creditDiscount += p.usedCredits

    return round(credits - creditDiscount, 2)


def checkout(request):
    if request.user.is_authenticated:
        tparams = getShoppingCart(request)

        if request.method == 'POST':
            form = paymentForm(request.POST)

            if form.is_valid():
                if request.user.is_superuser:
                    buyer = 'TechOn'
                else:
                    username = request.user.get_username()
                    buyer = username
                data = form.cleaned_data
                type = data['type']
                card_no = data['card_no']
                useCredits = data['useCredits']

                address = data['address']
                pm = PaymentMethod(type=type, card_no=card_no)
                pm.save()
                sp = ShoppingCart(user_id=request.user.id)
                sp.save()
                payment = Payment()
                payment.address = address
                payment.total = round(tparams['total'], 2)
                payment.method = pm
                payment.shopping_cart = sp
                payment.username = buyer
                if useCredits:
                    creds = getCredits(request)
                    if creds <= payment.total:
                        payment.usedCredits = creds
                    else:
                        payment.usedCredits = payment.total
                payment.save()

                for item, quantity in tparams['cart']:
                    spi = ShoppingCartItem()
                    spi.product = item
                    item.quantity = item.quantity - quantity
                    item.save()

                    # Saving Sell Record
                    s = Sold()
                    s.product = item
                    s.total = round(item.price * quantity, 2)
                    if item.promotion:
                        s.total -= round(s.total * item.promotion.discount, 2)
                    s.promotion = item.promotion
                    s.quantity = quantity
                    s.buyer = request.user.get_username()
                    s.save()

                    if item.quantity == 0:
                        item.stock = False
                    item.save()
                    spi.quantity = quantity
                    spi.cart_id = sp.id
                    spi.save()
                carts[request.user.id] = []
                messages.success(request, username + ' your products were purchased successfully!')

                return redirect('home')
        else:
            try:

                if request.user.is_superuser:
                    username = 'TechOn'
                else:
                    username = request.user.get_username()
                payment = Payment.objects.filter(username=username).order_by('-id')[0]
                form = paymentForm(initial={
                    'type': payment.method.type,
                    'card_no': payment.method.card_no
                })

            except:
                form = paymentForm()
        tparams['form'] = form
        print("OKS")
        return render(request, 'checkout.html', tparams)
    return redirect('login')


def getShoppingCart(request):
    userCart = []
    if request.user.id in carts:
        userCart = carts[request.user.id]
    currentCart = []
    total = 0
    totalDiscount = 0
    userCart.sort(key=lambda a: a[0])
    for item in userCart:
        product = Product.objects.get(id=item[0])
        currentCart.append((product, item[1]))
        total += product.price * item[1]

        if item[1] >= product.quantity:
            item[1] = product.quantity
        if product.promotion:
            totalDiscount += product.price * product.promotion.discount * item[1]
    tparams = {
        'cart': currentCart,
        'subtotal': round(total, 2),
        'discount': round(totalDiscount, 2),
        'total': round(total - totalDiscount, 2),
    }
    return tparams


def addToCart(request, id):
    if request.user.is_authenticated:
        if request.user.id in carts:
            products = [p for p in carts[request.user.id] if str(p[0]) != id]
            curProduct = [p for p in carts[request.user.id] if p not in products]
            if curProduct:
                prod = curProduct[0]
                prod = [id, prod[1] + 1]
                products.append(prod)
                carts[request.user.id] = products
            else:
                carts[request.user.id].append([id, 1])
        else:
            carts[request.user.id] = [[id, 1]]

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('login')


def removeFromCart(request, id):
    if request.user.is_authenticated:
        if request.user.id in carts:
            products = [p for p in carts[request.user.id] if str(p[0]) != id]
            carts[request.user.id] = products
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('login')


def increaseQuantity(request, id):
    if request.user.is_authenticated:
        products = [p for p in carts[request.user.id] if str(p[0]) != id]
        prod = [p for p in carts[request.user.id] if p not in products][0]
        prod = [id, prod[1] + 1]
        products.append(prod)
        carts[request.user.id] = products
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('login')


def decreaseQuantity(request, id):
    if request.user.is_authenticated:
        products = [p for p in carts[request.user.id] if str(p[0]) != id]
        prod = [p for p in carts[request.user.id] if p not in products][0]
        prod = [id, prod[1] - 1]
        products.append(prod)
        carts[request.user.id] = products

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('login')


def cart(request):
    if request.user.is_authenticated:
        tparams = getShoppingCart(request)
        return render(request, 'cart.html', tparams)
    return redirect('login')


def soldManagement(request):
    tparams = {}
    if request.user.is_authenticated:
        if request.user.is_superuser:
            userProducts = Product.objects.filter(seller='TechOn')
        else:
            username = request.user.get_username()
            userProducts = Product.objects.filter(seller=username)
        sold = []
        for pr in userProducts:
            sold += Sold.objects.filter(product=pr)
        tparams['sold'] = sold
        return render(request, 'soldManagement.html', tparams)
    return redirect('login')
