from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F, Sum
from django.db.utils import IntegrityError
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from user_home.services import UserServices
from watchers_app.models import TofaProductsRepository, Categorization, TofaProductsOrder,TofaProductsOrderID,bill_id
from accounts_app.models import User
from .serializers import TofaProductsRepositorySerializer, TofaProductsOrderSerializer,TofaProductsOrderIDSerializer
from helper.Logger_Setup import setup_logger
from django.db import transaction


logger = setup_logger('user_home', 'user_home.log')


# Function-Based Views
@login_required(login_url='/login')
def welcome(request):
    total_bill_value = UserServices.get_total_bill_price(request.user)
    wallet=User.objects.get(pk=request.user.id)
    return render(request, "home.html",{'total_bill_value':total_bill_value,'wallet':wallet})


@login_required(login_url='/login')
def services_view(request):
    return HttpResponse('Service View')


@login_required(login_url='/login')
def opinion_view(request):
    return HttpResponse('Opinion View')


@login_required(login_url='/login')
def food_view(request):
    items_in_cart= UserServices.get_items_count_in_cart(request.user)
    submenu_items = None
    selected_submenu = request.GET.get('submenue', '')

    if request.method == 'GET' and selected_submenu:
        submenu_category = get_object_or_404(
            Categorization,
            main_category='Food & Drinks',
            sub_category=selected_submenu
        )
        submenu_items = TofaProductsRepository.objects.filter(
            category=submenu_category,
            item_quantity__gt=0
        )

    elif request.method == 'POST':
        action = request.POST.get('action', '').lower()
        quantity = request.POST.get('quantity')
        item_id = request.POST.get('item_id')

        if not quantity or not quantity.isdigit():
            messages.error(request, 'Invalid quantity')
            return redirect(f'/home/menue/?submenue={selected_submenu}')

        quantity = int(quantity)
        item_obj = get_object_or_404(TofaProductsRepository, pk=item_id)

        if action == 'add_to_cart':
            try:
                UserServices.add_item_to_cart(request.user,item_obj,quantity,increment=True)
                messages.info(request, "Item added to cart successfully")
            except Exception as e:
                messages.error(request, "Failed to add item to cart")
                logger.error(f"Error adding item to cart: {e}")
            return redirect(f'/home/menue/?submenue={item_obj.category.sub_category}')

    menu_headers = Categorization.objects.filter(main_category='Food & Drinks')
    return render(request, 'menue.html', {
        'menue_headers': menu_headers,
        'sub_menues': submenu_items,
        'items_in_cart': items_in_cart
    })


@login_required(login_url='/login')
def cart_view(request):
    if request.method == 'POST':
        action = request.POST.get('action', '').lower()
        item_name = request.POST.get('item_name')
        quantity = request.POST.get('quantity')
        table_number = request.POST.get('table_number')

        # Validate numeric inputs
        quantity = int(quantity) if quantity and quantity.isdigit() else None
        table_number = int(table_number) if table_number and table_number.isdigit() else None

        if not item_name and action in ['update', 'remove']:
            messages.error(request, "No item selected")
            return redirect('/home/cart/')

        try:
            if action == 'update' and quantity:
                UserServices.add_item_to_cart(request.user, item_name, quantity, False)
                messages.info(request, "Item updated successfully")
            elif action == 'remove':
                UserServices.remove_item_from_cart(request.user, item_name)
                messages.info(request, "Item removed successfully")
            elif action == 'execute' and table_number:
                UserServices.send_cart_to_kitchen(request.user, table_number)
                messages.info(request, "Order sent to kitchen")
        except Exception as e:
            messages.error(request, f"Failed to process action: {action}")
            logger.error(f"Cart action '{action}' failed for user {request.user.username}: {e}")

        return redirect('/home/cart/')

    items_in_cart = UserServices.get_items_in_cart(request.user)
    total_price = UserServices.get_total_cart_price(request.user)

    return render(request, 'cart.html', {
        'items_in_cart': items_in_cart,
        'total_price': total_price
    })


