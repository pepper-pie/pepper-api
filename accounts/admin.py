from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import PersonalAccount

# Define a resource for import-export functionality
class PersonalAccountResource(resources.ModelResource):
    class Meta:
        model = PersonalAccount
        fields = ('id', 'name', 'account_type', 'description')
        export_order = ('id', 'name', 'account_type', 'description')

# Register the model with the ImportExportModelAdmin
@admin.register(PersonalAccount)
class PersonalAccountAdmin(ImportExportModelAdmin):
    resource_class = PersonalAccountResource

    list_display = ('name', 'account_type', 'description')  # Display in admin list view
    search_fields = ('name', 'account_type')  # Enable search by name and account type
    list_filter = ('account_type',)  # Add filtering by account type