from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from app import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    
    path('productsManagement/', views.productsManagement, name='productsManagement'),
    path('createProduct/', views.createProduct, name='createProduct'),
    path('updateProduct/<str:pk>/', views.updateProduct, name='updateProduct'),
    path('deleteProduct/<str:id>', views.deleteProduct, name='deleteProduct'),
    
    path('promotionsManagement/', views.promotionsManagement, name='promotionsManagement'),
    path('createPromotion/', views.createPromotion, name='createPromotion'),
    path('updatePromotion/<str:promotion_id>/', views.updatePromotion, name='updatePromotion'),
    path('deletePromotion/<str:id>', views.deletePromotion, name='deletePromotion'),
    
    path('searchProducts/', views.searchProducts, name='searchProducts'),
    path('details/<str:id>', views.productInfo, name='productInfo'),
    
    path('account/', views.account, name='account'),
    path('sold/', views.soldManagement, name='soldManagement'),
    
    path('commentsManagement/', views.commentsManagement, name='commentsManagement'),
    path('deleteComment/<str:id>', views.deleteComment, name='deleteComment'),
    
    path('shop/', views.shop, name='shop'),
    path('promotions/', views.promotions, name='promotions'),

    path('usersManagement/', views.usersManagement, name='usersManagement'),
    path('deleteUser/<str:id>', views.deleteUser, name='deleteUser'),
    path('updateUser/', views.updateUser, name='updateUser'),

    path('', views.home, name='home'),
    
    path('addToCart/<str:id>', views.addToCart, name='addToCart'),
    path('removeFromCart/<str:id>', views.removeFromCart, name='removeFromCart'),
    path('increaseQuantity/<str:id>', views.increaseQuantity, name='increaseQuantity'),
    path('decreaseQuantity/<str:id>', views.decreaseQuantity, name='decreaseQuantity'),

    path('checkout/', views.checkout, name='checkout'),
    path('cart/', views.cart, name='cart')




]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)