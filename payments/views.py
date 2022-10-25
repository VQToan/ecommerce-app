import hashlib
import hmac
import json
import random
import string
import uuid
from datetime import datetime

import requests
from carts.models import CartItem
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from orders.models import Order, Payment, OrderProduct
from store.models import Product

from .forms import PaymentForm
from .vnpay import vnpay


# def hmacsha512(key, data):
#     byteKey = key.encode('utf-8')
#     byteData = data.encode('utf-8')
#     return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()

@login_required(login_url="login")
def VNpayment(request):
    if request.method == 'POST':
        # Process input data and build url payment
        form = PaymentForm(request.POST)
        if form.is_valid():
            order_type = 'billpayment'
            order_id = form.cleaned_data['order_id']
            amount = form.cleaned_data['amount']
            order_desc = form.cleaned_data['order_desc']
            bank_code = form.cleaned_data['bank_code']
            language = form.cleaned_data['language']
            ipaddr = get_client_ip(request)
            # Build URL Payment
            vnp = vnpay()
            vnp.requestData['vnp_Version'] = '2.1.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
            vnp.requestData['vnp_Amount'] = amount * 100
            vnp.requestData['vnp_CurrCode'] = 'VND'
            vnp.requestData['vnp_TxnRef'] = order_id
            vnp.requestData['vnp_OrderInfo'] = order_desc
            vnp.requestData['vnp_OrderType'] = order_type
            # Check language, default: vn
            if language and language != '':
                vnp.requestData['vnp_Locale'] = language
            else:
                vnp.requestData['vnp_Locale'] = 'vn'
                # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
            if bank_code and bank_code != "":
                vnp.requestData['vnp_BankCode'] = bank_code

            vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
            vnp.requestData['vnp_IpAddr'] = ipaddr
            vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
            vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
            return redirect(vnpay_payment_url)
        else:
            print("Form input not validate")
    else:
        return render(request, "payments/VNPay/payment.html")


# def VNpayment_ipn(request):
#     inputData = request.GET
#     if inputData:
#         vnp = vnpay()
#         vnp.responseData = inputData.dict()
#         order_id = inputData['vnp_TxnRef']
#         amount = inputData['vnp_Amount']
#         order_desc = inputData['vnp_OrderInfo']
#         vnp_TransactionNo = inputData['vnp_TransactionNo']
#         vnp_ResponseCode = inputData['vnp_ResponseCode']
#         vnp_TmnCode = inputData['vnp_TmnCode']
#         vnp_PayDate = inputData['vnp_PayDate']
#         vnp_BankCode = inputData['vnp_BankCode']
#         vnp_CardType = inputData['vnp_CardType']
#         if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
#             # Check & Update Order Status in your Database
#             # Your code here
#             firstTimeUpdate = True
#             totalamount = True
#             if totalamount:
#                 if firstTimeUpdate:
#                     if vnp_ResponseCode == '00':
#                         print('Payment Success. Your code implement here')
#                     else:
#                         print('Payment Error. Your code implement here')
#
#                     # Return VNPAY: Merchant update success
#                     result = JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
#                 else:
#                     # Already Update
#                     result = JsonResponse({'RspCode': '02', 'Message': 'Order Already Update'})
#             else:
#                 # invalid amount
#                 result = JsonResponse({'RspCode': '04', 'Message': 'invalid amount'})
#         else:
#             # Invalid Signature
#             result = JsonResponse({'RspCode': '97', 'Message': 'Invalid Signature'})
#     else:
#         result = JsonResponse({'RspCode': '99', 'Message': 'Invalid request'})
#
#     return result

@login_required(login_url="login")
def VNpayment_return(request):
    inputData = request.GET
    # print(inputData)
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = int(inputData['vnp_Amount']) / 100
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']

        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                payment, order = payments_success(request, order_id, 'VNpay', 'COMPLETED')
                try:
                    ordered_products = OrderProduct.objects.filter(order_id=order.id)

                    subtotal = 0
                    for i in ordered_products:
                        subtotal += i.product_price * i.quantity
                    context = {
                        'order': order,
                        'ordered_products': ordered_products,
                        'order_number': order.order_number,
                        'transID': payment.payment_id,
                        'payment': payment,
                        'subtotal': subtotal,
                    }
                    return render(request, 'orders/order_complete.html', context)
                except Exception:
                    return redirect('home')

            else:
                payments_success(request, order_id, 'VNpay', 'PENDING')
                return render(request, "payments/VNPay/payment_return.html", {"title": "Kết quả thanh toán",
                                                                              "result": "Lỗi", "order_id": order_id,
                                                                              "amount": amount,
                                                                              "order_desc": order_desc,
                                                                              "vnp_TransactionNo": vnp_TransactionNo,
                                                                              "vnp_ResponseCode": vnp_ResponseCode})
        else:
            payments_success(request, order_id, 'VNpay', 'PENDING')
            return render(request, "payments/VNPay/payment_return.html",
                          {"title": "Kết quả thanh toán", "result": "Lỗi", "order_id": order_id, "amount": amount,
                           "order_desc": order_desc, "vnp_TransactionNo": vnp_TransactionNo,
                           "vnp_ResponseCode": vnp_ResponseCode, "msg": "Sai checksum"})
    else:
        return render(request, "payments/VNPay/payment_return.html", {"title": "Kết quả thanh toán", "result": ""})


