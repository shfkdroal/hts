from __future__ import absolute_import
from django import forms
from .models import *

class SignInInReqForm(forms.ModelForm):

    class Meta:
        model = SignInReq
        fields = ('user_id', 'user_pw', 'bank_id', 'user_bank_name', 'user_name')

