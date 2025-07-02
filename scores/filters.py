from django_filters import FilterSet, CharFilter, DateFilter, DateTimeFilter
from datetime import datetime
from .models import Match


class MatchFilter(FilterSet):
    competition = CharFilter(
        field_name='competition__id',
        help_text='Filter matches by competition ID.'
    )
    status = CharFilter(
        field_name='status',
        help_text='Filter matches by their status (e.g., ongoing, finished).'
    )
    match_date_gt = DateTimeFilter(
        field_name='match_date',
        method='filter_match_date_gt',
        help_text='Filter matches with a date or datetime greater than the given value.'
    )
    match_date_lt = DateTimeFilter(
        field_name='match_date',
        method='filter_match_date_lt',
        help_text='Filter matches with a date or datetime less than the given value.'
    )

    class Meta:
        model = Match
        fields = ['competition', 'status', 'match_date_gt', 'match_date_lt']

    def filter_match_date_gt(self, queryset, name, value):
        return queryset.filter(match_date__gt=value)

    def filter_match_date_lt(self, queryset, name, value):
        return queryset.filter(match_date__lt=value)
