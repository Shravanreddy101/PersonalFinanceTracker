from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import TransactionQuerySet

class User(AbstractUser):
    pass



class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name



class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('income','Income'),
        ('expense', 'Expense'),
    )
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    objects = TransactionQuerySet.as_manager()

    def __str__(self):
        return f"{self.type} of {self.amount} on {self.date} by {self.user}"
    
    class Meta:
        ordering = ['-date']


class CategoryBudget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    month = models.DateField(help_text="First day of the month")
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('user','category', 'month')
    
    def __str__(self):
        return f"{self.user} - {self.month.strftime('%B %Y')} - ${self.amount}"
    
    def get_total_spent(self):
        return(
            Transaction.objects.filter(
                user=self.user,
                category = self.category,
                type='expense',
                date__year = self.month.year,
                date__month = self.month.month
            ).aggregate(total=models.Sum('amount'))['total'] or 0 
        )
    
    def get_progress_bar(self):
        spent = self.get_total_spent()
        if self.amount > 0:
            return min((spent / self.amount) * 100, 100)
        return 0
