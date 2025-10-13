"""Decorators for Member Audit."""

from functools import wraps

from django.core.cache import cache
from django.http import HttpResponseForbidden, HttpResponseNotFound

from allianceauth.services.hooks import get_extension_logger
from app_utils.esi import EsiDailyDowntime, fetch_esi_status
from app_utils.logging import LoggerAddTag

from memberaudit import __title__
from memberaudit.constants import IS_TESTING

logger = LoggerAddTag(get_extension_logger(__name__), __title__)

ESI_STATUS_CACHE_TIMEOUT = 5
"""Calls to the ESI status endpoint by the when_esi_is_available decorator
 are cached for this duration in seconds.
 """


def fetch_character_if_allowed(*args_select_related):
    """Assert the current user has access to the character
    and load the given character if it exists.

    Args:
    - Optionally add list of parameters to be passed through to select_related().
    Note that "character_ownership" is already included.

    Returns:
    - 403 if user has no access
    - 404 if character does not exist
    """
    from .models import Character

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, character_pk, *args, **kwargs):
            try:
                args_select_related_2 = args_select_related + (
                    "eve_character",
                    "eve_character__character_ownership__user",
                    "eve_character__character_ownership__user__profile__main_character",
                )
                character = Character.objects.select_related(
                    *args_select_related_2
                ).get(pk=character_pk)
            except Character.DoesNotExist:
                return HttpResponseNotFound()

            if not character.user_has_access(request.user):
                return HttpResponseForbidden()

            return view_func(request, character_pk, character, *args, **kwargs)

        return _wrapped_view

    return decorator


def fetch_token_for_character(scopes=None):
    """Fetch and add valid token for a character.
    Needs to be attached on a character section manager method !!

    Args:
        -scopes: Optionally provide the required scopes.
            Otherwise will use all scopes defined for this character.
    """

    def decorator(func):
        @wraps(func)
        def _wrapped_view(self, character, *args, **kwargs):
            token = character.fetch_token(scopes)
            logger.debug(
                "%s: Using token %s for `%s`",
                token.character_name,
                token.pk,
                func.__name__,
            )
            return func(self, character, token, *args, **kwargs)

        return _wrapped_view

    return decorator


def when_esi_is_available(func):
    """Make sure the decorated task only runs when esi is available.

    Raise exception when ESI is offline.
    Complete the task without running it when downtime is detected.

    Automatically disabled during tests.
    """

    @wraps(func)
    def outer(*args, **kwargs):
        if IS_TESTING is not True:
            key = "when-esi-is-available-status"
            status = cache.get(key)
            if not status:
                try:
                    status = fetch_esi_status()
                except EsiDailyDowntime:
                    logger.info("Daily Downtime detected. Aborting.")
                    return None  # function will not run

                cache.set(key, status, timeout=ESI_STATUS_CACHE_TIMEOUT)

            status.raise_for_status()

        return func(*args, **kwargs)

    return outer
