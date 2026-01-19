import django_filters
from django.db.models import Q
from .models import MembershipApplication


class MembershipApplicationFilter(django_filters.FilterSet):
    """Filter for MembershipApplication queryset."""

    search = django_filters.CharFilter(method="filter_search")
    date_from = django_filters.DateFilter(field_name="date_applied", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date_applied", lookup_expr="lte")
    degree_program = django_filters.CharFilter(method="filter_degree_program")
    year_graduated = django_filters.CharFilter(
        field_name="year_graduated", lookup_expr="exact"
    )
    campus = django_filters.CharFilter(field_name="campus", lookup_expr="exact")
    province = django_filters.CharFilter(field_name="province", lookup_expr="icontains")
    mentorship = django_filters.BooleanFilter(field_name="join_mentorship_program")
    payment_method = django_filters.ChoiceFilter(
        field_name="payment_method",
        choices=[
            ("gcash", "GCash"),
            ("bank", "Bank Transfer"),
            ("cash", "Cash"),
        ],
    )

    class Meta:
        model = MembershipApplication
        fields = ["status"]

    def filter_search(self, queryset, name, value):
        """Search across multiple fields."""
        if not value:
            return queryset
        return queryset.filter(
            Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(email__icontains=value)
        )

    def filter_degree_program(self, queryset, name, value):
        """Filter by degree program name."""
        if not value:
            return queryset
        return queryset.filter(degree_program__icontains=value)


class RejectedApplicationFilter(MembershipApplicationFilter):
    """Extended filter for rejected applications."""

    rejection_stage = django_filters.ChoiceFilter(
        choices=[
            ("alumni_verification", "Alumni Verification"),
            ("payment_verification", "Payment Verification"),
        ]
    )
    rejected_from = django_filters.DateFilter(
        field_name="rejected_at", lookup_expr="gte"
    )
    rejected_to = django_filters.DateFilter(field_name="rejected_at", lookup_expr="lte")

    class Meta(MembershipApplicationFilter.Meta):
        fields = MembershipApplicationFilter.Meta.fields + ["rejection_stage"]
