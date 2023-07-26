from django.shortcuts import render, redirect
import logging
from .models import Blog
from django.contrib import messages 
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required

# Create your views here.

# Blog
@login_required(login_url='admin_login')
def blog(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    Blog_data = Blog.objects.all().order_by('id')
    return render(request, 'blog/blog.html',{'Blog' : Blog_data})

# Crete Blog
@login_required(login_url='admin_login')
def create_blog(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    if request.method == 'POST':
        image = request.FILES.get('image', None)
        name = request.POST['blog_name']
        description = request.POST['blog_discription']
    # validation
        if name.strip() =='':
            messages.error(request,'Image Not Fount')
            return redirect('blog')
        if not image:
            messages.error(request, "Image not uploaded")
            return redirect('blog')
        if Blog.objects.filter(blog_name=name).exists():
            messages.error(request, 'Blog name already exists')
            return redirect('blog')
    # Save
        categr = Blog(blog_name=name,blog_discription = description,blog_image=image)
        categr.save()
        return redirect('blog')
    

# Edit Blog
@login_required(login_url='admin_login')
def edit_blog(request, editBlog_id):
    if not request.user.is_superuser:
        return redirect('admin_login')
    if request.method == 'POST':
        name = request.POST['blog_name']
        description = request.POST['blog_discription']

    # validation
        try:
            caterg = Blog.objects.get(slug=editBlog_id)
            image = request.FILES.get('image')
            if image:
                caterg.blog_image = image
                caterg.save()
        except Blog.DoesNotExist:
            messages.error(request,'Image Not Fount')
            return redirect('blog')
        if name.strip() == '':
            messages.error(request,'Name field is empty')
            return redirect('blog')
        if Blog.objects.filter(blog_name=name).exists():
            check = Blog.objects.get(slug = editBlog_id)
            if name == check.blog_name:
                pass
            else:
                messages.error(request, 'Blog name already exists')
                return redirect('blog')
        
        categr = Blog.objects.get(slug=editBlog_id)
        categr.blog_name = name
        categr.blog_discription = description
        categr.save()
        return redirect ('blog')

# Delete Blog
@login_required(login_url='admin_login')
def delete_blog(request,deleteBlog_id):
    if not request.user.is_superuser:
        return redirect('admin_login')
    categre = Blog.objects.get(id=deleteBlog_id)
    categre.delete()
    return redirect('blog')

# Search Blog
@login_required(login_url='admin_login')
def search_Blog(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        if keyword:
            cate = Blog.objects.filter(blog_name__icontains=keyword).order_by('id')
            if cate.exists():
                context = {
                    'Blog': cate,
                }
                return render(request, 'blog/blog.html', context)
            else:
                message = "Blog not found"
                return render(request, 'blog/blog.html', {'message': message})
        else:
            message = "Please enter a valid search keyword"
            return render(request, 'blog/blog.html', {'message': message})
    else:
        return render(request, '404.html')

# user side
def blog_show(request):
    blog= Blog.objects.all()[:5]
    return render(request, 'blog/blog_view.html', {'blog':blog})