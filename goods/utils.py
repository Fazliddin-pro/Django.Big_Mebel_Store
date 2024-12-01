from django.db.models import Q
from django.contrib.postgres.search import (
    SearchVector, SearchQuery, SearchRank, SearchHeadline
)
from goods.models import Products

def q_search(query):
    # Поиск по ID, если цифры и длина <= 5
    if query.isdigit() and len(query) <= 5:
        return Products.objects.filter(id=int(query))
    
    # Вектор поиска
    vector = SearchVector("name", "description")
    search_query = SearchQuery(query)
    
    # Ранжирование по релевантности
    results = Products.objects.annotate(
        rank=SearchRank(vector, search_query)
    ).filter(rank__gt=0).order_by("-rank")
    
    # Подсветка в 'name'
    results = results.annotate(
        headline=SearchHeadline(
            "name", search_query,
            start_sel='<span style="background-color: yellow;">',
            stop_sel="</span>"
        )
    )
    
    # Подсветка в 'description'
    results = results.annotate(
        bodyline=SearchHeadline(
            "description", search_query,
            start_sel='<span style="background-color: yellow;">',
            stop_sel="</span>"
        )
    )
    
    return results

def alternative_q_search(query):
    # Поиск по ID
    if query.isdigit() and len(query) <= 5:
        return Products.objects.filter(id=int(query))
    
    # Разделение запроса на слова
    keywords = [word for word in query.split() if len(word) > 2]
    q_objects = Q()

    # Условия поиска по 'name' и 'description'
    for token in keywords:
        q_objects |= Q(description__icontains=token)
        q_objects |= Q(name__icontains=token)

    return Products.objects.filter(q_objects)
