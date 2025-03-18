def user_role(request):
    role = None
    if request.user.is_authenticated:
        role = request.user.user_type  
    return {'role': role}  # This makes 'role' available in all templates
