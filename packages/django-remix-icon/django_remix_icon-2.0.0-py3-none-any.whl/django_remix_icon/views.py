"""
Views for RemixIcon autocomplete functionality.
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import View

from .remix_icons import REMIX_ICONS


class IconSearchView(View):
    """
    AJAX view for searching RemixIcons.

    Returns JSON response with matching icons for autocomplete functionality.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        """
        Handle GET request for icon search.

        Query parameters:
        - q: search query string
        - limit: maximum number of results (default: 20)
        - category: filter by category (optional)
        """
        query = request.GET.get('q', '').lower().strip()
        limit = int(request.GET.get('limit', 20))
        category_filter = request.GET.get('category', '').strip()

        results = []

        # Iterate through categories and icons
        for category, icons in REMIX_ICONS.items():
            # Skip if category filter is specified and doesn't match
            if category_filter and category.lower() != category_filter.lower():
                continue

            for icon_name, keywords in icons.items():
                # Stop if we've reached the limit
                if len(results) >= limit:
                    break

                full_icon_name = f"ri-{icon_name}"

                # If no query, just add icons (useful for initial display)
                if not query:
                    results.append({
                        'value': full_icon_name,
                        'label': icon_name.replace('-', ' ').title(),
                        'icon': full_icon_name,
                        'category': category,
                        'score': 0
                    })
                    continue

                # Calculate relevance score
                score = 0
                icon_name_lower = icon_name.lower()
                keywords_lower = keywords.lower()

                # Exact match in icon name (highest priority)
                if icon_name_lower == query:
                    score = 1000
                # Starts with query in icon name
                elif icon_name_lower.startswith(query):
                    score = 900
                # Contains query in icon name
                elif query in icon_name_lower:
                    score = 800
                # Exact match in keywords
                elif f",{query}," in f",{keywords_lower},":
                    score = 700
                # Starts with query in any keyword
                elif any(keyword.startswith(query) for keyword in keywords_lower.split(',')):
                    score = 600
                # Contains query in keywords
                elif query in keywords_lower:
                    score = 500
                # Category match
                elif query in category.lower():
                    score = 400

                # If we have a match, add to results
                if score > 0:
                    results.append({
                        'value': full_icon_name,
                        'label': icon_name.replace('-', ' ').title(),
                        'category': category,
                        'score': score
                    })

            # Stop if we've reached the limit
            if len(results) >= limit:
                break

        # Sort by score (highest first) and limit results
        results.sort(key=lambda x: x['score'], reverse=True)
        results = results[:limit]

        # Remove score from final output (used only for sorting)
        for result in results:
            result.pop('score', None)

        return JsonResponse({
            'results': results,
            'total': len(results)
        })

    def post(self, request):
        """
        Handle POST request for icon search (same as GET).
        """
        return self.get(request)


@require_http_methods(["GET"])
def icon_list_view(request):
    """
    Simple view that returns all available icons with categories.
    Useful for debugging or getting the complete list.
    """
    category_filter = request.GET.get('category', '').strip()

    icons = []
    categories = {}

    for category, category_icons in REMIX_ICONS.items():
        # Skip if category filter is specified and doesn't match
        if category_filter and category.lower() != category_filter.lower():
            continue

        categories[category] = []

        for icon_name, keywords in category_icons.items():
            full_icon_name = f"ri-{icon_name}"
            icon_data = {
                'value': full_icon_name,
                'label': icon_name.replace('-', ' ').title(),
                'icon': full_icon_name,
                'category': category,
                'keywords': keywords
            }
            icons.append(icon_data)
            categories[category].append(icon_data)

    return JsonResponse({
        'icons': icons,
        'categories': categories,
        'total': len(icons)
    })
