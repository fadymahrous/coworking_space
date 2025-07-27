from watchers_app.models import TofaProductsRepository, Categorization, TofaProductsOrder,TofaProductsOrderID,bill_id
from accounts_app.models import User
from django.db.models import F, Sum
from user_home.constants import OrderStatus
from django.shortcuts import get_object_or_404
from logging import getLogger
from typing import Optional
from watchers_app.models import TofaProductsOrder
from django.db import IntegrityError

logger=getLogger('user_home')


class UserServices:

    @staticmethod
    def get_total_cart_price(user):
        total_orders_price=TofaProductsOrder.objects.filter(user=user,order_number__isnull=True).select_related('item_name').aggregate(
                total_bill=Sum(F('count') * F('item_name__price'))
            )
        clean_total_value=total_orders_price['total_bill']
        if clean_total_value:
            return clean_total_value
        return 0

    @staticmethod
    def get_items_in_cart(user):
        items_in_cart = TofaProductsOrder.objects.select_related('item_name').filter(
            user=user, 
            order_number__isnull=True
        ).order_by('placed_in_cart_at')
        if items_in_cart:
            return items_in_cart
        return None

    @staticmethod
    def get_items_count_in_cart(user):
        items_count_in_cart = TofaProductsOrder.objects.filter(user=user, order_number__isnull=True).aggregate(total=Sum('count'))['total']
        if items_count_in_cart:
            return items_count_in_cart
        return 0

    @staticmethod
    def _get_item_in_cart(user, item_name_obj) -> Optional[TofaProductsOrder]:
        try:
            return TofaProductsOrder.objects.get(
                user=user,
                item_name=item_name_obj,
                order_number__isnull=True
            )
        except TofaProductsOrder.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Unexpected error while checking cart item: {e}")
            return None

    @staticmethod
    def add_item_to_cart(user, item_name_obj, quantity: int,increment:bool=False):
        item = UserServices._get_item_in_cart(user, item_name_obj)
        if item:
            if increment:
                item.count += quantity
            else:
                item.count = quantity
        else:
            item = TofaProductsOrder(
                item_name=item_name_obj,
                user=user,
                count=quantity
            )

        try:
            item.save()
        except IntegrityError as e:
            logger.error(f"Integrity error while saving item to cart: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error while saving item to cart: {e}")
            raise e

    @staticmethod
    def remove_item_from_cart(user, item_name_obj):
        item = UserServices._get_item_in_cart(user, item_name_obj)
        if item:
            try:
                item.delete()
            except IntegrityError as e:
                logger.error(f"Faile to remove {item_name_obj} from cart for user {user.username} Details: {e}")
                raise e
        else:
            logger.error(f"Cant delete Because {item_name_obj} not exist in the cart for user {user.username} Details: {e}")
            raise ValueError(f"Cant find {item_name_obj} in cart")

    @staticmethod
    def send_cart_to_kitchen(user,table_number):
        items_in_cart=UserServices.get_items_in_cart(user=user)
        if items_in_cart:
            try:
                order_id=TofaProductsOrderID.objects.create(user=user,table_number=table_number)
            except Exception as e:
                logger.error(f"Failed to create Order, in items in the cart for user {user.username}")
                raise e
            try:
                items_in_cart.update(order_number=order_id)
            except Exception as e:
                logger.error(f"Failed to Assign Order, in items in the cart for user {user.username}")
                raise e

    @staticmethod
    def get_total_bill_price(user):
        total_orders_price=TofaProductsOrder.objects.select_related('order_number').filter(user=user,order_number__status='Served').aggregate(
                total_bill=Sum(F('count') * F('item_name__price'))
            )
        clean_total_value=total_orders_price['total_bill']
        if clean_total_value:
            return clean_total_value
        return 0
    
    @staticmethod
    def get_items_in_bill(user):
        items_in_cart=TofaProductsOrder.objects.select_related('order_number').filter(user=user,order_number__status='Served')
        if items_in_cart:
            return items_in_cart
        return None

    @staticmethod
    def request_bill_payment(user,total_bill_value):
        orders_not_charged=TofaProductsOrderID.objects.filter(user=user,status='Served')
        if orders_not_charged:
            try:
                pending_bill=bill_id.objects.get(bill_user=user,bill_status__in=['CUSTOMER_REQUEST_TO_CLOSE','RETURNED_TO_CUSTOMER'])
                pending_bill.bill_status='CUSTOMER_REQUEST_TO_CLOSE'
                pending_bill.save()
            except bill_id.DoesNotExist:
                pending_bill=bill_id.objects.create(bill_user=user,bill_value=total_bill_value)
            except Exception as e:
                logger.error(f'Failed to initiate bill for user: {user.username}, Details:{e}')
                raise e
            try:
                orders_not_charged.update(bill_number=pending_bill)
            except Exception as e:
                logger.error(f'Failed to update bill in Orders: {user.username}, Details:{e}')
                raise e
        else:
            return None

    @staticmethod
    def get_active_orders(user):
        try:
            active_orders=TofaProductsOrderID.objects.filter(user=user,status__ne='PAID_Closed')
        except Exception as e:
            logger.error(f'Detch to get Orders for user {user.username}, Details:{e}')
            raise e
        if active_orders:
            return active_orders
        return None

