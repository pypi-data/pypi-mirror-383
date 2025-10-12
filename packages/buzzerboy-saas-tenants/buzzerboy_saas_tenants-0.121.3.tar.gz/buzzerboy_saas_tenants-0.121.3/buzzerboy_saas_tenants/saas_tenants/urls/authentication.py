
from django.urls import path, include # Import path for URL routing
from django.contrib.auth import views as auth_views  # Import Django's built-in authentication views

from buzzerboy_saas_tenants.saas_tenants.views  import authentication as views 
from buzzerboy_saas_tenants.saas_tenants.forms import authentication as forms
from ..views.account_settings import UserPasswordChangeView
from ..views.authentication import PasswordResetView, PasswordResetDoneView

urlpatterns = [

    
    # User login page
    path('login/', views.UserLoginView.as_view(), name='login'),
    # URL for the login page, using a custom view `UserLoginView`.
    # `name='login'` allows us to reference this URL elsewhere in the project easily.

    path('two-factor-email/', views.two_factor_email_verification, name='two-factor-email'),


    # User logout page
    path('logout/', views.logout_view, name='logout'),
    # URL for logging out the user, using the `logout_view` function.
    # Once logged out, the user is typically redirected to the login page.

    # Change password page
    path('password-change/', UserPasswordChangeView.as_view(), name='change_password'),
    # URL for changing the user's password, using a custom view `UserPasswordChangeView`.
    # This allows users to update their password after logging in.

    # Password reset request page
    path('password-reset/', PasswordResetView.as_view(
       
            template_name='pages/authentication/password-reset-form.html',
            email_template_name='registration/password_reset_email.html',
            html_email_template_name='registration/password_reset_email.html',
            form_class=forms.UserPasswordResetForm
        ), 
        name='password_reset'),
    # URL for requesting a password reset, using Django's built-in `PasswordResetView`.
    # `template_name` specifies the HTML file used for the password reset form.
    # `form_class` specifies a custom form to handle the input.

    # Password reset done page
    path('password-reset-done/', 
         PasswordResetDoneView.as_view(
             template_name='pages/authentication/password-reset-done.html'
         ), 
         name='password_reset_done'),
    # URL for the page that confirms the password reset email was sent.
    # This uses Django's `PasswordResetDoneView` and a custom template.

    # Password reset confirm page
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='pages/authentication/password-reset-confirm.html',
             form_class=forms.UserSetPasswordForm
         ), 
         name='password_reset_confirm'),
    # URL for confirming the password reset, allowing the user to set a new password.
    # `<uidb64>` and `<token>` are placeholders for the encoded user ID and reset token.
    # This view is handled by Django's `PasswordResetConfirmView` and uses a custom template and form.

    # Password reset complete page
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='pages/authentication/password-reset-complete.html'
         ), 
         name='password_reset_complete'),
    # URL for the final page after the password has been reset successfully.
    # It uses Django's `PasswordResetCompleteView` and a custom template to inform the user of the successful reset.


    path('user/<token>/create-password', views.create_password_invite, name='invite_create_password'),
    path('user/create-password/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='pages/authentication/password-create-complete.html'
         ), 
         name='password_create_complete'),

    # User registration page
    path('register/', views.UserRegisterView.as_view(), name='register'),
    # URL for the user registration page, using the `register` view.
    # `name='register'` allows us to reference this URL elsewhere in the project easily.


 # User activation page
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),

    # resent activation email
    path('resend-activation/', views.resent_activation_email, name='resend_activation'),


    # SSO SAML Login
    path('sso/login/', views.sso_login, name='sso_login'),

    path('two-factor-email/', views.two_factor_email_verification, name='two_factor_email'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('renew-otp/', views.renew_otp, name='renew_otp'),

    path('cancel-login/', views.cancel_login, name='cancel_login'),


    
]
