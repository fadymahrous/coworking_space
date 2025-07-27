from watchers_app.models import bill_id,TofaProductsOrder,TofaProductsOrderID
from accounts_app.models import User
from workers_app.constants import BillStatus,ItemsInCartsStatus
from logging import getLogger
from datetime import datetime,timezone


logger=getLogger('workers_app')

class WorkerServices:

    @staticmethod
    def get_bills_to_be_charged():
        ready_bills=bill_id.objects.filter(bill_status=BillStatus.CUSTOMER_REQUEST_TO_CLOSE)
        if ready_bills:
            return ready_bills
        return None
    
    @staticmethod
    def get_users_in_the_hall():
        users_in_hall=User.objects.filter(TofaProductsOrderID__status__ne=ItemsInCartsStatus.PAID_Closed).values('user__id','user__username').distinct()
        if users_in_hall:
            return users_in_hall
        return None
    
    @staticmethod
    def get_items_in_bill(bill_id):
        items_in_bill=TofaProductsOrder.objects.filter(bill_number=bill_id)
        if items_in_bill:
            return items_in_bill
        return None

    @staticmethod
    def get_orders_in_kitchen():
        orders_in_kitchen=TofaProductsOrder.objects.select_related('order_number').filter(order_number__status='INPreparation').order_by('order_number__order_creation_time')
        if orders_in_kitchen:
            return orders_in_kitchen
        else:
            return None

    @staticmethod
    def server_order_to_customer(order_number):
        try:
            order_to_customer=TofaProductsOrderID.objects.get(pk=order_number)
            print(f'===>{order_to_customer}')
        except TofaProductsOrderID.DoesNotExist as e:
            logger.error(f'This Order not exist, Details:{e}')
            raise e
        except Exception as e:
            logger.error(f'Failed to Server Order to customer, Details:{e}')
            raise e
        if order_to_customer:
            order_to_customer.status='Served'
            order_to_customer.fullfilled_at=datetime.now(timezone.utc)
            try:
                order_to_customer.save()
                print(order_to_customer,order_to_customer.status)
            except Exception as e:
                logger.error(f'Failed to Server Order to customer, Details:{e}')
                raise e

    @staticmethod
    def get_ready_bills():
        return bill_id.objects.filter(bill_status='CUSTOMER_REQUEST_TO_CLOSE')
 
    @staticmethod
    def get_users_in_the_hall():
        return User.objects.filter(tofaproductsorderid__status='Served').distinct()

    @staticmethod
    def get_items_in_the_bill(bill_id_value):
        items_in_the_bill = TofaProductsOrder.objects.select_related(
            'order_number',
            'order_number__bill_number'
        ).filter(order_number__bill_number__id=bill_id_value)

        if not items_in_the_bill.exists():
            print(f"No items found for bill ID {bill_id_value}")
        else:
            print(f"{items_in_the_bill.count()} item(s) found for bill ID {bill_id_value}")
        return items_in_the_bill

    @staticmethod
    def approve_bill(bill_id_value):
        try:
            selected_bill = bill_id.objects.get(pk=bill_id_value)
        except bill_id.DoesNotExist as e:
            logger.error(f"Bill with ID {bill_id_value} does not exist. Details: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching bill with ID {bill_id_value}. Details: {e}")
            return None

        try:
            selected_bill.bill_status = 'SETTELLED'
            selected_bill.bill_closure_time=datetime.now(timezone.utc)
            selected_bill.save()
            logger.info(f"Bill with ID {bill_id_value} approved and status set to SETTELLED.")
        except Exception as e:
            logger.error(f"Failed to update status for bill ID {bill_id_value}. Details: {e}")
            return None

        try:
            related_orders = TofaProductsOrderID.objects.filter(bill_number=selected_bill)
            updated_count = related_orders.update(status='PAID_Closed')
            logger.info(f"Updated {updated_count} related orders to PAID_Closed for bill ID {bill_id_value}.")
        except Exception as e:
            logger.error(f"Failed to update related orders for bill ID {bill_id_value}. Details: {e}")
            return None

        return selected_bill

    @staticmethod
    def reject_bill(bill_id_value):
        try:
            selected_bill = bill_id.objects.get(pk=bill_id_value)
        except bill_id.DoesNotExist as e:
            logger.error(f"Bill with ID {bill_id_value} does not exist. Details: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching bill with ID {bill_id_value}. Details: {e}")
            return None

        try:
            selected_bill.bill_status = 'RETURNED_TO_CUSTOMER'
            selected_bill.save()
            logger.info(f"Bill with ID {bill_id_value} returned to customer.")
        except Exception as e:
            logger.error(f"Failed to update bill status to RETURNED_TO_CUSTOMER for bill ID {bill_id_value}. Details: {e}")
            return None

        return selected_bill
