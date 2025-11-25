from typing import Any

from django.db import models
from django.db.models import Case, Min, Max, Sum, When
from django.http import HttpRequest, JsonResponse

from data.models import ValueEntry, IndexedValueEntry
from data.utils import Timer

# percentile funcs should return the value and any relevant debug info

def calculate_percentile_db_ordering(model: models.Model, percentile: int) -> tuple[float, Any | None]:
    count = model.objects.count()
    offset = max(int((percentile / 100) * count) - 1, 0)
    return model.objects.order_by('value')[offset].value, None


def calculate_percentile_iterative_counts(model: models.Model, percentile: int) -> tuple[float, Any]:
    # on first iteration, calculate the min and max
    # then iterate and calculate how many values are above & below
    # don't actually need to count above AND below, do full-count once and then derive the other
    guess = 0.0

    first_result = model.objects.aggregate(
        count=models.Count('id'),
        min_value=Min('value'),
        max_value=Max('value'),
        count_above=Sum(Case(
            When(value__gt=guess, then=1),
            default=0,
        )),
    )
    count = first_result['count']
    min_value = first_result['min_value']
    max_value = first_result['max_value']
    count_above = first_result['count_above']
    count_below = count - count_above
    estimated_percentile = (count_below / count) * 100

    i = 0
    iterations = [(i, guess, estimated_percentile)]

    # iterate
    guess = min_value + ((max_value - min_value) * (percentile / 100))
    while abs(estimated_percentile - percentile) > 0.5 and i < 20:
        count_above = model.objects.filter(value__gt=guess).count()
        count_below = count - count_above
        estimated_percentile = (count_below / count) * 100

        i += 1
        iterations.append((i, guess, estimated_percentile))

        # interpolate new guess
        y1 = iterations[-2][2]
        y2 = iterations[-1][2]
        x1 = iterations[-2][1]
        x2 = iterations[-1][1]
        m = (y2 - y1) / (x2 - x1) if x2 != x1 else 0.0
        if m == 0.0:
            break
        c = y1 - m * x1
        guess = (percentile - c) / m

    print('-----     -----     -----')
    for iteration in iterations:
        print(f"Iteration {iteration[0]:2}: Guess={iteration[1]:.4f}, Estimated Percentile={iteration[2]:.2f}")
    print('-----     -----     -----')

    return guess, iterations


def percentile_view(request: HttpRequest) -> JsonResponse:
    percentile = int(request.GET.get("percentile", "50"))
    model = request.GET.get("model", "ValueEntry")  # ValueEntry or IndexedValueEntry
    method = request.GET.get("method", "1")

    func = {
        "1": calculate_percentile_db_ordering,
        "2": calculate_percentile_iterative_counts,
    }[method]

    model = {
        "ValueEntry": ValueEntry,
        "IndexedValueEntry": IndexedValueEntry,
    }[model]

    with Timer(f"Calculate {percentile}th percentile") as timer:
        value, debug_info = func(model, percentile)

    return JsonResponse({
        "method": method, 
        "model": model.__name__,
        "percentile": percentile, 
        "value": value, 
        "duration": timer.duration,
        "debug_info": debug_info,
    })
