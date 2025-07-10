from django import template
from core.models import Reponse

register = template.Library()

@register.inclusion_tag('core/partials/reponse_item.html', takes_context=True)
def show_reponses(context, reponse):
    reponses = Reponse.objects.filter(parent=reponse.pk)
    return {'reponses': reponses, 'user': context['user']}