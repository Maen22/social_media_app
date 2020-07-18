from django.core.exceptions import ValidationError
from django.db import models
from django.core import exceptions
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from .exceptions import AlreadyExistsError, AlreadyFriendsError, BlockedError
from django.contrib.auth import get_user_model


class FriendshipRequest(models.Model):
    """
        Model to represent friendship requests
    """

    from_user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="friendship_requests_sent",
    )
    to_user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="friendship_requests_received",

    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Friendship Request")
        verbose_name_plural = _("Friendship Requests")
        unique_together = ("from_user", "to_user")

    def __str__(self):
        return "%s" % self.from_user

    def accept(self, user1, user2):
        """
            Accept this friendship request
        """

        Friendship.objects.create(from_user=user1, to_user=user2)

        Friendship.objects.create(from_user=user2, to_user=user1)

        self.delete()

        # Delete any reverse requests
        FriendshipRequest.objects.filter(
            from_user=user1, to_user=user2
        ).delete()

        return True

    def reject(self, user1, user2):
        """
            reject this friendship request
        """

        FriendshipRequest.objects.filter(
            from_user=user1, to_user=user2
        ).delete()
        return True


class FriendshipManager(models.Manager):
    """
        Friendship manager
    """

    def are_friends(self, user1, user2):
        """
            Are these two users friends?
        """

        if Friendship.objects.get(to_user=user1, from_user=user2):
            return True
        else:
            return False

    def cant_send_request(self, from_user, to_user):
        """
            Checks if a request was sent
        """

        if from_user == to_user:
            return True

        if FriendshipRequest.objects.filter(
                from_user=from_user, to_user=to_user
        ).exists():
            return True

        return False

    def is_blocked(self, blocker, blocked):
        """
            Checks if a the user is blocked
        """

        if Block.objects.filter(
                blocker=blocker, blocked=blocked
        ).exists():
            return True

        return False

    def add_friend(self, from_user, to_user, message=None):
        """
            Create a friendship request
        """

        if from_user == to_user:
            raise ValidationError("Users cannot be friends with themselves")

        if self.are_friends(from_user, to_user):
            raise AlreadyFriendsError("Users are already friends")

        if self.cant_send_request(from_user, to_user):
            raise AlreadyExistsError("Friendship already requested")

        if self.is_blocked(to_user, from_user):
            raise BlockedError("User does not exists")

        request = FriendshipRequest.objects.create(
            from_user=from_user, to_user=to_user
        )

        request.save()

        return request

    def remove_friend(self, from_user, to_user):
        """
            Destroy a friendship relationship
        """

        try:
            qs = (
                Friendship.objects.filter(
                    Q(to_user=to_user, from_user=from_user)
                    | Q(to_user=from_user, from_user=to_user)
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

    to_user = models.ForeignKey(get_user_model(), models.CASCADE, related_name="friends")
    from_user = models.ForeignKey(
        get_user_model(), models.CASCADE, related_name="_unused_friend_relation"
    )
    created_at = models.DateTimeField(default=timezone.now)

    objects = FriendshipManager()

    class Meta:
        verbose_name = _("Friend")
        verbose_name_plural = _("Friends")
        unique_together = ("from_user", "to_user")

    def __str__(self):
        return "User #%s is friends with #%s" % (self.to_user, self.from_user)

    def save(self, *args, **kwargs):
        # users can't be friends with themselves
        if self.to_user == self.from_user:
            raise ValidationError("Users cannot be friends with themselves.")
        super(Friendship, self).save(*args, **kwargs)


class BlockManager(models.Manager):
    """
        Blocking manager
    """

    def add_block(self, blocker, blocked):

        if blocker == blocked:
            raise ValidationError("Users cannot block themselves")

        relation, created = Block.objects.get_or_create(
            blocker=blocker, blocked=blocked
        )

        qs = (
            Friendship.objects.filter(
                Q(to_user=blocked, from_user=blocker)
                | Q(to_user=blocker, from_user=blocked)
            )
                .distinct()
                .all()
        )

        if qs:
            qs.delete()

        if created is False:
            raise AlreadyExistsError(
                "User '%s' already blocked '%s'" % (blocker, blocked)
            )

        return relation

    def remove_block(self, blocker, blocked):

        try:
            rel = Block.objects.get(blocker=blocker, blocked=blocked)
            rel.delete()
            return True

        except exceptions.ObjectDoesNotExist:
            return False


class Block(models.Model):
    """ Model to represent block relationships """

    blocker = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="blocking"
    )
    blocked = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="blockees"
    )
    created_at = models.DateTimeField(default=timezone.now)

    objects = BlockManager()

    class Meta:
        verbose_name = _("Blocked Relationship")
        verbose_name_plural = _("Blocked Relationships")
        unique_together = ("blocker", "blocked")

    def __str__(self):
        return "User #%s blocks #%s" % (self.blocker, self.blocked)

    def save(self, *args, **kwargs):
        # Ensure users can't be friends with themselves
        if self.blocker == self.blocked:
            raise ValidationError("Users cannot block themselves.")
        super(Block, self).save(*args, **kwargs)
