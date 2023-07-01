from datetime import timedelta

from django.utils import timezone

from app.product.models import Rate, RateHistory, User


def save(rates, user_ids, freq):
    for user_id in user_ids:
        user_rates = list(filter(lambda rate: rate['assessed_user'] == user_id, rates))
        ln = len(user_rates)
        speed = 0
        quality = 0
        benevolence = 0
        for rate in user_rates:
            if rate['speed'] is None or rate['quality'] is None or rate['benevolence'] is None:
                ln = ln - 1
                continue
            speed = speed + rate['speed']
            quality = quality + rate['quality']
            benevolence = benevolence + rate['benevolence']

        if RateHistory.objects.filter(user_id=user_id, frequency=freq).exists():
            RateHistory.objects.filter(user_id=user_id, frequency=freq).update(speed=speed / ln, quality=quality / ln,
                                                                               benevolence=benevolence / ln)
        else:
            new_rate = RateHistory(user_id=user_id,
                                   frequency=freq,
                                   speed=speed / ln,
                                   quality=quality / ln,
                                   benevolence=benevolence / ln)
            new_rate.save()


def all_time():
    rates = [i.to_json() for i in list(Rate.objects.filter())]
    users = [i['assessed_user_id'] for i in Rate.objects.order_by().values('assessed_user_id').distinct()]
    save(rates, users, 'ALL')


def daily():
    rates = [i.to_json() for i in list(Rate.objects.filter(date__gte=timezone.now() - timedelta(days=1)))]
    users = [i['assessed_user_id'] for i in Rate.objects.order_by().values('assessed_user_id').distinct()]
    save(rates, users, 'DAY')
    all_time()


def weekly():
    rates = [i.to_json() for i in list(Rate.objects.filter(date__gte=timezone.now() - timedelta(days=7)))]
    users = [i['assessed_user_id'] for i in Rate.objects.order_by().values('assessed_user_id').distinct()]
    save(rates, users, 'WEEK')


def monthly():
    rates = [i.to_json() for i in list(Rate.objects.filter(date__gte=timezone.now() - timedelta(days=30)))]
    users = [i['assessed_user_id'] for i in Rate.objects.order_by().values('assessed_user_id').distinct()]
    save(rates, users, 'MONTH')


def clear_black_list():
    users = User.objects.all()
    for user in users:
        user.black_list = ""
        user.save()