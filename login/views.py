from email.message import EmailMessage

from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from django.conf import settings
from .forms import *
from .tokens import account_activation_token
import requests


def reCAPTCHA_validation(recaptcha_response, remoteip=None):
    payloads = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response,
    }
    if remoteip is not None:
        payloads['remoteip'] = remoteip
    r = requests.post(settings.GOOGLE_RECAPTCHA_AUTHENTICATION_URL, data=payloads)
    result = r.json()
    return result.get('success', False)


# Create your views here.
def signup(request):
    if request.method == 'POST':
        user_form = SignupForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            if reCAPTCHA_validation(recaptcha_response):
                user = user_form.save(commit=False)
                profile = profile_form.save(commit=False)
                # profile.user = user
                # profile_form.save()
                user.profile = profile
                user.profile.is_active = False
                user.save()

                current_site = get_current_site(request)
                mail_subject = 'Activate your blog account.'
                message = render_to_string('login/active_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                to_email = user_form.cleaned_data.get('email')
                email = EmailMessage(
                    subject=mail_subject,
                    body=message,
                    to=[to_email, ]
                )
                email.send()
                return HttpResponse('Please confirm your email address to complete the registration.')
            return HttpResponse('Invalid reCAPTCHA, please try again!')
    else:
        # user_form = SignupForm(instance=request.user)
        # profile_form = ProfileForm(instance=request.user.profile)
        user_form = SignupForm()
        profile_form = ProfileForm()
    return render(request, 'login/signup.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, TypeError, OverflowError, ValueError):
        user = None
    if user is not None and account_activation_token.check_token(user, token=token):
        if not user.profile.is_active:
            user.profile.is_active = True
            user.save()
            login(request, user)
            return HttpResponse('Thanks for your confirmation!')
        return HttpResponse('Your account already activated!')
    else:
        return HttpResponse('Activation link is invalid!')
