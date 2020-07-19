from django.core import exceptions
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from profiles.models import Profile
from .exceptions import AlreadyExistsError, AlreadyFriendsError, BlockedError


class FriendshipManager(models.Manager):
    """
        Friendship manager
    """

    def validation(self, user1, user2, status):

        if Friendship.objects.filter(
                Q(user_one_id=user1, user_two_id=user2, status=status)
                | Q(user_one_id=user2, user_two_id=user1, status=status)
        ).exists():
            return True
        else:
            return False

    def add_friend(self, from_user, to_user):
        """
            Create a friendship request
        """

        if from_user == to_user:
            raise ValidationError("Users cannot be friends with themselves")

        if self.validation(from_user, to_user, 1):
            raise AlreadyExistsError("Friendship already requested")

        if self.validation(from_user, to_user, 2):
            raise AlreadyFriendsError("Users are already friends")

        friendship = Friendship.objects.create(
            user_one_id=from_user, user_two_id=to_user, status=1
        )

        friendship.save()

        # return friendship

    def accept(self, user1, user2):
        """
            Accept this friendship request
        """

        friendship = Friendship.objects.filter(
            user_one_id=user1, user_two_id=user2, status=1
        )

        if friendship:
            friendship.status = 2
            friendship.save()
            return True
        return exceptions.ObjectDoesNotExist()

    def reject(self, user1, user2):
        """
            reject this friendship request
        """

        friendship = Friendship.objects.filter(
            user_one_id=user1, user_two_id=user2, status=1
        )

        if friendship:
            friendship.status = 3
            friendship.save()
            return True

        return exceptions.ObjectDoesNotExist()

    def remove_friend(self, from_user, to_user):
        """
            Destroy a friendship relationship
        """

        try:
            qs = (
                Friendship.objects.filter(
                    Q(user_one_id=to_user, user_two_id=from_user, status=2)
                    | Q(user_one_id=from_user, user_two_id=to_user, status=2)
                )
                    .distinct()
                    .all()
            )

            if qs:
                qs.delete()
                return True
            else:
                return False
        except exceptions.ObjectDoesNotExist:
            return False


class Friendship(models.Model):
    """
        Model to represent Friendships
    """

    class Status(models.IntegerChoices):
        PENDING = 1
        ACCEPTED = 2
        DECLINED = 3

    user_one_id = models.ForeignKey(Profile, models.CASCADE, related_name="friends")

    user_two_id = models.ForeignKey(
        Profile, models.CASCADE, related_name="_unused_friend_relation"
    )

    status = models.IntegerField(choices=Status.choices, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    objects = FriendshipManager()

    class Meta:
        verbose_name = _("Friend")
        verbose_name_plural = _("Friends")
        unique_together = ("user_one_id", "user_two_id")

    def __str__(self):
        return f"User {self.user_one_id} is friend with user {self.user_two_id}"

    def save(self, *args, **kwargs):
        # users can't be friends with themselves
        if self.user_one_id == self.user_two_id:
            raise ValidationError("Users cannot be friends with themselves.")
        super(Friendship, self).save(*args, **kwargs)
