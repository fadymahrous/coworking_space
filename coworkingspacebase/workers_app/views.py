from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from watchers_app.models import TofaProductsOrder,bill_id
from django.contrib.auth.decorators import permission_required
from datetime import datetime
from django.contrib import messages
from helper.Logger_Setup import setup_logger

logger=setup_logger('workers_app', 'workers_app.log')

# Create your views here.
@permission_required('watchers_app.change_tofaproductsorderid',login_url='/worker/NotAutohrized/')
def worker_view(request):
    return render(request, 'home_worker.html')

@permission_required('watchers_app.change_tofaproductsorderid',login_url='/worker/NotAutohrized/')
def pick_shift(request):
    return render(request, 'pick_shift.html')

def close_bill(request):
    ready_bills=bill_id.objects.filter(bill_status='CUSTOMER_REQUEST_TO_CLOSE')
    users_in_the_hall = TofaProductsOrder.objects.exclude(status='PAID_Closed').values('user__id','user__username').distinct()
    items_linked_to_bills=None
    selected_bill=None
    if request.method=='POST':
        selected_bill=request.POST.get('bill_id',None)
        if not (selected_bill or selected_bill.isdigit()):
            messages.error(request,'There is no Bill provided to fetch')
            return redirect('/worker/close_bill/')
        selected_bill=int(selected_bill)
        action=request.POST.get('action',None)
        if action=='approve':
            try:
                items_linked_to_bills=TofaProductsOrder.objects.filter(bill_number=selected_bill)
                items_linked_to_bills.update(status='PAID_Closed')
            except Exception as e:
                messages.error(request,'Failed to settele the Order')
                logger.error(f"Failed to close orders in Orders table for user: {bill_object.bill_user}")
            bill_object=get_object_or_404(bill_id,pk=selected_bill)
            try:
                bill_object.bill_status='SETTELLED'
                bill_object.save()
            except Exception as e:
                messages.error(request,'Failed to Close the Bill.')
                logger.error(f"Failed to close Bill id {bill_object.id} for user: {bill_object.bill_user}")
            return redirect('/worker/close_bill/')
        elif action=='reject':
            bill_object=get_object_or_404(bill_id,pk=selected_bill)
            try:
                bill_object.bill_status='RETURNED_TO_CUSTOMER'
                bill_object.save()
            except Exception as e:
                messages.error(request,'Failed to Return Bill to the Customer.')
                logger.error(f"Failed to return Bill id {bill_object.id} to user: {bill_object.bill_user}")
            return redirect('/worker/close_bill/')
        items_linked_to_bills=TofaProductsOrder.objects.filter(bill_number=selected_bill)
    return render(request,'close_bill.html',{'ready_bills':ready_bills,'users_in_the_hall':users_in_the_hall,'items_linked_to_bills':items_linked_to_bills,'selected_bill':selected_bill})


@permission_required('watchers_app.change_tofaproductsorderid',login_url='/worker/NotAutohrized/')
def ongoing_orders(request):
    if request.method == 'POST':
        order_number = request.POST.get('order_number')
        if order_number and order_number.isdigit():
            try:
                orders = TofaProductsOrder.objects.select_related('order_number').filter(order_number__pk=int(order_number), status='INPreparation')
                try:
                    updates=orders.update(status='Served', fullfilled_at=datetime.now())
                except Exception as e:
                    messages.error(request, f"Error updating order: {e}")
                    logger.error(f"Error updating order {order_number} for item: {updates}: {e}")
                messages.info(request,"Order marked as finished.")
                return redirect('/worker/ongoing_orders/')
            except TofaProductsOrder.DoesNotExist:
                return HttpResponse("Order not found.", status=404)
        else:
            messages.error(request, "Invalid order number.")
    ongoing_orders=TofaProductsOrder.objects.select_related('order_number').filter(status='INPreparation').order_by('order_number__order_creation_time')
    print(ongoing_orders)
    
    return render(request, 'ongoing_orders.html', {'orders': ongoing_orders})

def not_authorized(request):
    return render(request,'not_authorized_worker.html')