"""Centralized random-number and Faker utilities.

All generators call new_uuid() instead of uuid.uuid4() so that UUID generation
is driven by Python's seeded random module, making output fully reproducible
when seed_all(n) is called before generation.

Concurrency note
----------------
Python's global `random` module and the shared Faker instance carry process
wide state. When two seeded generations run at the same time (for example two
concurrent API requests that each pass a seed), their interleaved draws would
corrupt each other's deterministic sequence.

To keep seeded output reproducible under concurrency, all generation runs
through `generation_scope()`, which holds a process wide lock for the duration
of one generation. Generation is CPU bound and already serialized by the GIL,
so the throughput cost is negligible while determinism is guaranteed.
"""
import random
import threading
import uuid
from collections.abc import Iterator
from contextlib import contextmanager

from faker import Faker

# Single shared Faker instance, seeded via Faker.seed() in seed_all().
fake = Faker("en_US")

# Serializes generation so seeded runs cannot interleave their RNG draws.
_generation_lock = threading.RLock()


def seed_all(seed: int) -> None:
    """Seed Python's random, all Faker instances, and the UUID generator."""
    random.seed(seed)
    Faker.seed(seed)


@contextmanager
def generation_scope(seed: int | None = None) -> Iterator[None]:
    """Serialize one generation run and optionally seed it first.

    Use this around any block that produces resources so concurrent seeded
    runs stay reproducible:

        with generation_scope(seed):
            ...build resources...

    When a seed is given, the record-keeping clock is frozen for the duration so
    that timestamps are deterministic too and the output is byte-reproducible.
    """
    import clock

    with _generation_lock:
        token = None
        if seed is not None:
            seed_all(seed)
            token = clock.freeze(clock.today_midnight_utc())
        try:
            yield
        finally:
            if token is not None:
                clock.unfreeze(token)


def new_uuid() -> str:
    """UUID4 generated from Python's seeded random, reproducible with seed_all()."""
    return str(uuid.UUID(int=random.getrandbits(128), version=4))


def e164_phone() -> str:
    """US phone number in E.164 format (+1XXXXXXXXXX)."""
    digits = fake.numerify("##########")
    return f"+1{digits}"


def coherent_address() -> dict:
    """A US address whose city, state, and ZIP agree with a real locality.

    Faker draws city, state, and ZIP independently, which yields impossible
    combinations. This anchors all three to one real locality (see
    data/geography.py) and completes the ZIP with a plausible suffix.
    """
    from data.geography import LOCALITIES

    loc = random.choice(LOCALITIES)
    return {
        "address_line": fake.street_address(),
        "city": loc.city,
        "state": loc.state,
        "postal_code": loc.zip_prefix + fake.numerify("##"),
        "country": "US",
    }
