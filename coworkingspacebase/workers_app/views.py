from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from watchers_app.models import TofaProductsOrder,bill_id
from django.contrib.auth.decorators import permission_required
from datetime import datetime
from django.contrib import messages
from helper.Logger_Setup import setup_logger
from django.db import transaction
from workers_app.services import WorkerServices

logger=setup_logger('workers_app', 'workers_app.log')

# Create your views here.
@permission_required('watchers_app.change_tofaproductsorderid',login_url='/worker/NotAutohrized/')
def worker_view(request):
    return render(request, 'home_worker.html')

@permission_required('watchers_app.change_tofaproductsorderid',login_url='/worker/NotAutohrized/')
def pick_shift(request):
    return render(request, 'pick_shift.html')

@permission_required('watchers_app.change_tofaproductsorderid',login_url='/worker/NotAutohrized/')
@transaction.atomic
def close_bill(request):
    ready_bills=WorkerServices.get_ready_bills()
    users_in_the_hall = WorkerServices.get_users_in_the_hall()
    items_linked_to_bills=None
    selected_bill=None
    if request.method=='POST':
        #Choose Bill to Focus on Or view its details
        selected_bill=request.POST.get('bill_id',None)
        if not (selected_bill and selected_bill.isdigit()):
            messages.error(request,'There is no Bill provided to fetch')
            return redirect('/worker/close_bill/')
        selected_bill=int(selected_bill)
        items_linked_to_bills=WorkerServices.get_items_in_the_bill(selected_bill)
        # Make specefic Action on this Bill Either Paied or returned to customer
        action=request.POST.get('action',None)
        if action=='approve':
            try:
                WorkerServices.approve_bill(selected_bill)
            except Exception as e:
                messages.error(request,'Failed to settele the Bill')
                logger.error(f"Failed to close orders in Orders table for user: {e} Details:{e}")
            return redirect('/worker/close_bill/')
        elif action=='reject':
            try:
                WorkerServices.reject_bill(selected_bill)
            except Exception as e:
                messages.error(request,'Failed to reject the bill')
                logger.error(f"Failed to close orders in Orders table for user: {e} Details:{e}")
            return redirect('/worker/close_bill/')
    return render(request,'close_bill.html',{'ready_bills':ready_bills,'users_in_the_hall':users_in_the_hall,'items_linked_to_bills':items_linked_to_bills,'selected_bill':selected_bill})

@permission_required('watchers_app.change_tofaproductsorderid',login_url='/worker/NotAutohrized/')
@transaction.atomic
def ongoing_orders(request):
    if request.method == 'POST':
        order_number = request.POST.get('order_number')
        if order_number and order_number.isdigit():
            order_number=int(order_number)
        if order_number:
            try:
                print(f"--/\/\/\->{order_number}")
                WorkerServices.server_order_to_customer(order_number)
            except Exception as e:
                messages.error(request,'Failed to send Order to Customer.')
                logger.error(f'Failed to Server Order to customer, Details:{e}')
    ongoing_orders=WorkerServices.get_orders_in_kitchen()
    
    return render(request, 'ongoing_orders.html', {'orders': ongoing_orders})

def not_authorized(request):
    return render(request,'not_authorized_worker.html')