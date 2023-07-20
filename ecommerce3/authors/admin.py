from django.contrib import admin
from .models import author
# Register your models here.

class authorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('author_name',)}


admin.site.register(author,authorAdmin)