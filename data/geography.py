"""US geography catalog for coherent addresses.

Faker generates city, state, and ZIP independently, which produces impossible
combinations (a Texas city with a California ZIP). This catalog holds real
city, state, and ZIP prefixes so the generators can emit addresses whose parts
agree. ZIP codes are completed with a plausible last two digits at generation
time; the leading three digits are anchored to the real locality.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Locality:
    city: str
    state: str          # USPS two-letter code
    zip_prefix: str     # first three digits of a real ZIP for the city
    timezone: str       # IANA timezone, useful for future temporal realism


# A geographically spread sample of US localities. Each ZIP prefix is a real
# leading-three-digit ZIP for that city.
LOCALITIES: list[Locality] = [
    Locality("New York", "NY", "100", "America/New_York"),
    Locality("Brooklyn", "NY", "112", "America/New_York"),
    Locality("Buffalo", "NY", "142", "America/New_York"),
    Locality("Boston", "MA", "021", "America/New_York"),
    Locality("Philadelphia", "PA", "191", "America/New_York"),
    Locality("Pittsburgh", "PA", "152", "America/New_York"),
    Locality("Baltimore", "MD", "212", "America/New_York"),
    Locality("Washington", "DC", "200", "America/New_York"),
    Locality("Richmond", "VA", "232", "America/New_York"),
    Locality("Charlotte", "NC", "282", "America/New_York"),
    Locality("Atlanta", "GA", "303", "America/New_York"),
    Locality("Miami", "FL", "331", "America/New_York"),
    Locality("Orlando", "FL", "328", "America/New_York"),
    Locality("Jacksonville", "FL", "322", "America/New_York"),
    Locality("Nashville", "TN", "372", "America/Chicago"),
    Locality("Memphis", "TN", "381", "America/Chicago"),
    Locality("Detroit", "MI", "482", "America/New_York"),
    Locality("Columbus", "OH", "432", "America/New_York"),
    Locality("Cleveland", "OH", "441", "America/New_York"),
    Locality("Indianapolis", "IN", "462", "America/New_York"),
    Locality("Chicago", "IL", "606", "America/Chicago"),
    Locality("Milwaukee", "WI", "532", "America/Chicago"),
    Locality("Minneapolis", "MN", "554", "America/Chicago"),
    Locality("St. Louis", "MO", "631", "America/Chicago"),
    Locality("Kansas City", "MO", "641", "America/Chicago"),
    Locality("New Orleans", "LA", "701", "America/Chicago"),
    Locality("Houston", "TX", "770", "America/Chicago"),
    Locality("Dallas", "TX", "752", "America/Chicago"),
    Locality("San Antonio", "TX", "782", "America/Chicago"),
    Locality("Austin", "TX", "787", "America/Chicago"),
    Locality("Oklahoma City", "OK", "731", "America/Chicago"),
    Locality("Denver", "CO", "802", "America/Denver"),
    Locality("Albuquerque", "NM", "871", "America/Denver"),
    Locality("Salt Lake City", "UT", "841", "America/Denver"),
    Locality("Phoenix", "AZ", "850", "America/Phoenix"),
    Locality("Tucson", "AZ", "857", "America/Phoenix"),
    Locality("Las Vegas", "NV", "891", "America/Los_Angeles"),
    Locality("Los Angeles", "CA", "900", "America/Los_Angeles"),
    Locality("San Diego", "CA", "921", "America/Los_Angeles"),
    Locality("San Francisco", "CA", "941", "America/Los_Angeles"),
    Locality("San Jose", "CA", "951", "America/Los_Angeles"),
    Locality("Sacramento", "CA", "958", "America/Los_Angeles"),
    Locality("Portland", "OR", "972", "America/Los_Angeles"),
    Locality("Seattle", "WA", "981", "America/Los_Angeles"),
    Locality("Spokane", "WA", "992", "America/Los_Angeles"),
]
