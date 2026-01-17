import json
import time
from collections import deque
from threading import Condition

# Buffer limité des derniers événements (pour les nouveaux clients)
_MAX_EVENTS = 1000
_events = deque(maxlen=_MAX_EVENTS)
_cond = Condition()

def publish(obj):
    """Publie un objet Python (sera sérialisé en JSON) à tous les clients SSE."""
    try:
        data = json.dumps(obj, default=str)
    except Exception:
        # Recours à la chaîne de caractères
        data = json.dumps({"raw": str(obj)})
    with _cond:
        _events.append(data)
        _cond.notify_all()
        try:
            print(f"realtime.publish: appended event (queue={len(_events)})")
        except Exception:
            pass

def stream(poll_timeout=15.0):
    """
    Générateur SSE : génère des événements au format SSE.
    - envoie un arriéré initial s'il existe,
    - envoie des messages de maintien de vie (commentaires) tous les poll_timeout s'il n'y a rien de neuf.
    """
    last_index = 0
    # Envoyer l'état initial (arriéré) s'il existe
    with _cond:
        backlog = list(_events)
    if backlog:
        for i, ev in enumerate(backlog):
            yield f"event: measurement\ndata: {ev}\n\n"
        last_index = len(backlog)

    while True:
        with _cond:
            # S'il y a des nouveaux événements, les consommer
            if last_index < len(_events):
                while last_index < len(_events):
                    ev = _events[last_index]
                    last_index += 1
                    yield f"event: measurement\ndata: {ev}\n\n"
                continue
            # Sinon, attendre une notification ou un timeout
            _cond.wait(timeout=poll_timeout)
            # Après wait, la boucle recommence et enverra de nouveaux événements s'ils sont présents
        # Maintien de vie pour éviter les timeouts des proxies
        yield ": ping\n\n"