from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from categories.models import category
from .models import author
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# .......................author....................................


@login_required(login_url='admin_login')
def authors(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    author_data = author.objects.all().order_by('id')

    author_per_page = 10
    paginator = Paginator(author_data, author_per_page)

    page = request.GET.get('page')
    try:
        authors = paginator.page(page)
    except PageNotAnInteger:
        authors = paginator.page(1)
    except EmptyPage:
        authors = paginator.page(paginator.num_pages)

    return render(request, 'author/author.html', {'authors': authors})

# Create author
@login_required(login_url='admin_login')
def createauthors(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    if request.method == 'POST':
        cname = request.POST.get('author_name', '')
        eimage = request.FILES.get('author_image', None)
       
        cdescription = request.POST['author_discription']

        # Validation
        if cname.strip() == '':
            messages.error(request, "Name Field empty")
            return redirect('authors')

        if not eimage:
            messages.error(request, "Image not uploaded")
            return redirect('authors')
        
        if author.objects.filter(author_name=cname).exists():
            messages.error(request, 'author name already exists')
            return redirect('authors')

        bran = author(
            author_name=cname,
            author_image=eimage,
       
            author_discription=cdescription,
        )
        bran.save()
        return redirect('authors')

    return render(request, 'author/author.html')


# Edit author
@login_required(login_url='admin_login')
def editauthors(request, editauthors_id):
    if not request.user.is_superuser:
        return redirect('admin_login')
    if request.method == 'POST':
        cname = request.POST['author_name']
     
        cdescription = request.POST['author_discription']
    # validation
        if cname.strip() == '':
            messages.error(request, "Name Field empty")
            return redirect('authors')
        if author.objects.filter(author_name=cname).exists():
            check = author.objects.get(slug = editauthors_id)
            if cname == check.author_name:
                pass
            else:
                messages.error(request, 'author name already exists')
                return redirect('authors')

        try:
            cat = author.objects.get(slug=editauthors_id)
            eimage = request.FILES['author_image']
            cat.author_image = eimage
            cat.save()
        except:
            pass 

        cat = author.objects.get(slug=editauthors_id)
        cat.author_name = cname
      
        cat.author_discription = cdescription
        cat.save()
        return redirect('authors')
    cate = author.objects.filter(slug=editauthors_id)       
    return render(request, 'author/editauthors.html', {'catego': cate})

# Delete author
@login_required(login_url='admin_login')
def deleteauthors(request,deleteauthors_id):
    if not request.user.is_superuser:
        return redirect('admin_login')
    bran = author.objects.get(id=deleteauthors_id)
    bran.delete()
    return redirect('authors')

#search author
@login_required(login_url='admin_login')
def search_author(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            authors = author.objects.filter(author_name__icontains=keyword).order_by('id')
            if authors.exists():
                context = {
                    'author': authors,
                }
                return render(request, 'author/author.html', context)
            else:
                message = "author not found."
                return render(request, 'author/author.html', {'message': message})
        else:
            message = "Please enter a valid search keyword"
            return render(request, 'author/author.html', {'message': message})
    else:
        return render(request, '404.html')

