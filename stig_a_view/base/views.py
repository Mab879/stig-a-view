from django.views.generic.base import TemplateView

from stig_a_view.base import models as base_models


class StigIndex(TemplateView):
    template_name = 'base/stig_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stigs'] = base_models.Stig.objects.all()
        return context


class StigDetail(TemplateView):
    template_name = 'base/stig_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stig = base_models.Stig.objects.filter(id=context['id']).first()
        context['stig'] = stig
        context['controls'] = base_models.Control.objects.filter(stig_id=stig.id).select_related('cci').all()
        return context


class ControlView(TemplateView):
    template_name = 'base/control_detail.html'

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        if type(context['id']) == int:
            context['control'] = base_models.Control.objects.filter(id=context['id']).first()
        elif type(context['id']) == str:
            context['control'] = base_models.Control.objects.filter(disa_stig_id=context['id']).first()
        return context
