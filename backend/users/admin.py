from django.contrib import admin

from .models import MyUser
from recipes.models import Ingredients, Tag

admin.site.register(MyUser)
admin.site.register(Ingredients)
admin.site.register(Tag)
