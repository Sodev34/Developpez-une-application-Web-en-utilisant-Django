from django.contrib.auth.models import User
from django.db.models import Q

from critique.models import Review, Ticket
from authentification.models import UserFollow


def find_viewable_reviews(user: User):
    follow_users = find_user_follows(user) + [user]
    reviews = Review.objects.filter(
        Q(user__in=follow_users) | Q(ticket__user=user)
    ).distinct()

    return reviews

def find_viewable_tickets(user: User):
    followed_users = find_user_follows(user) + [user]
    replied_tickets = Review.objects.filter(user__in=followed_users).values_list("ticket", flat=True)
    tickets = Ticket.objects.exclude(id__in=replied_tickets).filter(user__in=followed_users)
    return tickets


def find_tickets_validate(tickets):
    replied_reviews = Review.objects.filter(ticket__in=tickets)
    replied_tickets = [review.ticket for review in replied_reviews]
    return replied_tickets, replied_reviews


def find_user_follows(user):
    follows = UserFollow.objects.filter(user=user)
    followed_users = [follow.followed_user for follow in follows]
    return followed_users

