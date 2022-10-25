"""vnpay_python URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('VNpay', views.VNpayment, name='VNpayment'),
    # url(r'^payment_load$', views.payment_load, name='payment_load'),
    # path('VNpayment_ipn', views.VNpayment_ipn, name='VNpayment_ipn'),
    path('VNpayment_return', views.VNpayment_return, name='VNpayment_return'),
    path('Paypal/', views.Paypal_payments, name='Paypal_payments'),
    path('MoMo/', views.MoMo_payment, name='MoMo_payments'),
    path('MoMo_payment_return', views.MoMo_payment_return, name='MoMo_payment_return'),
    path('order_complete/', views.Paypal_order_complete, name='PaypaL_order_complete'),
    # path('VNpayquery', views.VNquery, name='query'),
    # path('VNpayrefund', views.VNrefund, name='refund'),
]
