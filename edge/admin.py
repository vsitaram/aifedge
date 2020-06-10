from django.contrib import admin

from .models import Pitch, Member, Document, Tool#, DataFile

class DocumentInline(admin.TabularInline):
    model = Document

class PitchAdmin(admin.ModelAdmin):
	filter_horizontal = ('pitchers',)
	inlines = [DocumentInline]

class ToolAdmin(admin.ModelAdmin):
	filter_horizontal = ('creators',)
		

admin.site.register(Pitch, PitchAdmin)
admin.site.register(Member)
admin.site.register(Document)
# admin.site.register(DataFile)
admin.site.register(Tool, ToolAdmin)

