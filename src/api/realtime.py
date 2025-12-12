import json
import time
from collections import deque
from threading import Condition

# buffer limité des derniers événements (pour nouveaux clients)
_MAX_EVENTS = 1000
_events = deque(maxlen=_MAX_EVENTS)
_cond = Condition()

def publish(obj):
    """Publie un objet Python (sera jsonifié) à tous les clients SSE."""
    try:
        data = json.dumps(obj, default=str)
    except Exception:
        # fallback to string
        data = json.dumps({"raw": str(obj)})
    with _cond:
        _events.append(data)
        _cond.notify_all()

def stream(poll_timeout=15.0):
    """
    Générateur SSE : yield des événements au format SSE.
    - envoie un dernier backlog si existant,
    - envoie des keepalive (comment) toutes les poll_timeout si rien de neuf.
    """
    last_index = 0
    # send initial state (backlog) if any
    with _cond:
        backlog = list(_events)
    if backlog:
        for i, ev in enumerate(backlog):
            yield f"event: measurement\ndata: {ev}\n\n"
        last_index = len(backlog)

    while True:
        with _cond:
            # si y'a des événements nouveaux, consomme-les
            if last_index < len(_events):
                while last_index < len(_events):
                    ev = _events[last_index]
                    last_index += 1
                    yield f"event: measurement\ndata: {ev}\n\n"
                continue
            # sinon attend notification ou timeout
            _cond.wait(timeout=poll_timeout)
            # après wait, loop repars et enverra de nouveaux events si présents
        # keepalive pour éviter timeouts proxies
        yield ": ping\n\n"