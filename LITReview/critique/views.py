
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Value, CharField
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import DeleteView

from .forms import ReviewForm, TicketForm
from .models import Review, Ticket
from .complements import (
    find_viewable_reviews,
    find_viewable_tickets,
    find_tickets_validate,
    find_user_follows,
)


# -------- FLUX --------
@login_required
def flux(request):
    followed_users = find_user_follows(request.user)

    reviews = find_viewable_reviews(request.user)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = find_viewable_tickets(request.user)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    replied_tickets, replied_reviews = find_tickets_validate(tickets)

    posts_list = sorted(chain(reviews, tickets), key=lambda post: post.time_created, reverse=True)

    if posts_list:
        paginator = Paginator(posts_list, 5)
        page = request.GET.get('page')
        posts = paginator.get_page(page)
    else:
        posts = None

    context = {
        'posts': posts,
        'r_tickets': replied_tickets,
        'r_reviews': replied_reviews,
      #  'title': 'Flux',
        'followed_users': followed_users
    }

    return render(request, 'critique/flux.html', context)


@login_required
def posts(request, pk=None):
    if pk:
        user = get_object_or_404(User, id=pk)
    else:
        user = request.user

    followed_users = find_user_follows(request.user)

    reviews = Review.objects.filter(user=user)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = Ticket.objects.filter(user=user)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    replied_tickets, replied_reviews = find_tickets_validate(tickets)

    posts_list = sorted(chain(reviews, tickets), key=lambda post: post.time_created, reverse=True)

    if posts_list:
        paginator = Paginator(posts_list, 5)
        page = request.GET.get('page')
        posts = paginator.get_page(page)
        total_posts = paginator.count
    else:
        posts = None
        total_posts = 0

    context = {
        'posts': posts,
        'title': f"Mes posts ({total_posts})",
        'r_tickets': replied_tickets,
        'r_reviews': replied_reviews,
        'followed_users': followed_users
    }

    return render(request, 'critique/flux.html', context)


# -------- Reviews --------

@login_required
def create_review(request):
    if request.method == 'POST':
        t_form = TicketForm(request.POST, request.FILES)
        r_form = ReviewForm(request.POST)

        if t_form.is_valid() and r_form.is_valid():
            try:
                image = request.FILES['image']
            except MultiValueDictKeyError:
                image = None

            t = Ticket.objects.create(
                user=request.user,
                title=request.POST['title'],
                description=request.POST['description'],
                image=image
            )
            t.save()
            Review.objects.create(
                ticket=t,
                user=request.user,
                headline=request.POST['headline'],
                rating=request.POST['rating'],
                body=request.POST['body']
            )
            return redirect('flux')

    else:
        t_form = TicketForm()
        r_form = ReviewForm()

    context = {
        't_form': t_form,
        'r_form': r_form,
        'title': 'Créer une critique'
    }

    return render(request, 'critique/create_review.html', context)


@login_required
def review_response(request, pk):
    ticket = get_object_or_404(Ticket, id=pk)

    if request.method == 'POST':
        r_form = ReviewForm(request.POST)

        if r_form.is_valid():
            Review.objects.create(
                ticket=ticket,
                user=request.user,
                headline=request.POST['headline'],
                rating=request.POST['rating'],
                body=request.POST['body']
            )

            return redirect('flux')

    else:
        r_form = ReviewForm()

    context = {
        'r_form': r_form,
        'post': ticket,
        'title': 'Crée une critique'
    }

    return render(request, 'critique/create_review.html', context)


@login_required
def review_update(request, pk):
    review = get_object_or_404(Review, id=pk)
    if review.user != request.user:
        raise PermissionDenied()

    if request.method == 'POST':
        r_form = ReviewForm(request.POST, instance=review)

        if r_form.is_valid():
            r_form.save()
            return redirect('flux')

    else:
        r_form = ReviewForm(instance=review)

    context = {
        'r_form': r_form,
        'post': review.ticket,
        'title': 'Modifier votre critique'
    }

    return render(request, 'critique/create_review.html', context)


@login_required
def review_detail(request, pk):
    review = get_object_or_404(Review, id=pk)
    followed_users = find_user_follows(request.user)

    context = {
        'post': review,
        'title': 'Critique du livre',
        'followed_users': followed_users
    }

    return render(request, 'critique/post_detail.html', context)


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    success_url = '/flux'
    context_object_name = 'post'

    def test_func(self):
        review = self.get_object()
        if self.request.user == review.user:
            return True
        return False

    def delete(self, request, *args, **kwargs):
        return super(ReviewDeleteView, self).delete(request, *args, **kwargs)


# -------- Tickets --------

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)

        if form.is_valid():
            image = request.FILES.get('image', None)
            Ticket.objects.create(
                user=request.user,
                title=request.POST['title'],
                description=request.POST['description'],
                image=image
            )
         
            return redirect('flux')

    else:
        form = TicketForm()

    context = {
        'form': form,
        'title': 'Crée un ticket'
    }

    return render(request, 'critique/create_ticket.html', context)


@login_required
def ticket_update(request, pk):
    ticket = get_object_or_404(Ticket, id=pk)
    if ticket.user != request.user:
        raise PermissionDenied()

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)

        if form.is_valid():
            form.save()
            return redirect('flux')

    else:
        form = TicketForm(instance=ticket)

    context = {
        'form': form,
        'title': 'Modifer votre ticket'
    }

    return render(request, 'critique/create_ticket.html', context)


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, id=pk)
    followed_users = find_user_follows(request.user)

    replied_tickets, replied_reviews = find_tickets_validate([ticket])

    context = {
        'post': ticket,
        'title': 'Ticket',
        'r_tickets': replied_tickets,
        'r_reviews': replied_reviews,
        'followed_users': followed_users,
    }

    return render(request, 'critique/post_detail.html', context)


class TicketDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ticket
    success_url = '/flux'
    context_object_name = 'post'

    def test_func(self):
        ticket = self.get_object()
        if self.request.user == ticket.user:
            return True
        return False

    def delete(self, request, *args, **kwargs):
        return super(TicketDeleteView, self).delete(request, *args, **kwargs)