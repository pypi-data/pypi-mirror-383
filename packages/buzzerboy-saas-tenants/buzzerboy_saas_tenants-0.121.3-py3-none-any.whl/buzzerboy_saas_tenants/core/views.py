from django.shortcuts import redirect
from django.utils.translation import activate
from django.conf import settings


def change_language(request):
    if request.method == 'POST':
        current_language = request.POST.get('current')
        selected_language = request.POST.get('language')
        next_url = request.POST.get('next', '/')
        # Ensure the selected language is valid
        if selected_language in dict(settings.LANGUAGES).keys():
            activate(selected_language)

            # Replace the language code in the URL
            next_url = next_url.replace(f'/{current_language}/', f'/{selected_language}/')
            
            return redirect(next_url)


