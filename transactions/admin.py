from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Transaction, Category, SubCategory


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'narration', 'category', 'subcategory', 'debit_amount', 'credit_amount', 'nominal_account', 'personal_account')
    search_fields = ('narration', 'category__name', 'subcategory__name', 'nominal_account')
    list_filter = ('category', 'subcategory', 'nominal_account', 'personal_account')


# Resource for Category import/export
class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ('id', 'name')  # Define fields to import/export
        export_order = ('id', 'name')


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ('id', 'name')
    search_fields = ('name',)


# Resource for SubCategory import/export
class SubCategoryResource(resources.ModelResource):
    def before_import_row(self, row, **kwargs):
        """
        Validate that the category referenced in the subcategory exists.
        """
        category_name = row['category']
        if not Category.objects.filter(name=category_name).exists():
            raise ValueError(f"Category '{category_name}' does not exist. Please import categories first.")

    class Meta:
        model = SubCategory
        fields = ('id', 'name', 'category')  # Define fields to import/export
        export_order = ('id', 'name', 'category')


@admin.register(SubCategory)
class SubCategoryAdmin(ImportExportModelAdmin):
    resource_class = SubCategoryResource
    list_display = ('id', 'name', 'category')
    search_fields = ('name', 'category__name')
    list_filter = ('category',)