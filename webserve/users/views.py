from django.contrib import messages  # Import messages framework
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView
from .forms import CustomLoginForm

class LandingPageView(FormView):
    template_name = 'users/landing_page.html'
    form_class = CustomLoginForm

    def form_valid(self, form):
        email = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
            # Redirect the user to a different page after successful login
            return redirect('landing_page')  # Replace 'home' with the desired URL

    def form_invalid(self, form):
        # If login credentials are incorrect, re-render the form with error messages
        messages.error(self.request, 'Invalid email or password. Please try again.')
        return render(self.request, self.template_name, {'form': form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Welcome to the Landing Page'
        return context
