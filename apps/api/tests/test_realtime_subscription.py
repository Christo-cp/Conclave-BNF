from app.realtime.broker import EventSubscription


def test_empty_subscription_does_not_accept_everything():
    subscription = EventSubscription(set())
    assert subscription.channels == set()
