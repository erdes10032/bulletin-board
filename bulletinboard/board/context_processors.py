from django.utils import timezone
import pytz


def timezone_context(request):
    tzname = request.session.get('django_timezone')
    if tzname:
        current_tz = pytz.timezone(tzname)
        current_time = timezone.now().astimezone(current_tz)
    else:
        current_time = timezone.now()

    return {
        'current_time': current_time,
    }