def payments_success(request, order_id, method, status):
    current_date = datetime.now().strftime('%Y%m%d%H%M%S')
    order_number = current_date + str(request.META.get('REMOTE_ADDR'))
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_id)
    cart_items = CartItem.objects.filter(user=request.user)
    if method == 'PENDING':
        payment = Payment(
            user=request.user,
            payment_id=order_number,
            payment_method='VNPay',
            amount_paid=order.order_total,
            status='PENDING'
        )
        payment.save()
        order.payment = payment
        order.is_ordered = False
        order.save()
    if status == 'COMPLETED':
        payment = Payment(
            user=request.user,
            payment_id=order_number,
            payment_method=method,
            amount_paid=order.order_total,
            status=status
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()
        for item in cart_items:
            order_product = OrderProduct()
            order_product.order_id = order.id
            order_product.payment = payment
            order_product.user_id = request.user.id
            order_product.product_id = item.product_id
            order_product.quantity = item.quantity
            order_product.product_price = item.product.price
            order_product.ordered = True
            order_product.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            order_product = OrderProduct.objects.get(id=order_product.id)
            order_product.variations.set(product_variation)
            order_product.save()

            # Reduce the quantity of the sold products
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        # Xóa hết cart_item
        CartItem.objects.filter(user=request.user).delete()
        return payment, order

@login_required(login_url='login')
def Paypal_order_complete(request):
    order_number = request.GET.get('order_number')
    payment, order = payments_success(request, order_number, 'Paypal', 'COMPLETED')
    try:
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except Exception:
        return redirect('home')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required(login_url='login')
def Paypal_payments(request):
    try:
        if request.is_ajax() and request.method == 'POST':
            data = request.POST
            order_id = data['orderID']
            trans_id = data['transID']
            payment_method = data['payment_method']
            status = data['status']

            # Lấy bản ghi order
            order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_id)
            # Tạo 1 bản ghi payment
            payment = Payment(
                user=request.user,
                payment_id=trans_id,
                payment_method=payment_method,
                amount_paid=order.order_total,
                status=status,
            )
            payment.save()
            order.payment = payment
            order.is_ordered = False
            order.save()
            # Phản hồi lại ajax
            data = {
                'order_number': order.order_number,
                'transID': payment.payment_id,
            }
        return JsonResponse({"data": data}, status=200)
    except Exception as e:
        return JsonResponse({"error": e}, status=400)


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    print("Random string of length", length, "is:", result_str)


@login_required(login_url='login')
def MoMo_payment(request):
    if request.method == 'POST':
        # Process input data and build url payment
        form = PaymentForm(request.POST)
        if form.is_valid():
            orderId = form.cleaned_data['order_id']
            amount = form.cleaned_data['amount']
            endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
            partnerCode = "MOMO"
            accessKey = "F8BBA842ECF85"
            secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
            orderInfo = form.cleaned_data['order_desc']
            redirectUrl = settings.MOMO_RETURN_URL
            requestId = str(uuid.uuid4())
            ipnUrl = settings.MOMO_RETURN_URL
            requestType = "payWithMethod"
            extraData = ""
            # print(ipnUrl)
            rawSignature = "accessKey=" + accessKey + "&amount=" + str(amount) + "&extraData=" + extraData + "&ipnUrl=" \
                           + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode \
                           + "&redirectUrl=" + redirectUrl + "&requestId=" + requestId + "&requestType=" + requestType
            h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
            signature = h.hexdigest()
            data = {
                'partnerCode': partnerCode,
                'partnerName': "Test",
                'storeId': "MomoTestStore",
                'requestId': requestId,
                'amount': amount,
                'orderId': orderId,
                'orderInfo': orderInfo,
                'redirectUrl': redirectUrl,
                'ipnUrl': ipnUrl,
                'lang': "vi",
                'extraData': extraData,
                'requestType': requestType,
                'signature': signature
            }
            data = json.dumps(data)
            clen = len(data)
            response = requests.post(endpoint, data=data,
                                     headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
            # print(response.json())
            if response.status_code == 200:
                response = response.json()
                if response['resultCode'] == 0:
                    return redirect(response['payUrl'])
                else:
                    return HttpResponse(response['message'])
            else:
                return HttpResponse("Error")

@login_required(login_url='login')
def MoMo_payment_return(request):
    if request.method == 'GET':
        data = request.GET
        if data['resultCode'] == '0':
            payment, order = payments_success(request, data['orderId'], 'MoMo', 'COMPLETED')
            try:
                ordered_products = OrderProduct.objects.filter(order_id=order.id)

                subtotal = 0
                for i in ordered_products:
                    subtotal += i.product_price * i.quantity
                context = {
                    'order': order,
                    'ordered_products': ordered_products,
                    'order_number': order.order_number,
                    'transID': payment.payment_id,
                    'payment': payment,
                    'subtotal': subtotal,
                }
                return render(request, 'orders/order_complete.html', context)
            except Exception:
                return redirect('home')
