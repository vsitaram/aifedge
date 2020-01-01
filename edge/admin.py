from django.contrib import admin

from .models import Pitch, Member, Document

class DocumentInline(admin.TabularInline):
    model = Document

class PitchAdmin(admin.ModelAdmin):
	filter_horizontal = ('pitchers',)
	inlines = [DocumentInline]
		

admin.site.register(Pitch, PitchAdmin)
admin.site.register(Member)
admin.site.register(Document)
