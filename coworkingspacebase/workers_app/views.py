from django.shortcuts import render,HttpResponse,redirect
from watchers_app.models import TofaProductsOrder
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