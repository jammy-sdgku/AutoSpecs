import asyncio
import json
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages

from .models import SearchHistory
from .forms import YMMSearchForm, VINSearchForm
from .api import get_specs_by_ymm, get_specs_by_vin


def search_home(request):
    ymm_form = YMMSearchForm()
    vin_form = VINSearchForm()
    recent_searches = SearchHistory.objects.all()[:5]
    return render(request, 'carspecs/search.html', {
        'ymm_form': ymm_form,
        'vin_form': vin_form,
        'recent_searches': recent_searches,
    })


def search_ymm(request):
    if request.method != 'POST':
        return redirect('carspecs:search_home')

    form = YMMSearchForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Please correct the errors below.')
        return render(request, 'carspecs/search.html', {
            'ymm_form': form,
            'vin_form': VINSearchForm(),
        })

    year = form.cleaned_data['year']
    make = form.cleaned_data['make']
    model = form.cleaned_data['model']
    trim = form.cleaned_data.get('trim')

    try:
        result = get_specs_by_ymm(year, make, model, trim)

        if not result.get('success'):
            messages.error(request, result.get('message', 'No results found.'))
            return redirect('carspecs:search_home')

        SearchHistory.objects.create(
            search_type='ymm',
            year=year,
            make=make,
            model=model,
            trim=trim or '',
        )

        return render(request, 'carspecs/results.html', {
            'results': result['data'],
            'total': result.get('total', 0),
            'search_type': 'ymm',
            'query': f"{year} {make} {model}" + (f" {trim}" if trim else ""),
        })

    except Exception as e:
        messages.error(request, f"API error: {e}")
        return redirect('carspecs:search_home')


def search_vin(request):
    if request.method != 'POST':
        return redirect('carspecs:search_home')

    form = VINSearchForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Please correct the errors below.')
        return render(request, 'carspecs/search.html', {
            'ymm_form': YMMSearchForm(),
            'vin_form': form,
        })

    vin = form.cleaned_data['vin']

    try:
        result = get_specs_by_vin(vin)

        if not result.get('success'):
            messages.error(request, result.get('message', 'VIN not found.'))
            return redirect('carspecs:search_home')

        SearchHistory.objects.create(
            search_type='vin',
            vin=vin,
        )

        data = result['data']
        return render(request, 'carspecs/results.html', {
            'search_type': 'vin',
            'query': vin,
            'vin_data': data,
            'specs': data.get('specs', {}),
            'trims': data.get('trims', []),
        })

    except Exception as e:
        messages.error(request, f"API error: {e}")
        return redirect('carspecs:search_home')
