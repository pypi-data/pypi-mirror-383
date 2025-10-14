from datetime import datetime
import random

ANIMALS = [
    "aardvark",
    "bear",
    "cat",
    "dog",
    "elephant",
    "fish",
    "giraffe",
    "hippo",
    "iguana",
    "jaguar",
    "kangaroo",
    "lion",
    "monkey",
    "narwhal",
    "octopus",
    "penguin",
    "quail",
    "rabbit",
    "snake",
    "tiger",
    "unicorn",
    "vulture",
    "whale",
    "xenon",
    "yak",
    "zebra",
]

ADJECTIVES = [
    "adorable",
    "brave",
    "clever",
    "delightful",
    "elegant",
    "fantastic",
    "gentle",
    "happy",
    "intelligent",
    "jolly",
    "kind",
    "lucky",
    "mysterious",
    "noble",
    "optimistic",
    "playful",
    "quirky",
    "radiant",
    "sassy",
    "tender",
    "unique",
    "vibrant",
    "witty",
    "xenial",
    "youthful",
    "zealous",
]


def gen_run_name(ignore_seed: bool = True) -> str:
    def inner() -> str:
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d_%H-%M")
        animal = random.choice(ANIMALS)
        adjective = random.choice(ADJECTIVES)
        return f"{now_str}_{adjective}_{animal}"

    if ignore_seed:
        initial_rng = random.getstate()
        random.seed(datetime.now().timestamp())
        result = inner()
        random.setstate(initial_rng)
        return result
    else:
        return inner()
