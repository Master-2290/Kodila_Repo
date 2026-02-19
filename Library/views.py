from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import Book, Loan, Student


def home(request):
    return render(request, "library/base.html", {"logged_student": get_logged_student(request)})


def get_safe_next_url(request, candidate_url):
    if candidate_url and url_has_allowed_host_and_scheme(
        candidate_url, allowed_hosts={request.get_host()}
    ):
        return candidate_url
    return reverse("book_list")


def get_logged_student(request):
    student_id = request.session.get("student_id")
    if not student_id:
        return None
    return Student.objects.filter(id=student_id).first()


def require_student_login(request):
    student = get_logged_student(request)
    if student:
        return student, None

    next_candidate = (
        request.POST.get("next")
        or request.GET.get("next")
        or request.META.get("HTTP_REFERER")
        or reverse("book_list")
    )
    next_url = get_safe_next_url(request, next_candidate)

    messages.error(request, "Veuillez vous connecter pour effectuer cette action.")
    login_url = f"{reverse('student_login')}?next={next_url}"
    return None, redirect(login_url)


def student_login(request):
    if request.method == "POST":
        matricule = (request.POST.get("matricule") or "").strip()
        next_url = get_safe_next_url(request, request.POST.get("next"))

        student = Student.objects.filter(matricule=matricule).first()
        if student:
            request.session["student_id"] = student.id
            messages.success(request, f"Connexion reussie: {student.name}.")
            return redirect(next_url)

        messages.error(request, "Matricule introuvable. Verifiez dans l'admin.")

    next_url = get_safe_next_url(request, request.GET.get("next"))
    context = {
        "next_url": next_url,
        "logged_student": get_logged_student(request),
    }
    return render(request, "library/login.html", context)


@require_POST
def student_logout(request):
    request.session.pop("student_id", None)
    messages.info(request, "Vous etes deconnecte.")
    return redirect("book_list")


def book_list(request):
    sort_by = request.GET.get("sort", "title")
    allowed_sorts = {"title", "author", "year"}
    if sort_by not in allowed_sorts:
        sort_by = "title"

    books = Book.objects.all().order_by(sort_by)
    return render(
        request,
        "library/book_list.html",
        {"books": books, "logged_student": get_logged_student(request)},
    )


def search_book(request):
    query = (request.GET.get("q") or "").strip()
    books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query)
            | Q(author__icontains=query)
            | Q(isbn__icontains=query)
        )

    return render(
        request,
        "library/book_list.html",
        {"books": books, "logged_student": get_logged_student(request)},
    )


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    student = get_logged_student(request)
    active_loan = None

    if student:
        active_loan = Loan.objects.filter(
            book=book,
            student=student,
            returned=False,
        ).first()

    context = {
        "book": book,
        "active_loan": active_loan,
        "logged_student": student,
    }
    return render(request, "library/book_detail.html", context)


@require_POST
def borrow_book(request, book_id):
    student, redirect_response = require_student_login(request)
    if redirect_response:
        return redirect_response

    book = get_object_or_404(Book, id=book_id)
    next_url = request.POST.get("next") or reverse("book_detail", args=[book.id])

    if book.available and student.can_borrow():
        Loan.objects.create(book=book, student=student)
        messages.success(request, "Livre emprunte avec succes.")
    elif not book.available:
        messages.error(request, "Ce livre est indisponible.")
    else:
        messages.error(request, "Limite d'emprunts atteinte (3).")

    return redirect(next_url)


@require_POST
def return_book(request, book_id):
    student, redirect_response = require_student_login(request)
    if redirect_response:
        return redirect_response

    book = get_object_or_404(Book, id=book_id)
    next_url = request.POST.get("next") or reverse("book_detail", args=[book.id])

    loan = Loan.objects.filter(book=book, student=student, returned=False).first()
    if loan:
        loan.returned = True
        book.available = True
        book.save(update_fields=["available"])
        Loan.objects.filter(id=loan.id).update(returned=True)
        messages.success(request, "Livre restitue avec succes.")
    else:
        messages.error(request, "Aucun emprunt actif trouve pour ce livre.")

    return redirect(next_url)
