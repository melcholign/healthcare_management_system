from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse

def account_permission(account_type):
    def wrapper(view):
        def sub_wrapper(request, *args, **kwargs):
            
            if 'account_user' not in request.session:
                HttpResponseRedirect(reverse('account_login'))
                
            if request.session['account_data']['account_type'] != account_type:
                return HttpResponseForbidden()
            
            return view(request, *args, **kwargs)
        
        return sub_wrapper
    
    return wrapper
    