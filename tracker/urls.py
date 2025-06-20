from django.urls import path
from tracker import views


urlpatterns = [
    path("", views.index, name='index'),
    path("transactions/", views.transactions_list, name='transactions-list'),
    path("transactions/create/", views.create_transaction, name='create-transaction'),
    path("transactions/<int:pk>/update/", views.update_transaction, name='update-transaction'),
    path("transactions/<int:pk>/delete/", views.delete_transaction, name='delete-transaction'),
    path("transactions/<int:pk>/delete-category/", views.delete_category, name='delete-category'),
    path("get-transactions/", views.get_transactions, name='get-transactions'),
    path("transactions/charts", views.transactions_charts, name='transactions-charts'),
    path("transactions/export", views.export, name='export'),
    path("transactions/charts/exportChart", views.export_charts, name='exportCharts'),
    path('top-expenses/', views.get_top_expenses, name='get-top-expenses'),
    path('transactions/setbudget/', views.set_category_budget, name='set-budget'),
    path('transactions/category-budgets/', views.category_budget_progress, name='category-budgets'),
    
]
