from django.db import models
from django.core.exceptions import ValidationError


# ==============================
# BOOK MODEL (ADT Livre)
# ==============================
class Book(models.Model):
    isbn = models.CharField(max_length=13, unique=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    year = models.PositiveIntegerField()
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.isbn})"

    class Meta:
        ordering = ["title"]


# ==============================
# STUDENT MODEL
# ==============================
class Student(models.Model):
    matricule = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.name} ({self.matricule})"

    def can_borrow(self):
        active_loans = Loan.objects.filter(student=self, returned=False).count()
        return active_loans < 3


# ==============================
# LOAN MODEL (Allocation dynamique)
# ==============================
class Loan(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_borrowed = models.DateField(auto_now_add=True)
    returned = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.student.can_borrow():
            raise ValidationError("L'etudiant a atteint la limite d'emprunts.")

        if not self.book.available:
            raise ValidationError("Ce livre n'est pas disponible.")

        self.book.available = False
        self.book.save()

        super().save(*args, **kwargs)

    def return_book(self):
        self.returned = True
        self.book.available = True
        self.book.save()
        self.save()

    def __str__(self):
        return f"{self.student.name} borrowed {self.book.title}"
