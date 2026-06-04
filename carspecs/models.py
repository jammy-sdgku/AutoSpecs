from django.db import models

class SearchHistory(models.Model):
    SEARCH_TYPE_CHOICES = [
        ('ymm', 'Year/Make/Model'),
        ('vin', 'VIN'),
    ]
    search_type = models.CharField(max_length=10, choices=SEARCH_TYPE_CHOICES)
    vin = models.CharField(max_length=17, blank=True, null=True)
    year = models.CharField(max_length=4, blank=True, null=True)
    make = models.CharField(max_length=50, blank=True, null=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    trim = models.CharField(max_length=50, blank=True, null=True)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.search_type == 'vin':
            return f"VIN: {self.vin}"
        return f"{self.year} {self.make} {self.model} {self.trim or ''}".strip()

    class Meta:
        ordering = ['-searched_at']
        verbose_name_plural = "Search Histories"
