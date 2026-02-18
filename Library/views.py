from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Book, Loan, Student


def book_list(request):
    sort_by = request.GET.get("sort", "title")
    allowed_sorts = {"title", "author", "year"}
    if sort_by not in allowed_sorts:
        sort_by = "title"

    books = Book.objects.all().order_by(sort_by)
    return render(request, "library/book_list.html", {"books": books})


def search_book(request):
    query = (request.GET.get("q") or "").strip()
    books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query)
            | Q(author__icontains=query)
            | Q(isbn__icontains=query)
        )

    return render(request, "library/book_list.html", {"books": books})


def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    student = Student.objects.first()

    if student and book.available and student.can_borrow():
        Loan.objects.create(book=book, student=student)

    return redirect("book_list")


def return_book(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    if not loan.returned:
        loan.returned = True
        loan.book.available = True
        loan.book.save(update_fields=["available"])
        Loan.objects.filter(id=loan.id).update(returned=True)

    return redirect("book_list")
