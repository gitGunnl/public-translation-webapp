from django import template
register = template.Library()

@register.filter
def index(sequence, position):
    try:
        return sequence[int(position)]
    except:
        return ''

@register.filter
def get_range(start, end):
    return range(int(start), int(end))