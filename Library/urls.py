from django.urls import path

from . import views

urlpatterns = [
    path("", views.book_list, name="book_list"),
    path("borrow/<int:book_id>/", views.borrow_book, name="borrow_book"),
    path("return/<int:loan_id>/", views.return_book, name="return_book"),
    path("search/", views.search_book, name="search_book"),
]
