"""Disjoncteur déterministe, horloge simulée ; ne mesure pas des timeouts réseau."""
from dataclasses import dataclass
from .common import check


@dataclass
class Breaker:
    failures: int = 0
    open_until: float = 0
    calls: int = 0

    def call(self, now, dependency):
        if now < self.open_until:
            return "degrade"
        self.calls += 1
        try:
            value = dependency()
        except TimeoutError:
            self.failures += 1
            if self.failures >= 3:
                self.open_until = now + 5
            return "degrade"
        self.failures = 0
        self.open_until = 0
        return value


def run():
    breaker = Breaker()

    def unavailable():
        raise TimeoutError("Dépendance indisponible")

    outcomes = [breaker.call(i / 100, unavailable) for i in range(100)]
    calls_during_outage = breaker.calls
    recovery = breaker.call(6, lambda: "ok")
    check(calls_during_outage == 3 and set(outcomes) == {"degrade"} and recovery == "ok",
          "Le circuit doit protéger la dépendance puis se refermer")
    return {"appels_naifs": 100, "appels_avec_circuit": calls_during_outage,
            "reprise_apres_delai": recovery}