@login_required(login_url='/login')
def bill_view(request):
    items_to_be_charged=UserServices.get_items_in_bill(request.user)
    if items_to_be_charged:
        total_bill_value=0
        for i in items_to_be_charged:
            total_bill_value+=i.count*i.item_name.price
        if request.method=="POST":
            try:
                UserServices.request_bill_payment(request.user,total_bill_value)
                messages.info(request,'Bill submitted')
                return redirect('/home/')
            except Exception as e:
                messages.error(request,'Failed to Request for Paymrnt')
                logger.error(f'User {request.user.username} Failed to request payment, Details:{e} ')
        return render(request, 'bill.html', {'items_to_be_charged':items_to_be_charged,'total_bill_value':total_bill_value})
    else:
        messages.info(request,'There are no bills pending')
        return redirect('/home/')

    # API Views
class FoodViewAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            items = TofaProductsRepository.objects.filter(category__exposure=True)
            serializer = TofaProductsRepositorySerializer(items, many=True)
            return Response({'message': 'Items fetched successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Food API error: {e}")
            return Response({'error': 'Failed to fetch items'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CartViewAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            items = UserServices.get_items_in_cart(request.user)
            if items is None:
                return Response({'message': 'Cart is empty'}, status=status.HTTP_404_NOT_FOUND)
            serializer = TofaProductsOrderSerializer(items, many=True)
            return Response({'message': 'Cart items fetched', 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Cart fetch error for {request.user.username}: {e}")
            return Response({'error': 'Failed to fetch cart items'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def post(self, request):
        """
        In this method, we handle both adding/Updating items to the cart and submitting the cart for preparation.
        and for the count update the value is set to the value in the request body.
        If the 'execute' flag is set, we process the cart for preparation.
        """
        # Check for execution flag
        # Normal add-to-cart logic
        serializer = TofaProductsOrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            item_name=serializer.validated_data.get('item_name')
            count=serializer.validated_data.get('count')
            try:
                UserServices.add_item_to_cart(request.user,item_name,count,False)
                return Response({'message':'Update the Cart successfully'},status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f'Faile to add {item_name} in users {request.user.username} for Deatils :{e}')
                return Response({'messsage':' Failed to update The item in the cart'},status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        item_name = request.data.get('item_name')
        try:
            UserServices.remove_item_from_cart(request.user,item_name)
            return Response({'message': 'Item deleted'}, status=status.HTTP_200_OK)
        except IntegrityError as e:
            logger.error(f"Delete error: {e}")
            return Response({'error': 'Failed to delete item'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderAPI(APIView):
    """
    This Method has two functions:
    post: send cart to kitchen
    get: list all served orders
    """
    permission_classes=[IsAuthenticated]

    def get(self,request):
        try:
            active_orders=UserServices.get_active_orders(request.user)
            serializer=TofaProductsOrderIDSerializer(active_orders)
            if serializer.is_valid():
                return Response({'message':'Orders returnen Successfully','data':serializer.data},status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Failed to list orders for user {request.user.username}, Details:{e}')
            return Response({'error':'Orders returnen Successfully'},status=status.HTTP_200_OK)
    def post(self,request):
        serialize=TofaProductsOrderIDSerializer(data=request.data)
        serialize.is_valid(raise_exception=True)
        try:
            UserServices.send_cart_to_kitchen(request.user,serialize.validated_data.get('table_number'))
            return Response({'message':'Yor card send to kitchen'},status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Failed to send Cart of user {request.user.username} for details :{e}')
            return Response({'error':'failed to send Cart to Kitchen'},status=status.HTTP_406_NOT_ACCEPTABLE)

class BillAPI(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            items_to_be_charged=UserServices.get_items_in_bill(request.user)
            serialize=TofaProductsOrderSerializer(items_to_be_charged,many=True)
            return Response({'message':'Successfully retrived Bill view','data':serialize.data},status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Failed to retrive bill details for {request.user.username}, Details:{e}')
            return Response({'error':'failed to request bill'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def post(self,request):
        items_to_be_charged=UserServices.get_items_in_bill(request.user)
        total_bill_value=0
        if items_to_be_charged:
            for i in items_to_be_charged:
                total_bill_value+=i.count*i.item_name.price
            try:
                UserServices.request_bill_payment(request.user,total_bill_value)
                return Response({'messages':'Bill submitted to Cashier'},status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f'Failed to Request for payment for {request.user.username}, Details:{e}')
                return Response({'error':'failed to request bill'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error':'No orders to be billed found'},status=status.HTTP_404_NOT_FOUND)
