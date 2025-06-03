from django import forms
import django_filters
from tracker.models import Transaction, Category

class TransactionFilter(django_filters.FilterSet):
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

    transaction_type = django_filters.ChoiceFilter(
        choices = Transaction.TRANSACTION_TYPE_CHOICES,
        field_name = 'type',
        lookup_expr = 'iexact',
        empty_label = 'Any',
    )

    date_month = django_filters.ChoiceFilter(
        choices = MONTH_CHOICES,
        field_name = 'date',
        lookup_expr = 'month',
        empty_label = 'Select Month'
    )

    greater_than_amount = django_filters.NumberFilter(
        field_name = 'amount',
        lookup_expr="gte",
        label = "Amount greater than"
    )

    less_than_amount = django_filters.NumberFilter(
        field_name = 'amount',
        lookup_expr="lte",
        label = "Amount less than"
    )

    start_date = django_filters.DateFilter(
        field_name = 'date',
        lookup_expr = "gte",
        label = "Date From",
        widget = forms.DateInput(attrs={'type' : 'date'})
    )

    end_date = django_filters.DateFilter(
        field_name = 'date',
        lookup_expr = "lte",
        label = "Date To",
        widget = forms.DateInput(attrs={'type' : 'date'})
    )

    category = django_filters.ModelMultipleChoiceFilter(
        queryset = Category.objects.all(),
        widget = forms.CheckboxSelectMultiple,
    )


    


    class Meta:
        model = Transaction
        fields = ('transaction_type','date_month','greater_than_amount','less_than_amount', 'start_date','end_date', 'category')