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

from watchers_app.models import TofaProductsRepository, Categorization, TofaProductsOrder,TofaProductsOrderID
from accounts_app.models import User
from .serializers import TofaProductsRepositorySerializer, TofaProductsOrderSerializer
from helper.Logger_Setup import setup_logger
from django.db import transaction


logger = setup_logger('user_home', 'user_home.log')


# Function-Based Views
@login_required(login_url='/login')
def welcome(request):
    try:
        bill_summary = TofaProductsOrder.objects.filter(
                user=request.user,
                status='Served'
            ).select_related('item_name').aggregate(
                total_bill=Sum(F('count') * F('item_name__price'))
            )
        total_bill_value = bill_summary['total_bill'] or 0
    except Exception as e:
        logger.error(f"We Couldnt get pending bills value for User:{request.username} so assuming it 0")
        total_bill_value=0
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
    items_in_cart = TofaProductsOrder.objects.filter(user=request.user, status='INCart_Pending').aggregate(total=Sum('count'))['total'] or 0
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
        item_name = request.POST.get('item_name')

        if not quantity or not quantity.isdigit():
            messages.error(request, 'Invalid quantity')
            return redirect(f'/home/menue/?submenue={selected_submenu}')

        quantity = int(quantity)
        item_obj = get_object_or_404(TofaProductsRepository, item_name=item_name)

        if action == 'add_to_cart':
            order_item = TofaProductsOrder.objects.filter(
                item_name=item_obj, user=request.user, status='INCart_Pending'
            ).first()

            if order_item:
                order_item.count += quantity
            else:
                order_item = TofaProductsOrder(
                    item_name=item_obj,
                    user=request.user,
                    status='INCart_Pending',
                    count=quantity
                )
            try:
                order_item.save()
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
        quantity = request.POST.get('quantity')
        table_number = request.POST.get('table_number')
        order_id = request.POST.get('order_id')

        if order_id:
            order_item = get_object_or_404(TofaProductsOrder, pk=order_id)

        if action == 'update' and quantity and quantity.isdigit():
            order_item.count = int(quantity)
            try:
                order_item.save()
                messages.info(request, "Item updated successfully")
            except Exception as e:
                messages.error(request, "Failed to update item")
                logger.error(f"Error updating item: {e}")
            return redirect('/home/cart/')

        elif action == 'remove':
            try:
                order_item.delete()
                messages.info(request, "Item removed successfully")
            except Exception as e:
                messages.error(request, "Failed to remove item")
                logger.error(f"Error removing item: {e}")
            return redirect('/home/cart/')

        elif action == 'execute' and table_number and table_number.isdigit():
            items = TofaProductsOrder.objects.filter(user=request.user, status='INCart_Pending')
            order_id_obj= TofaProductsOrderID.objects.create(user=request.user)
            if items.exists():
                for item in items:
                    item.status = 'INPreparation'
                    item.table_number = int(table_number)
                    item.order_number = order_id_obj
                    item.created_at = datetime.now()
                    try:
                        item.save()
                    except Exception as e:
                        messages.error(request, "Failed to process your order")
                        logger.error(f"Processing error for item {item.item_name}: {e}")
                        return redirect('/home/cart/')
                messages.info(request, "Your order is being prepared")
            else:
                messages.error(request, "No items in cart")
            return redirect('/home/cart/')

    items_in_cart = TofaProductsOrder.objects.filter(user=request.user, status='INCart_Pending')
    total_price = items_in_cart.aggregate(
        total=Sum(F('count') * F('item_name__price'))
    )['total'] or 0.0
    return render(request, 'cart.html', {
        'items_in_cart': items_in_cart,
        'total_price': total_price
    })


@login_required(login_url='/login')
def bill_view(request):
    items_to_be_charged=TofaProductsOrder.objects.select_related('item_name','order_number').filter(user=request.user,status='Served')
    total_bill_value=0
    for i in items_to_be_charged:
        total_bill_value+=i.count*i.item_name.price
    if request.method=='POST':
        pass
    return render(request, 'bill.html', {'items_to_be_charged':items_to_be_charged,'total_bill_value':total_bill_value})



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

class CartViewSubmitAPI(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        items=TofaProductsOrder.objects.filter(user=request.user, status='INCart_Pending')
        if not items:
            return Response({'error': 'No items in cart'}, status=status.HTTP_204_NO_CONTENT)
        tables_number=request.data.get('table_number',None)
        if not tables_number or not str(tables_number).isdigit():
            return Response({'error': 'missing field "tables_number" Valid table number required'}, status=status.HTTP_400_BAD_REQUEST)
        order_id_obj= TofaProductsOrderID.objects.create(user=request.user)
        try:
            Updated=items.update(
                status = 'INPreparation',
                table_number = int(tables_number),
                order_number = order_id_obj,
            )
        except Exception as e:
            logger.error(f"Error submit orders for {request.user.username} item {Updated}: {e}")
            return Response({'error': 'Failed to process your order'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.info(f"Cart submitted for preparation by {request.user.username} with {Updated} items.")
        return Response({'message': 'Cart submitted for preparation'}, status=status.HTTP_200_OK)


class CartViewAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            items = TofaProductsOrder.objects.filter(user=request.user, status='INCart_Pending')
            if not items.exists():
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
            item_name_exit=TofaProductsOrder.objects.get(user=request.user, item_name=serializer.validated_data['item_name'], status='INCart_Pending')
            if item_name_exit:
                item_name_exit.count = serializer.validated_data['count']
                try:
                    item_name_exit.save()
                except Exception as e:
                    logger.error(f"Update error for {request.user.username} item {item_name_exit.item_name}: {e}")
                    return Response({'error': 'Failed to update item in cart'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response({'message': 'Item updated in cart'}, status=status.HTTP_200_OK)
            else:
                try:
                    serializer.save(user=request.user, status='INCart_Pending')
                except Exception as e:
                    logger.error(f"Add error for {request.user.username} item {serializer.validated_data['item_name']}: {e}")
                    return Response({'error': 'failed to add Item'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response({'message': 'Item added to cart'}, status=status.HTTP_201_CREATED)
            

    def delete(self, request):
        item_name = request.data.get('item_name')
        if not item_name:
            return Response({'error': 'Item name required'}, status=status.HTTP_400_BAD_REQUEST)
        item = get_object_or_404(TofaProductsOrder, user=request.user, status='INCart_Pending', item_name__iexact=item_name)
        if not item:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
        try:
            item.delete()
            return Response({'message': 'Item deleted'}, status=status.HTTP_200_OK)
        except IntegrityError as e:
            logger.error(f"Delete error: {e}")
            return Response({'error': 'Failed to delete item'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetBill(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            items_to_be_charged=TofaProductsOrder.objects.select_related('item_name').filter(user=request.user,status='Served')
            serialize=TofaProductsOrderSerializer(items_to_be_charged,many=True)
        except Exception as e:
            logger.error(f'Failed to get pending bills for user {request.user.username}')
            return Response({'Error':'Failed to get user Bill'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'message':'Successfull bills returned','data':serialize.data},status=status.HTTP_200_OK)