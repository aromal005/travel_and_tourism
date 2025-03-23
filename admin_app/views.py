from django.shortcuts import render

# Create your views here.
def admin_dashboard(request):
    return render(request, 'admin_app/admin_dashboard.html')

def customer_management(request):
    return render(request, 'admin_app/customer-management.html')

def agent_management(request):
    return render(request, 'admin_app/agent_management.html')



