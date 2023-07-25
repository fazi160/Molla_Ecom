
from django.shortcuts import render,redirect
from .models import Offer
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
# Create your views here.

def adminoffer(request):
    context = {
        'offer' : Offer.objects.all()
    }

    return render (request,'offer/offer.html',context)

def addoffer(request):
    if request.method == 'POST':
        offername = request.POST.get('offerrname')
        discount = request.POST.get('discount')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        if offername.strip() == '':
            messages.error(request, "Can't blank order name")
            return redirect('adminoffer')
        if discount.strip() == '':
            messages.error(request, "Can't blank Discount")
            return redirect('adminoffer')

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
            return redirect('adminoffer')

        if start_date >= end_date:
            messages.error(request, "Start date must be before end date.")
            return redirect('adminoffer')

        if start_date < timezone.now().date():
            messages.error(request, "Start date cannot be in the past.")
            return redirect('adminoffer')

        offer = Offer.objects.create(
            offer_name=offername,
            discount_amount=discount,
            start_date=start_date,
            end_date=end_date
        )
        offer.save()
        return redirect('adminoffer')
    
def editoffer(request, offer_id):
    if request.method == 'POST':
        offername = request.POST.get('offername')
        discount = request.POST.get('discount')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        if offername.strip() == '':
            messages.error(request, "Order name cannot be blank.")
            return redirect('adminoffer')
        if discount.strip() == '':
            messages.error(request, "Can't blank Offer field")
            return redirect('adminoffer')
        
        if Offer.objects.filter(offer_name=offername).exclude(id=offer_id).exists():
            messages.error(request, 'Offer name already exists')
            return redirect('adminoffer')

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
            return redirect('adminoffer')

        if start_date >= end_date:
            messages.error(request, "Start date must be before end date.")
            return redirect('adminoffer')

        if start_date < timezone.now().date():
            messages.error(request, "Start date cannot be in the past.")
            return redirect('adminoffer')

        off = Offer.objects.get(id=offer_id)
        off.offer_name = offername
        off.discount_amount = discount
        off.start_date = start_date
        off.end_date = end_date
        off.save()
        return redirect('adminoffer')

    offs = Offer.objects.filter(id=offer_id)
    return render(request, 'offer/offer.html', {'offer': offs})





def deleteoffer(request,delete_id):
    try:
        offer = Offer.objects.filter(id = delete_id)
        offer.delete()
        return redirect('adminoffer')
    except Offer.DoesNotExist:
        messages.error(request, "The specified offer does not exist.")
        return redirect('adminoffer')

def search_offer(request):
    if not request.user.is_superuser:
        return redirect('adminsignin')

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            offer = Offer.objects.filter(offer_name__icontains=keyword).order_by('id')
            if offer.exists():
                context = {
                    'offer': offer,
                }
                return render (request,'offer/offer.html',context)
            else:
                message = "offer not found."
                return render(request,'offer/offer.html', {'message': message})
        else:
            message = "Please enter a valid search keyword"
            return render(request, 'offer/offer.html', {'message': message})
    else:
        return render(request, 'error/index.html')
