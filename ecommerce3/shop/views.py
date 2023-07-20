# from django.shortcuts import render,redirect
# from products.models import product

# from wishlist.models import Wishlist
# from django.views.decorators.cache import cache_control
# from django.http.response import JsonResponse
# # Create your views here.



# def product_detail(request,product_id):

#     try:
#         prod=product.objects.get(slug=product_id)
#     except product.DoesNotExist:
#         return render(request,'error/index.html')


#     if request.method == 'POST':

#         prod_id=request.POST.get('prod_id')
#         product=product.objects.get(product=prod_id)
#         product_quantity=prod.quantity
#         return JsonResponse({'product_id':product.id, 'product_quantity':product_quantity})

#     related=product.objects.all()

#     context={
#         'allpro':related,
#         'pro_detail':prod

#     }

#     return render(request,'product-detail.html',context)




