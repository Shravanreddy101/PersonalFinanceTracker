import plotly.express as px
from django.db.models import Sum
from tracker.models import Category
import plotly.io as pio
from io import BytesIO


def plot_income_expenses_bar_chart(qs, as_image=False):
    x_vals = ['Income', 'Expenditure']

    total_income = qs.filter(type = 'income').aggregate(
        total = Sum('amount')
    )['total'] or 0
    total_expenses = qs.filter(type = 'expense').aggregate(
        total = Sum('amount')
    )['total'] or 0

    data = {
        'Type': ['Income', 'Expenses'],
        'Amount': [total_income, total_expenses]
    }
    fig = px.bar(
        data,
        x='Type',
        y='Amount',
        color='Type',
        color_discrete_map={'Income': 'green', 'Expenses': 'red'},
        text='Amount',
        labels={'Amount': 'Total Amount ($)', 'Type': 'Transaction Type'}
    )

    fig.update_layout(
        title= {
            'text': 'Income vs. Expenses',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size':20}
        },
        yaxis_title='Amount ($)',
        xaxis_title='',
        title_font_size=20,
        plot_bgcolor='rgba(0,0,0,0)',  
        paper_bgcolor='white',
        font=dict(color='black'),
        margin=dict(t=60, b=30, l=20, r=20),
    )

    fig.update_traces(
        texttemplate='$%{text:.2f}',
        textposition='outside'
    )

    if as_image:
        return pio.to_image(fig, format="png")
    return fig

    



def plot_category_pie_chart(qs,chart_title, as_image=False):
    count_per_category = qs.order_by('category').values('category').annotate(total=Sum('amount'))
    print(count_per_category)

    category_pks = count_per_category.values_list('category', flat=True).order_by('category')
    categories = Category.objects.filter(pk__in=category_pks).order_by('pk').values_list('name', flat=True)
    total_amount = count_per_category.order_by('category').values_list('total', flat=True)

    fig = px.pie(values=total_amount, names=categories)
    fig.update_layout(
    title={
        'text': chart_title,     
        'y':0.95,               
        'x':0.5,                 
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 20}
    },
    showlegend=True,
    margin=dict(t=60, b=30, l=0, r=0),  
    paper_bgcolor='white'  
    ) 
    if as_image:
        return pio.to_image(fig, format="png")
    return fig