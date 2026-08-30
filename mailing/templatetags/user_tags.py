from django import template

register = template.Library()


@register.filter(name="has_group")
def has_group(user, group_name):
    """Фильтр для проверки, входит ли пользователь в указанную группу."""
    return user.groups.filter(name=group_name).exists()
