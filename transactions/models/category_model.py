from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Unique name for categories

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)  # SubCategory name
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")  # Link to Category

    class Meta:
        unique_together = ('name', 'category')  # Ensure unique SubCategory per Category

    def __str__(self):
        return f"{self.name} ({self.category.name})"