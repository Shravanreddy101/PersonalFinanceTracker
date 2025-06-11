from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.conf import settings
from tracker.models import CategoryBudget, Transaction
from tracker.filters import TransactionFilter
from tracker.forms import CategoryBudgetForm, TransactionForm
from django_htmx.http import retarget
from tracker.charting import plot_income_expenses_bar_chart, plot_category_pie_chart
from tracker.resources import TransactionResource
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import FileResponse
from io import BytesIO
from tracker.models import Transaction
import io
import base64
from reportlab.lib.utils import ImageReader
from django.utils import timezone
import datetime
from django.db import models
from django.utils.timezone import now



@login_required
def index(request):
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )

    total_income = transaction_filter.qs.get_total_income()
    total_expenses = transaction_filter.qs.get_total_expenses()

    selected_month = request.GET.get('date_month')
    today = now()
    if selected_month and selected_month.isdigit():
        month_name = datetime.date(1900, int(selected_month), 1).strftime('%B')
        current_month_year = f"{month_name} {today.year}"
    else:
        current_month_year = today.strftime('%B %Y')
    
    
    context = {
        'filter': transaction_filter,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': total_income - total_expenses,
        'current_date' : current_month_year
    }
    if request.htmx:
        return render(request, 'tracker/partials/totals.html', context)
    
    return render(request, 'tracker/index.html', context)




@login_required
def transactions_list(request):
    transaction_filter = TransactionFilter(
        request.GET,
        queryset = Transaction.objects.filter(user=request.user).select_related('category')
    )
    paginator = Paginator(transaction_filter.qs, settings.PAGE_SIZE)
    transaction_page = paginator.page(1)

    total_income = transaction_filter.qs.get_total_income()
    total_expenses = transaction_filter.qs.get_total_expenses()
    context = {
        'transactions' : transaction_page,
        'filter' : transaction_filter,
        'total_income' : total_income,
        'total_expenses' : total_expenses,
        'net_income' : total_income - total_expenses
        }
    if request.htmx:
        return render(request, 'tracker/partials/transactions-container.html', context)
    return render(request, 'tracker/transactions-list.html', context)





@login_required
def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            context = {'message' : 'Transaction added successfully!'}
            if request.htmx:
                return render(request, 'tracker/partials/transaction-success.html', context)
        else:
            context = {'form' : form}
            response = render(request, 'tracker/partials/create-transaction.html', context)
            return retarget(response, '#transaction-block')

    context = {'form' : TransactionForm()}
    if request.htmx:
        return render(request, 'tracker/partials/create-transaction.html', context)
    else:
        return render(request, 'tracker/create-base-transaction.html', context)

    



@login_required
def update_transaction(request,pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save()
            context = {'message' : 'Transaction updated successfully!'}
            if request.htmx:
                return render(request, 'tracker/partials/transaction-success.html', context)
        else:
            context = {'form' : form, 'transaction' : transaction}
            response = render(request, 'tracker/partials/update-transaction.html', context)
            return retarget(response, '#transaction-block')
        
    context = {'form' : TransactionForm(instance=transaction), 'transaction' : transaction}
    if request.htmx:
        return render(request,'tracker/partials/update-transaction.html', context)
    else:
        return render(request,'tracker/update-base-transaction.html', context)





@login_required
@require_http_methods(["DELETE"])
def delete_transaction(request,pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.delete()
    context = {
        'message' : f"Transaction amount of {transaction.amount} on {transaction.date} was deleted successfully!"
    }
    return render(request, 'tracker/partials/transaction-success.html', context)





@login_required
def get_transactions(request):
    page = request.GET.get('page', 1)
    transaction_filter = TransactionFilter(
        request.GET,
        queryset = Transaction.objects.filter(user=request.user).select_related('category')
    )
    paginator = Paginator(transaction_filter.qs, settings.PAGE_SIZE)
    total_income = transaction_filter.qs.get_total_income()
    total_expenses = transaction_filter.qs.get_total_expenses()
    context = {
        'transactions': paginator.page(page),
        'filter': transaction_filter,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': total_income - total_expenses
    }
    return render(request, 'tracker/partials/transactions-container.html', context )




@login_required
def transactions_charts(request):
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )
    income_expense_bar = plot_income_expenses_bar_chart(transaction_filter.qs)
    category_income_pie = plot_category_pie_chart(transaction_filter.qs.filter(type='income'), 'Income')
    category_expense_pie = plot_category_pie_chart(transaction_filter.qs.filter(type='expense'), 'Expenses')
    total_income = transaction_filter.qs.get_total_income()
    total_expenses = transaction_filter.qs.get_total_expenses()
    net_income = total_income - total_expenses

    context = {'filter' : transaction_filter, 'income_expense_bar_chart' : income_expense_bar.to_html(),'income_pie' : category_income_pie.to_html(),'expense_pie' : category_expense_pie.to_html(),'total_income' : total_income, 'total_expenses' : total_expenses, 'net_income' : net_income}
    if request.htmx:
        return render(request, 'tracker/partials/charts-container.html', context)
    return render(request, 'tracker/charts.html', context)




@login_required
def export(request):
    if request.htmx:
        return HttpResponse(headers={'HX-Redirect' : request.get_full_path()})
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )
    data = TransactionResource().export(transaction_filter.qs)
    response = HttpResponse(data.csv)
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    return response



@login_required
def export_charts(request):
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )

    income_expense_bar = plot_income_expenses_bar_chart(transaction_filter.qs, as_image=True)
    category_income_pie = plot_category_pie_chart(transaction_filter.qs.filter(type='income'), 'Income', as_image=True)
    category_expense_pie = plot_category_pie_chart(transaction_filter.qs.filter(type='expense'), 'Expenses', as_image=True)
    total_income = transaction_filter.qs.get_total_income()
    total_expenses = transaction_filter.qs.get_total_expenses()
    net_income = total_income - total_expenses

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 100

    for img_bytes in [income_expense_bar, category_income_pie, category_expense_pie]:
        img_stream = BytesIO(img_bytes)
        img = ImageReader(img_stream)
        p.drawImage(img, 100, y - 250, width=400, height=250)
        y -= 270
        if y < 300:
            p.showPage()
            y = height - 100
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='charts.pdf')


@login_required
def get_top_expenses(request):
    transaction_filter = TransactionFilter(
        request.GET,
        queryset= Transaction.objects.filter(user=request.user).select_related('category')
    )
    top_10 = transaction_filter.qs.get_top_10_expenses()
    total_expenses = transaction_filter.qs.get_total_top_10_expenses()
    context = {'filter' : transaction_filter,'transactions' : top_10, 'total_expenses' : total_expenses, }
    return render(request, 'tracker/partials/transactions-container.html', context)



@login_required
def set_category_budget(request):
    if request.method == 'POST':
        form = CategoryBudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()

            budgets = CategoryBudget.objects.filter(user=request.user).select_related('category')
            context = {"budgets" : budgets}
            return render(request, 'tracker/partials/budget_progress.html', context)
        else:
            context = {'form' : form}
            response = render(request, 'tracker/partials/set-budget.html', context)
            return retarget(response, '#transaction-block')
    context = {'form' : CategoryBudgetForm()}
    if request.htmx:
        return render(request, 'tracker/partials/set-budget.html', context)
    else:
        return render(request, 'tracker/set-base-budget.html', context)
    


@login_required
def category_budget_progress(request):
    budgets = CategoryBudget.objects.filter(user=request.user).select_related('category')
    return render(request, 'tracker/view-budgets.html', {'budgets': budgets})