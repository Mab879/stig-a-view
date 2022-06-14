import urllib.request
import xml.etree.ElementTree as ET

from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from stig_a_view.base import actions as base_actions
from stig_a_view.base import models as base_models
from stig_a_view.base import forms as base_forms


class StigIndex(TemplateView):
    template_name = 'base/stig_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stigs'] = base_models.Stig.objects.select_related("product").all()
        return context


class StigDetail(TemplateView):
    template_name = 'base/stig_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stig = base_models.Stig.objects.filter(id=context['id']).first()
        context['stig'] = stig
        context['controls'] = base_models.Control.objects.filter(stig_id=stig.id).select_related('cci')\
            .order_by('disa_stig_id').all()
        return context


class ControlView(TemplateView):
    template_name = 'base/control_detail.html'

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        if type(context['id']) == int:
            context['control'] = base_models.Control.objects.filter(stig_id=context['stig_id'],
                                                                    id=context['id']).first()
        elif type(context['id']) == str:
            context['control'] = base_models.Control.objects.filter(stig_id=context['stig_id'],
                                                                    disa_stig_id=context['id']).first()
        return context


class ProductView(TemplateView):
    template_name = 'base/product.html'

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        if type(context['id']) == int:
            product = base_models.Product.objects.filter(id=context['id']).first()
        else:
            product = base_models.Product.objects.filter(short_name=context['id']).first()
        context['stigs'] = base_models.Stig.objects.filter(product=product).all()
        context['product'] = product
        return context


class ImportStigView(LoginRequiredMixin, TemplateView):
    template_name = 'base/import_stig.html'

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        form = base_forms.ImportStigUrlForm()
        context['form'] = form
        return context

    def post(self, request):
        form = base_forms.ImportStigUrlForm(request.POST)
        if form.is_valid():
            with urllib.request.urlopen(form.cleaned_data['url']) as response:
                stig_xml = str(response.read(), 'utf-8')
                root = ET.ElementTree(ET.fromstring(stig_xml)).getroot()
                base_actions.process_stig_xml(form.cleaned_data['product'].short_name, form.cleaned_data['version'],
                                              form.cleaned_data['release'], form.cleaned_data['release_date'],
                                              root)
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/?import_failed')
