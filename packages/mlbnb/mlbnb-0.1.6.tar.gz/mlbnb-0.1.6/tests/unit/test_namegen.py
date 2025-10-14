from mlbnb.namegen import gen_run_name, ANIMALS, ADJECTIVES
from datetime import datetime


def test_generate_name() -> None:
    random_name = gen_run_name()

    datestr, timestr, adjective, animal = random_name.split("_")

    assert adjective in ADJECTIVES
    assert animal in ANIMALS

    # Assert that we can turn the YYYY-MM-DD into a datetime object
    datetime.strptime(datestr, "%Y-%m-%d")

    # Assert that we can turn the HH-MM into a datetime object
    datetime.strptime(timestr, "%H-%M")
