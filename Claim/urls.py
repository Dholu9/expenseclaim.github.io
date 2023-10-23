from django.urls import path
from django.contrib import admin
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('',views.index,name="index"),
    path('logout/',views.logout_user,name="logout"),
    path('newclaim/',views.newclaim,name="newclaim"),
    path('addclaim/',views.addclaim,name="addclaim"),
    path('saverecord/',views.saverecord,name="saverecord"),
    path('entereddata/', views.entereddata, name='entereddata'),
    path('teams/',views.teams,name="teams"),
    path('associate/',views.associate,name="associate"),
    path('demo/<str:username>/', views.demo, name='demo'),
    path('demo2/<int:ClaimNumber>/',views.demo2,name="demo2"),
    path('entereddata2/<int:ClaimNumber>/',views.entereddata2,name="entereddata2"),
    path('entereddata3/<int:ClaimNumber>/',views.entereddata3,name="entereddata3"),
    path('showclaim/<int:ClaimNumber>/', views.showclaim, name='showclaim'),
    path('review_claim/<int:ClaimNumber>/',views.review_claim,name="review_claim"),
    path('accountsview/<str:username>/',views.accountsview,name="accountsview"),
    path('accountsreview/<int:ClaimNumber>/',views.accountsreview,name="accountsreview"),
    path('updaterecord/<int:ClaimNumber>/',views.updaterecord, name='updaterecord'),
    # path('delete_receipt/<str:ReceiptNumber>/', views.delete_receipt, name='delete_receipt'),   
    path('paymentreview/<int:ClaimNumber>/',views.paymentreview,name="paymentreview"),
    path('claims/',views.claims,name="claims"),
    path('view_child_history/',views.view_child_history,name="view_child_history"),

    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
