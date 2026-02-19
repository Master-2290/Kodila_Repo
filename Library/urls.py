from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("catalogue/", views.book_list, name="book_list"),
    path("books/<int:book_id>/", views.book_detail, name="book_detail"),
    path("login/", views.student_login, name="student_login"),
    path("logout/", views.student_logout, name="student_logout"),
    path("borrow/<int:book_id>/", views.borrow_book, name="borrow_book"),
    path("return/<int:book_id>/", views.return_book, name="return_book"),
    path("search/", views.search_book, name="search_book"),
]
