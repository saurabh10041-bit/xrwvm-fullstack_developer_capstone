# Uncomment the required imports before adding the code

# from django.shortcuts import render
# from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
# from django.contrib.auth import logout
# from django.contrib import messages
# from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)


# Create a `logout_request` view to handle sign out request
def logout_request(request):

    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)


# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):

    data = json.loads(request.body)

    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']

    username_exists = User.objects.filter(username=username).exists()

    if username_exists:
        return JsonResponse({
            "userName": username,
            "error": "Already Registered"
        })

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name
    )

    login(request, user)

    return JsonResponse({
        "userName": username,
        "status": "Authenticated"
    })


def get_dealerships(request, state=None):
    if request.method == "GET":
        if state:
            dealerships = get_request(f"/fetchDealers/{state}")
        else:
            dealerships = get_request("/fetchDealers")

        return JsonResponse({"status": 200, "dealers": dealerships})


@csrf_exempt
def add_review(request):
    if request.method == "POST":
        review_data = json.loads(request.body)

        sentiment = analyze_review_sentiments(review_data["review"])
        review_data["sentiment"] = sentiment.get("sentiment", "neutral")

        result = post_review(review_data)

        return JsonResponse(result)


def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        dealer = get_request(f"/fetchDealer/{dealer_id}")
        return JsonResponse({"status": 200, "dealer": dealer})

# Create a `add_review` view to submit a review
# def add_review(request):
# ...


def get_cars(request):
    count = CarMake.objects.filter().count()

    if count == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')

    cars = []

    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })

    return JsonResponse({"CarModels": cars})


def get_dealer_reviews(request, dealer_id):
    if request.method == "GET":
        reviews = get_request("/fetchReviews", dealerId=str(dealer_id))

        for review in reviews:
            if "review" in review:
                sentiment = analyze_review_sentiments(review["review"])
                review["sentiment"] = sentiment.get("sentiment", "neutral")

        return JsonResponse({"status": 200, "reviews": reviews})
