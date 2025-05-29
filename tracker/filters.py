from django import forms
import django_filters
from tracker.models import Transaction, Category

class TransactionFilter(django_filters.FilterSet):
    transaction_type = django_filters.ChoiceFilter(
        choices = Transaction.TRANSACTION_TYPE_CHOICES,
        field_name = 'type',
        lookup_expr = 'iexact',
        empty_label = 'Any',
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
        fields = ('transaction_type','greater_than_amount','less_than_amount', 'start_date','end_date', 'category')