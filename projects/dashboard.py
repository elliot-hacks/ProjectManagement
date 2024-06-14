from admin_tools.dashboard import Dashboard, AppIndexDashboard

class CustomIndexDashboard(Dashboard):
    columns = 3

class MyAppDashboard(AppIndexDashboard):
    # Define panels and modules here
    widgets = [
        'myapp.widgets.MyCustomWidget',
        'myapp.widgets.AnalyticsWidget',
    ]
