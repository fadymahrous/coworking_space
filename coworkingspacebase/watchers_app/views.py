from django.shortcuts import render,HttpResponse,redirect
from helper.Logger_Setup import setup_logger
from .forms import Categorization_Form,TofaProductsRepository_form
from .models import Categorization,TofaProductsRepository
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.shortcuts import get_object_or_404

##initiate logger
logger=setup_logger('watchers_app','watchers_app.log')

# Create your views here.
@permission_required('watchers_app.change_categorization',login_url='NotAutohrized/')
def watcher_view(request):
    if request.method=='GET' and 'GoTo' in request.GET:
        which_page=request.GET['GoTo']
        if which_page=="AddCategory":
            return add_category(request)
        elif which_page=="AddGoods":
            return add_goods(request)
        elif which_page=="Reports":
            return reports(request)
    return render(request,'home_watcher.html')

@permission_required('watchers_app.change_categorization',login_url='NotAutohrized/')
def add_category(request):
    if request.method=="POST" and 'action' in request.POST:
        action=request.POST.get("action","").lower()
        if action=='save':
            form=Categorization_Form(request.POST)
            if form.is_valid():
                try:
                    form.save()
                    logger.info(f"User {request.user.username} saved a {request.POST}.")
                    messages.info(request,'Object saved Successfully.')
                    return redirect('/watcher/addcategory/')
                except Exception as e:
                    logger.error(f"Cant Save the form in the database due to this Exception: {e}")
            else:
                messages.error(request, f"form is not valid for details:{form.errors}")
        elif action=='delete':
            element=request.POST.get('element_id',None)
            if element and element.isdigit():
                row=get_object_or_404(Categorization,pk=int(element))
                try:
                    row.delete()
                    logger.info(f"User {request.user.username} deleted item {str(row)}.")
                    messages.info(request,'Object deleted Successfully.')
                    return redirect('/watcher/addcategory/')
                except Exception as e:
                    messages.error(request,'Object deletion failed.')
                    logger.error(f"Cant Delete Object from database due to this Exception: {e}")
            else:
                messages.info(request,'Object deletion failed.')
                logger.error(f"The passed element is Invalid we were expecting integer while got :{element}")

    all_categories=Categorization.objects.all()
    form=Categorization_Form()
    return render(request,'add_category.html',{'form':form,'all_categories':all_categories})

@permission_required('watchers_app.change_categorization', login_url='NotAutohrized/')
def add_goods(request):
    update_row = None
    form = TofaProductsRepository_form()
    if request.method == "POST":
        print(f"---->{request.POST}")
        action = request.POST.get("action", "").lower()
        element_id = request.POST.get("element_id", None)
        quantity = request.POST.get("quantity", None)

        if quantity and quantity.isdigit():
            quantity = int(quantity)
        else:
            quantity = None

        if action == "edit" and element_id:
            print(f"---->{request.POST}")
            update_row = get_object_or_404(TofaProductsRepository, pk=element_id)
            form = TofaProductsRepository_form(instance=update_row)
        elif action == "update" and element_id:
            update_row = get_object_or_404(TofaProductsRepository, pk=element_id)
            form=TofaProductsRepository_form(request.POST,instance=update_row)
            if form.is_valid():
                try:
                    form.save()
                    messages.info(request,f"Object updated successfully")
                    logger.info(f"User: {request.user.username} updated {request.POST.get('item_name')}")
                    return redirect('/watcher/addgoods/')
                except Exception as e:
                    messages.error(request,f"Failed to Update Object")
                    logger.error(f"Failed to update the element {update_row} , for more details:{e}")
            else:
                messages.error(request,'Your imput is invalid')
                logger.error(f"Failed to update the element {update_row} , for more details:{form.errors}")
        elif action == "delete" and element_id:
            delete_row = get_object_or_404(TofaProductsRepository, pk=element_id)
            try:
                delete_row.delete()
                messages.success(request, "Object deleted successfully.")
                logger.info(f"User: {request.user.username} deleted {delete_row.item_name}")
                return redirect('/watcher/addgoods/')
            except Exception as e:
                messages.error(request, "Failed to delete object.")
                logger.error(f"Failed to delete object: {e}")

        elif action == "save":
            if isinstance(element_id, int):
                update_row = get_object_or_404(TofaProductsRepository, pk=element_id)
                form = TofaProductsRepository_form(request.POST, instance=update_row)
            else:
                form = TofaProductsRepository_form(request.POST)

            if form.is_valid():
                try:
                    form.save()
                    logger.info(f"User: {request.user.username} created or updated {request.POST.get('item_name')}")
                    return redirect('/watcher/addgoods/')
                except Exception as e:
                    messages.error(request, "Failed to save object.")
                    logger.error(f"Failed to save object: {e}")
            else:
                messages.error(request, "Please correct the errors below.")

        elif quantity is not None and element_id:
            update_row = get_object_or_404(TofaProductsRepository, pk=element_id)
            update_row.item_quantity = update_row.item_quantity + quantity
            try:
                update_row.save()
                logger.info(f"User: {request.user.username} topped up {update_row.item_name} by {quantity}")
                return redirect('/watcher/addgoods/')
            except Exception as e:
                messages.error(request, "Failed to top up the object.")
                logger.error(f"Failed to top up the object: {e}")

    all_categories = TofaProductsRepository.objects.all().order_by("item_name", "category", "brand")
    return render(request, "add_goods.html", {
        "form": form,
        "all_categories": all_categories,
        "update_row": update_row
    })

@permission_required('watchers_app.change_categorization',login_url='NotAutohrized/')
def reports(request):
    return HttpResponse("We are in the reports page")

def not_authorized(request):
    return render(request,'not_authorized_Watcher.html')