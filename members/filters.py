import django_filters
from django.db.models import Q
from .models import Member


class MemberFilter(django_filters.FilterSet):
    """Filter for Member queryset."""
    
    search = django_filters.CharFilter(method='filter_search')
    date_from = django_filters.DateFilter(field_name='member_since', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='member_since', lookup_expr='lte')
    degree_program = django_filters.CharFilter(method='filter_degree_program')
    year_graduated = django_filters.CharFilter(method='filter_year_graduated')
    status = django_filters.CharFilter(method='filter_status')

    class Meta:
        model = Member
        fields = []

    def filter_search(self, queryset, name, value):
        """Search across name and email fields."""
        if not value:
            return queryset
        return queryset.filter(
            Q(full_name__icontains=value) |
            Q(email__icontains=value)
        )

    def filter_degree_program(self, queryset, name, value):
        """Filter by degree program name via application."""
        if not value:
            return queryset
        return queryset.filter(application__degree_program__name__icontains=value)

    def filter_year_graduated(self, queryset, name, value):
        """Filter by graduation year via application."""
        if not value:
            return queryset
        return queryset.filter(application__year_graduated=value)

    def filter_status(self, queryset, name, value):
        """Filter by member status: active, revoked, or all."""
        if not value or value.lower() == 'all':
            return queryset
        elif value.lower() == 'active':
            return queryset.filter(is_active=True)
        elif value.lower() == 'revoked':
            return queryset.filter(is_active=False)
        return queryset
