import django_filters
from django.db.models import Q
from .models import Member


class MemberFilter(django_filters.FilterSet):
    """Filter for Member queryset."""

    search = django_filters.CharFilter(method="filter_search")
    date_from = django_filters.DateFilter(field_name="member_since", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="member_since", lookup_expr="lte")
    degree_program = django_filters.CharFilter(method="filter_degree_program")
    year_graduated = django_filters.CharFilter(method="filter_year_graduated")
    status = django_filters.CharFilter(method="filter_status")
    campus = django_filters.CharFilter(method="filter_campus")
    province = django_filters.CharFilter(method="filter_province")
    mentorship = django_filters.BooleanFilter(method="filter_mentorship")
    payment_method = django_filters.ChoiceFilter(
        method="filter_payment_method",
        choices=[
            ("gcash", "GCash"),
            ("bank", "Bank Transfer"),
            ("cash", "Cash"),
        ],
    )

    class Meta:
        model = Member
        fields = []

    def filter_search(self, queryset, name, value):
        """Search across name and email fields."""
        if not value:
            return queryset
        return queryset.filter(
            Q(full_name__icontains=value) | Q(email__icontains=value)
        )

    def filter_degree_program(self, queryset, name, value):
        """Filter by degree program name via application."""
        if not value:
            return queryset
        return queryset.filter(application__degree_program__icontains=value)

    def filter_year_graduated(self, queryset, name, value):
        """Filter by graduation year via application."""
        if not value:
            return queryset
        return queryset.filter(application__year_graduated=value)

    def filter_status(self, queryset, name, value):
        """Filter by member status: active, revoked, or all."""
        if not value or value.lower() == "all":
            return queryset
        elif value.lower() == "active":
            return queryset.filter(is_active=True)
        elif value.lower() == "revoked":
            return queryset.filter(is_active=False)
        return queryset

    def filter_campus(self, queryset, name, value):
        """Filter by campus via application."""
        if not value:
            return queryset
        return queryset.filter(application__campus=value)

    def filter_province(self, queryset, name, value):
        """Filter by province via application (partial match)."""
        if not value:
            return queryset
        return queryset.filter(application__province__icontains=value)

    def filter_mentorship(self, queryset, name, value):
        """Filter by mentorship interest via application."""
        if value is None:
            return queryset
        return queryset.filter(application__join_mentorship_program=value)

    def filter_payment_method(self, queryset, name, value):
        """Filter by payment method via application."""
        if not value:
            return queryset
        return queryset.filter(application__payment_method=value)
