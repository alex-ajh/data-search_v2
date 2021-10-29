from django.contrib.auth.decorators import user_passes_test

def group_required(*group_names): 
    def in_groups(user):
        if user.is_authenticated: 
            if bool(user.groups.filter(name__in=group_names)) | user.is_superuser:             
                return True
        return False
    return user_passes_test(in_groups, login_url='/ps_data/') 
