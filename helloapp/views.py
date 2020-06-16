from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .forms import NameForm


# Create your views here.
def get_name(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('helloapp:index'))
    else:
        form = NameForm()
    return render(request, 'hello/name.html', {'form': form})


def hello(request):
    return render(request, 'hello/hello.html')
