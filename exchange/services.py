from dataclasses import dataclass

from .models import Listing


@dataclass(frozen=True)
class MatchResult:
    listing: Listing
    priority: int
    reasons: tuple[str, ...]


def match_candidate(source, candidate):
    reasons = []

    category_matches = source.desired_category_id == candidate.category_id
    same_city = source.city.casefold() == candidate.city.casefold()
    reverse_category = candidate.desired_category_id == source.category_id

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
        .prefetch_related('images')
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
            not (match.listing.desired_category_id == source.category_id),
            -match.listing.pk,
        ),
    )[:limit]
