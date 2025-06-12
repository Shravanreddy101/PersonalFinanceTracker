from datetime import date
from django import forms
from tracker.models import Category, Transaction, CategoryBudget


class TransactionForm(forms.ModelForm):


    custom_category = forms.CharField(
        required = False,
        label = "Custom Category",
        widget = forms.TextInput(attrs={'Placeholder': 'Enter new category name'})
    )


    category = forms.ModelChoiceField(
        queryset = Category.objects.all(),
        widget = forms.RadioSelect()
    )

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be a positive number")
        return amount

    class Meta:
        model = Transaction
        fields = (
            'type',
            'amount',
            'date',
            'category',
            'custom_category'
        )
        widgets = {
            'date' : forms.DateInput(attrs={'type' : 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False




class CategoryBudgetForm(forms.ModelForm):
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget = forms.Select,
        
    )

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be a positive number")
        return amount
    
    def clean_month(self):
        month_num = int(self.cleaned_data['month'])
        current_year = date.today().year
        return date(current_year, month_num,1)
    
    MONTH_CHOICES = [
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ]
    month = forms.ChoiceField(choices=MONTH_CHOICES)

    class Meta:
        model = CategoryBudget
        fields = (
            'category',
            'month',
            'amount'
        )

    
