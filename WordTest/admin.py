from django.contrib import admin
from WordTest.models import *

# Register your models here.

admin.site.register(Languages)
admin.site.register(WordRepository)
admin.site.register(WordGroup)
admin.site.register(Word)
admin.site.register(WordTest)
admin.site.register(TestHistory)

