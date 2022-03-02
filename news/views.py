import json

from bson.json_util import dumps
from django.http import JsonResponse
from pymongo import MongoClient

my_client = MongoClient(
    "mongodb://34.64.216.132:27017/", username="project2", password="6DevkdZirJ"
)
newsDB = my_client["newsDB"]

sample_col = newsDB["predict"]
count_col = newsDB["premade"]
case_col = newsDB["case"]
sentiment_col = newsDB["graph"]


def count(request):
    date = request.GET.get("date")
    keyword = request.GET.get("keyword")
    press = request.GET.get("press")

    query = {"$and": [{"날짜": {"$regex": f"{date}"}}, {"키워드": keyword}, {"언론사": press}]}
    data = list(count_col.find(query, {"_id": 0}))

    return JsonResponse(data, safe=False)


def case(request):
    date = request.GET.get("date")

    if date == "전체":
        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$case"}}}]
        cases = list(case_col.aggregate(pipeline))[0]
    else:
        query = {"date": date}
        cases = case_col.find(query, {"_id": 0})[0]

    return JsonResponse(cases, safe=False)


def graph(request):
    case_data = case_col.find({}, {"_id": 0})
    sentiment_data = sentiment_col.find({}, {"_id": 0})

    dumped1 = dumps(case_data)
    loaded1 = json.loads(dumped1)
    dumped2 = dumps(sentiment_data)
    loaded2 = json.loads(dumped2)

    result = {"case_stats": loaded1, "sentiment_stats": loaded2}

    return JsonResponse(result)


def newslist(request):
    date = request.GET.get("date")
    keyword = request.GET.get("keyword")
    press = request.GET.get("press")

    # pagination
    page = int(request.GET.get("page", 1))
    limit = 20
    offset = (page - 1) * limit

    query_arr = []
    if date != "전체":
        query_arr.append({"time": {"$regex": f"{date}"}})
    if press != "전체":
        query_arr.append({"text_company": press})
    if keyword != "전체":
        query_arr.append({"text_headline": {"$regex": f"{keyword}"}})

    if date == "전체" and press == "전체" and keyword == "전체":
        data = list(
            sample_col.find({}, {"_id": 0, "text_context": 0})
            .limit(limit)
            .skip(offset)
        )
    else:
        query = {"$and": query_arr}
        data = list(
            sample_col.find(query, {"_id": 0, "text_context": 0})
            .limit(limit)
            .skip(offset)
        )

    return JsonResponse(data, safe=False)


def press(request):
    date = request.GET.get("date")
    keyword = request.GET.get("keyword")

    pipeline = [
        {"$match": {"날짜": {"$regex": f"{date}"}, "키워드": keyword}},
        {
            "$group": {
                "_id": "$언론사",
                "normal": {"$first": "$노말비율"},
                "minus": {"$first": "$부정비율"},
                "plus": {"$first": "$긍정비율"},
            }
        },
    ]

    sentiment = list(count_col.aggregate(pipeline))

    return JsonResponse(sentiment, safe=False)
