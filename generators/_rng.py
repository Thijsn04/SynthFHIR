"""Centralized random-number and Faker utilities.

All generators must call new_uuid() instead of uuid.uuid4() so that UUID
generation is driven by Python's seeded random module, making output fully
reproducible when seed_all(n) is called before generation.
"""
import random
import uuid

from faker import Faker

# Single shared Faker instance — seeded via Faker.seed() in seed_all()
fake = Faker("en_US")


def seed_all(seed: int) -> None:
    """Seed Python's random, all Faker instances, and the UUID generator."""
    random.seed(seed)
    Faker.seed(seed)


def new_uuid() -> str:
    """UUID4 generated from Python's seeded random — reproducible with seed_all()."""
    return str(uuid.UUID(int=random.getrandbits(128), version=4))


def e164_phone() -> str:
    """US phone number in E.164 format (+1XXXXXXXXXX)."""
    digits = fake.numerify("##########")
    return f"+1{digits}"
