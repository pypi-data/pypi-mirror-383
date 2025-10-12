

import datetime
import json
from pathlib import Path

from django.db import models
import pandas as pd

from buzzerboy_saas_tenants.core.models import AuditableBaseModel
from buzzerboy_saas_tenants.saas_tenants.models.tenant import Tenant
from buzzerboy_saas_tenants.core import shortcuts as CORE_SHORTCUTS
from buzzerboy_saas_tenants.core.utils import load_csv_file

def current_year():
    return datetime.datetime.now().year

def current_month():
    return datetime.datetime.now().month


MONTH_CHOICES = [
    { "value": "1", "label": "January"},
    { "value": "2", "label": "February"},
    { "value": "3", "label": "March"},
    { "value": "4", "label": "April"},
    { "value": "5", "label": "May"},
    { "value": "6", "label": "June"},
    { "value": "7", "label": "July"},
    { "value": "8", "label": "August"},
    { "value": "9", "label": "September"},
    { "value": "10", "label": "October"},
    { "value": "11", "label": "November"},
    { "value": "12", "label": "December"}
]



class MonthlyAnalytics(AuditableBaseModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='analytics')
    
    created = models.DateTimeField(auto_now_add=True)

    month = models.IntegerField(default=current_month)
    year = models.IntegerField(default=current_year)



    @staticmethod
    def get_or_create_analytics(tenant, month, year):
        analytics = None
        analytics = MonthlyAnalytics.objects.filter(tenant=tenant, month=month, year=year)

        for analytic in analytics:
            analytic.calculate_active_users_csv(month, year)
            analytic.calculate_monthly_revenue(tenant, month, year)
            return analytic

        if not analytics:
            analytics = MonthlyAnalytics.objects.create(tenant=tenant, month=month, year=year)
            return analytics
    
    @staticmethod
    def calculate_active_users_csv(month: None, year: None):
        # todo calculate active users
        try:
            active_users_csv = load_csv_file('analytics/active_user.csv')
        except FileNotFoundError:
            active_users_csv = {}

        user = MonthlyAnalytics.filter_by_month_year_csv(active_users_csv, year, month)
        active_user = 0
        user = user.values.tolist()
        for i in user:
              active_user += i[1]
            
        return active_user
    
    @staticmethod
    def filter_by_month_year_csv(df, year, month):
        """
            Filters a DataFrame by a specific month and year.
            Args:
                df (pd.DataFrame): The DataFrame containing a 'date' column to filter.
                year (int): The year to filter by.
                month (int): The month to filter by.
            Returns:
                pd.DataFrame: A DataFrame filtered to include only rows from the specified month and year.
            """
        try:
            df["date"] = pd.to_datetime(df["date"], format="%Y-%m")
            return df[(df["date"].dt.year == year) & (df["date"].dt.month == month)]
        except KeyError as e:
            print(f"KeyError: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"An error occurred: {e}")
            return pd.DataFrame()
    @staticmethod
    def calculate_monthly_revenue( tenant, month, year):
        return 0
    
    @staticmethod
    def past_twelve_months_active_users():
        months = MonthlyAnalytics.get_previous_twelve_months()
        data = []
        for month in months:
            data.append(MonthlyAnalytics.calculate_active_users_csv(month['month'], month['year']))

        return data

    
    @staticmethod
    def get_previous_twelve_months():
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        months = []
        month_choices_dict = {int(choice["value"]): choice["label"] for choice in MONTH_CHOICES}
        for i in range(0, 12):
            month = current_month - i
            year = current_year
            if month <= 0:
                month = 12 + month
                year = current_year - 1
            
            
            months.append(
                {'month': month,
                'month_name': month_choices_dict[month],
                'year': year}
        )
        return months
    @staticmethod
    def get_month_name(months):
        _months = []
        
        for month in months:
            month_name = month['month_name']
           
            _months.append( month_name)
        return _months
    
    @staticmethod
    def get_month_number(months):
        _months = []
        for month in months:
            month_no = month['month']
            _months.append(month_no)
        return _months
        
    
    @staticmethod
    def get_previous_twelve_months_csv():
        previous_months = MonthlyAnalytics.get_previous_twelve_months()
        csv_data = []
        csv_str = ""
        for month in previous_months:
            month_short = month["month_name"]
            month_short = month_short[:3]
            csv_str += f'{month_short},'
            
        csv_str = csv_str[:-1]    
        return csv_str
    
         

