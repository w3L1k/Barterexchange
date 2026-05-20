from dataclasses import dataclass

from .models import Listing


@dataclass(frozen=True)
class MatchResult:
    listing: Listing
    priority: int
    reasons: tuple[str, ...]


MATCH_GROUP_TITLES = {
    1: 'Подходят по категории и находятся в вашем городе',
    2: 'Подходят по категории, но находятся в другом городе',
    3: 'Не подходят по искомой категории, но находятся в вашем городе',
}


def desired_category_ids(listing):
    ids = set(listing.desired_categories.values_list('id', flat=True))
    if ids:
        return ids
    return {listing.desired_category_id}


def match_candidate(source, candidate):
    reasons = []

    source_desired_ids = desired_category_ids(source)
    candidate_desired_ids = desired_category_ids(candidate)

    category_matches = candidate.category_id in source_desired_ids
    same_city = source.city.casefold() == candidate.city.casefold()
    reverse_category = source.category_id in candidate_desired_ids

    if category_matches and same_city:
        priority = 1
        reasons.append('подходит по категории и находится в вашем городе')
    elif category_matches:
        priority = 2
        reasons.append('подходит по категории, но находится в другом городе')
    elif same_city:
        priority = 3
        reasons.append('находится в вашем городе, но категория отличается')
    else:
        return None

    if reverse_category:
        reasons.append('владелец этого объявления тоже ищет вашу категорию')

    return MatchResult(candidate, priority, tuple(reasons))


def find_matches(source, limit=12):
    candidates = (
        Listing.objects.select_related('owner', 'category', 'desired_category')
        .prefetch_related('images', 'desired_categories')
        .filter(status=Listing.Status.ACTIVE)
        .exclude(owner=source.owner)
        .exclude(pk=source.pk)
    )
    matches = []
    for candidate in candidates:
        match = match_candidate(source, candidate)
        if match:
            matches.append(match)
    return sorted(
        matches,
        key=lambda match: (
            match.priority,
            not (source.category_id in desired_category_ids(match.listing)),
            -match.listing.pk,
        ),
    )[:limit]


def group_matches(matches):
    groups = []
    for priority, title in MATCH_GROUP_TITLES.items():
        grouped_matches = [match for match in matches if match.priority == priority]
        if grouped_matches:
            groups.append({'priority': priority, 'title': title, 'matches': grouped_matches})
    return groups
