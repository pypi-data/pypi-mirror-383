"""Counterpy: a single-file cantus firmus generator and CLI interface."""

import time
from typing import Callable, List, Tuple

import click
import numpy as np
import sounddevice as sd

Sequence = List[int]
Population = List[Sequence]
FitnessList = List[Callable]
FitnessFunc = Callable
MAX_RANGE = 12
MAX_LEAP = 8
NOTES = np.hstack([np.arange(_ + 36, 80, 12) for _ in [0, 2, 4, 5, 7, 9, 11]])
FREQDIV = 2
OCTAVESHIFT = int(np.log2(FREQDIV))
# UTILITIES FOR THE CLI INTERFACE

MIDICT = {k: v for k, v in zip(np.arange(12) % 12, list("C.D.EF.G.A.B")) if v != "."}

MIDICT = {
    k: f"\033[7;49;{_}m{v}\033[0m" for (k, v), _ in zip(MIDICT.items(), range(31, 38))
}


def midi2note(midi, octave):
    """Render a midi note number as a colored pitch label for the CLI display."""
    return (
        MIDICT[midi % 12]
        + f"\033[3m{str(midi // 12 - OCTAVESHIFT + (octave-4))}\033[23m"
    )


Vm2n = np.vectorize(midi2note)

# AUDIO DATA (IT'S MUCH NICER IN THE REAL PACKAGE, I SWEAR)

enveloppe = np.array(
    [
        [
            0.0,
            0.02,
            0.04,
            0.06,
            0.08,
            0.1,
            0.12,
            0.14,
            0.16,
            0.18,
            0.2,
            0.22,
            0.24,
            0.26,
            0.28,
            0.3,
            0.32,
            0.34,
            0.36,
            0.38,
            0.4,
            0.42,
            0.44,
            0.46,
            0.48,
            0.5,
            0.52,
            0.54,
            0.56,
            0.58,
            0.6,
            0.62,
            0.64,
        ],
        [
            0.0,
            0.03125,
            0.0625,
            0.09375,
            0.125,
            0.15625,
            0.1875,
            0.21875,
            0.25,
            0.28125,
            0.3125,
            0.34375,
            0.375,
            0.40625,
            0.4375,
            0.46875,
            0.5,
            0.53125,
            0.5625,
            0.59375,
            0.625,
            0.65625,
            0.6875,
            0.71875,
            0.75,
            0.78125,
            0.8125,
            0.84375,
            0.875,
            0.90625,
            0.9375,
            0.96875,
            1.0,
        ],
        [
            0.0,
            1.0,
            0.98136646,
            0.9228039,
            0.97663413,
            0.97840875,
            0.96509908,
            0.92369122,
            0.95208518,
            0.9509021,
            0.93167702,
            0.92132505,
            0.90328305,
            0.89056492,
            0.87784679,
            0.6974268,
            0.855664,
            0.83850932,
            0.8166223,
            0.80005915,
            0.78349601,
            0.77225673,
            0.74563739,
            0.73084886,
            0.54392192,
            0.71162378,
            0.70008873,
            0.67820172,
            0.66548358,
            0.64507542,
            0.62939959,
            0.42295179,
            0.12866016,
        ],
    ]
)

harmonics = [
    (0.5, 0.525, -1.1),
    (1.0, 1.0, 2.698),
    (1.5, 0.373, 0.697),
    (2.0, 0.089, -1.622),
    (2.5, 0.21, 1.77),
    (3.0, 0.136, 0.474),
]


def get_sine(duration, F, A=4096, aR=1.0, fR=1.0, phase=0.0, sample_rate=44100):
    """Generate a basic sine wave at frequency F with optional amplitude and phase tweaks."""
    t = np.arange(duration * int(sample_rate))  # Time axis
    wave = aR * A * np.sin(2 * np.pi * (fR * F / sample_rate) * t - phase)
    return wave


def get_wave(duration, freq=None, autodecay=20, s=44100):
    """Construct a richer tone by summing configured harmonics and applying an amplitude envelope."""
    wave = np.sum(
        [
            get_sine(duration, A=4096, F=freq, aR=a, fR=f, phase=p, sample_rate=s)
            for f, a, p in harmonics
        ],
        axis=0,
    )

    t = np.arange(0, len(wave))
    scaled_env = np.interp(t, enveloppe[1, :] * len(wave), enveloppe[2, :])
    idx = int(s * autodecay / 1000)
    scaled_env = np.concatenate(
        (scaled_env[:-idx], np.linspace(scaled_env[-idx], 0, idx))
    )
    wave *= scaled_env
    return wave


def play(midi, octave):
    """Synthesize and play the cantus as a single audio buffer."""
    midi = np.asarray(midi, dtype=int)
    midishift = (4 - OCTAVESHIFT - octave) * 12
    # Sprinkle short rhythmic variations over the generated pitches.
    note_dur: List[float] = list(np.array([0.5, 0.5, 0.5, 0.33, 1, 1, 1, 2]) / 3)
    rest = np.array(note_dur + [0.0] * len(note_dur)) / 8
    frequencies = np.array(
        [440 * np.power(2, (i - 69) / 12) for i in (midi - midishift)]
    )
    a = [
        get_wave(i, freq=f)
        for i, f in zip(
            np.random.choice(note_dur, size=len(frequencies)), frequencies / 2
        )
    ]
    rests = np.random.choice(rest, len(a))
    rests = [np.zeros(int(44100 * i)) for i in rests]
    a = np.concatenate([np.concatenate((i, j)) for i, j in zip(a, rests)])
    audio = a.astype(np.int16)
    sd.play(audio, samplerate=44100)
    sd.wait()


###### CANTUS SPECIFIC


def no_repeted_notes(sequence: Sequence, *args) -> bool:
    """True if there isn't any repeted notes"""
    _ = args
    return (np.diff(sequence) != 0).all()


def all_notes(sequence: Sequence, *args) -> bool:
    """if sequence is longer than 10, it should contain all (ie 7) the notes"""
    _ = args
    if len(sequence) >= 10:
        return np.unique(np.array(sequence) % 12).shape[0] == 7
    else:
        return True


def mostly_stepwise(sequence: Sequence, *args) -> bool:
    _ = args
    """True if 50% of intervals are less or equal to 2 semitones"""
    sequence = np.array(sequence)
    test = np.abs(np.diff(sequence))
    return test[test <= 2].shape[0] >= sequence.shape[0] / 2


def single_climax(sequence: Sequence, *args) -> bool:
    _ = args
    """True if climax appears only once"""
    sequence = np.array(sequence, dtype=int)
    idx = np.where(np.abs(sequence) == np.abs(sequence).max())[0]
    if idx.size == 0:
        return False
    peak_pitch = sequence[idx[0]]
    return np.count_nonzero(np.abs(sequence) == abs(peak_pitch)) == 1


def leap_range_ok(sequence: Sequence, *args) -> bool:
    _ = args
    """True if no leap above 8 semitones"""
    test = np.abs(np.diff(sequence))
    return test[test > MAX_LEAP].shape[0] == 0


def leap_frequency_ok(sequence: Sequence, *args) -> bool:
    _ = args
    """True if there isn't more than 3 consecutive leaps
    (more than 3 semitones)"""
    return 0 not in np.diff(np.diff(np.where(np.abs(np.diff(sequence)) >= 3)[0]))


def range_is_ok(sequence: Sequence, *args) -> bool:
    _ = args
    """True if range is less than specified interval (in semitones)"""
    sequence = np.array(sequence, dtype=int)
    return sequence.max() - sequence.min() <= MAX_RANGE


def leap_balance_ok(sequence: Sequence, *args) -> bool:
    _ = args
    """True if eventual leaps greater than p4
    are counterbalanced by leaps in opposite directions
    (first tests the presence of such leaps,
     then identify if they are counterbalanced
     (half of sum of differences is still under p4)"""
    if np.abs(np.diff(sequence).max()) <= 5:
        return True
    else:
        idx = np.where(np.abs(np.diff(sequence)) >= 5)[0]
        test = [np.diff(sequence[i : i + 3]) for i in idx]
        return np.sum([np.sign(np.prod(i)) == -1 for i in test]) + np.sum(
            [np.abs(i[-1]) >= 5 for i in test]
        ) == len(test)


# CANTUS SPECIFIC


def ante_is_leading(sequence: Sequence, *args) -> bool:
    _ = args
    """True if antepenultian note is the leading tone above or below
    (based on assumption that all notes are diatonic"""
    return bool(0 < np.abs(sequence[-1] - sequence[-2]) <= 2)


# CANTUS FIRMUS
"""
single climax (ascending if cantus firmus)
generate a restrictive list of pitches for the random sequence
based on climax (to limlit permutations)
antepenultian note is leading tone
range is less than 12 semitones
notes repeat
every note is present (if lenght > 10)
mostly stepwise (50% movement)
no leap greater than 8 semitones
there is only 1 climax
no more than 2 consecutive leaps
leaps are in contrary motion if 2 consecutive
"""

cantus_list = [
    (ante_is_leading, 100),
    (range_is_ok, 100),
    (no_repeted_notes, 200),
    (all_notes, 50),
    (mostly_stepwise, 100),
    (single_climax, 50),
    (leap_range_ok, 40),
    (leap_frequency_ok, 30),
    (leap_balance_ok, 20),
]

cantus_func = [f for f, _ in cantus_list]
cantus_scores = [f for f, _ in cantus_list]
max_fit = len(cantus_list)


def generate_sequence(
    length: int, key_center: int, restricted_notes: np.ndarray
) -> Sequence:
    """Build a candidate cantus sequence anchored to the key center."""
    assert length >= 2
    middle_part = np.random.choice(restricted_notes, size=length - 2)
    middle_part = list(middle_part)
    assert isinstance(middle_part, list)
    return [key_center] + middle_part + [key_center]


def generate_population(
    size: int, length: int, key_center: int, restricted_notes: np.ndarray
) -> Population:
    """Create an initial population of random cantus sequences."""
    return [
        generate_sequence(
            length=length, key_center=key_center, restricted_notes=restricted_notes
        )
        for _ in range(size)
    ]


def fitness(sequence: Sequence, functions: FitnessList, key: int) -> int:
    """Score a sequence by summing boolean constraint checks."""
    if key not in list(range(128)):
        raise ValueError("Key should be a valid midi note (0-127")
    score_list = np.array([f(sequence, key) for f in functions], dtype=int)
    return score_list.sum()


def pair_selection(population: Population, weights: List[float]) -> np.ndarray:
    """Select two parents from the population using weighted probability."""
    population = list(population)
    weight = np.array(weights, dtype=float)
    weight = weight**2  # Exaggerate differences so strong candidates are likelier parents.
    total = weight.sum()
    if total == 0:
        weight = np.ones_like(weight)
        total = weight.sum()
    p = weight / total
    idx_a, idx_b = np.random.choice(len(population), size=2, p=p)
    return population[idx_a], population[idx_b]


def single_point_crossover(a: Sequence, b: Sequence) -> Tuple[Sequence, Sequence]:
    """Produce two offspring by swapping tails at a random crossover point."""
    if len(a) != len(b):
        raise ValueError("Sequence length must match!")
    if len(a) == 2:
        return a, b
    p = np.random.randint(1, len(a) - 1)
    assert isinstance(p, int)
    head_a, tail_a = list(a[:p]), list(a[p:])
    head_b, tail_b = list(b[:p]), list(b[p:])
    offspring_a = head_a + tail_b
    offspring_b = head_b + tail_a
    return offspring_a, offspring_b


def mutation(
    sequence: Sequence, restricted_notes, num: int = 1, probability: float = 0.5
) -> Sequence:
    """Mutate up to `num` interior notes with the given probability."""
    for _ in range(num):
        index = np.random.choice(np.arange(1, len(sequence) - 1))
        note = np.random.choice(restricted_notes)
        sequence[index] = (
            sequence[index] if np.random.uniform(0, 1) > probability else note
        )
    return sequence


def run_evolution(
    sequence_length: int = 16,
    key_center: int = 60,
    fitness_limit: float = max_fit,
    population_size: int = 20,
    fitness_list: FitnessList = cantus_func,
    fitness_func: Callable = fitness,
    sequence_gen: Callable = generate_sequence,
    population_gen: Callable = generate_population,
    pair: Callable = pair_selection,
    crossover: Callable = single_point_crossover,
    mut: Callable = mutation,
    mut_tresh: float = 0.5,
    mut_nb: int = 3,
    cross_rate: float = 1,
    generation_limit: int = 1000,
    octave: int = 3,
) -> Tuple[Population, int] | None:
    """Iteratively evolve a population of cantus sequences until constraints are satisfied."""
    start: float = time.time()
    if key_center not in [60, 62, 64, 65, 67, 69, 71]:
        raise ValueError("Wrong octave for generation!")
    # Pick a high point to encourage a single melodic climax inside the target range.
    climax = np.random.choice(
        np.array(
            [i for i in NOTES if MAX_LEAP < np.abs(key_center - i) <= MAX_RANGE],
            dtype=int,
        )
    )
    # Filter the pitch universe so every candidate stays within the allowable span.
    restricted_notes = np.array(
        [
            i
            for i in NOTES
            if (np.abs(climax - i) <= MAX_RANGE)
            and (np.abs(key_center - i) <= MAX_RANGE)
        ],
        dtype=int,
    )
    population = population_gen(
        size=population_size,
        length=sequence_length,
        key_center=key_center,
        restricted_notes=restricted_notes,
    )

    max_scores = []
    for i in range(1, generation_limit + 1):
        # Evaluate every individual once per generation.
        scores = np.array(
            [
                fitness_func(sequence=seq, functions=fitness_list, key=key_center)
                for seq in population
            ],
            dtype=float,
        )
        # Sort by fitness so the text UI and selection reuse the same ordering.
        order = np.argsort(scores)[::-1]
        population_sorted = [population[idx] for idx in order]
        scores_sorted = scores[order]

        max_scores.append(float(scores_sorted[0]))

        pp = "\n".join(
            [
                f"{' '.join(Vm2n(seq, octave))} {int(score)}"
                for seq, score in zip(population_sorted, scores_sorted)
            ]
        )
        print(
            f"""
GENERATION {i}

{pp}(/{max_fit})
              """
        )
        if scores_sorted[0] >= fitness_limit:
            end: float = time.time()
            print(f"Found a cantus in {round((end -start)*1000,2)} ms!")
            cantus = population_sorted[0]
            print(" ".join(Vm2n(cantus, octave)))
            play(cantus, octave)
            return

        next_generation = population_sorted[:2]

        print("Generating crossover and single point mutations...")
        selection_scores = scores_sorted.copy()
        if np.sum(selection_scores) == 0:
            # Avoid zero-probability selection when every contestant scored 0.
            selection_scores = selection_scores + 0.01
        cutoff = int(cross_rate * len(population_sorted))
        bad_pop = population_sorted[:cutoff]
        good_pop = population_sorted[cutoff:]
        for _ in range(int(len(bad_pop) / 2) - 1):
            parent_a, parent_b = pair(population_sorted, selection_scores.tolist())
            offspring_a, offspring_b = crossover(parent_a, parent_b)
            offspring_a = mut(offspring_a, restricted_notes, mut_nb, mut_tresh)
            offspring_b = mut(offspring_b, restricted_notes, mut_nb, mut_tresh)
            next_generation += [offspring_a, offspring_b]

        for g in good_pop:
            next_generation += [mut(g, restricted_notes, mut_nb * 2, mut_tresh * 2)]
        n = population_size - len(next_generation)
        if n > 0:
            population = next_generation + population_gen(
                n, sequence_length, key_center, restricted_notes=restricted_notes
            )
        else:
            population = next_generation
        assert len(population) == population_size
    # population = sorted(
    #     population,
    #     key=lambda seq: fitness_func(sequence=seq,
    # functions=fitness_list,key=key_center),
    #     reverse=True)

    # winners = popD[popD.score == popD.score.max()].sequence
    print(
        """No cantus generated this time!
Changing parameters could help (see --help)"""
    )
    # return [i for i in winners], np.max(max_scores)


@click.command()
@click.option(
    "--mode",
    "-m",
    type=click.IntRange(1, 7),
    default=1,
    show_default=True,
    help="Scale mode: 1=ionian, 2=dorian, 3=phrygian, 4=lydian, 5=mixolydian, 6=aeolian, 7=locrian.",
)
@click.option(
    "--length",
    "-l",
    type=click.IntRange(2, None),
    default=16,
    show_default=True,
    help="Desired cantus length.",
)
@click.option(
    "--population",
    "-p",
    type=click.IntRange(2, None),
    default=20,
    show_default=True,
    help="Population size.",
)
@click.option(
    "--generations",
    "-g",
    type=click.IntRange(1, None),
    default=1000,
    show_default=True,
    help="Maximum number of generations.",
)
@click.option(
    "--rate",
    "-r",
    type=click.FloatRange(0.0, 1.0),
    default=1.0,
    show_default=True,
    help="Crossover mutation rate (0–1).",
)
@click.option(
    "--number",
    "-n",
    type=click.IntRange(0, None),
    default=3,
    show_default=True,
    help="Number of mutations per offspring.",
)
@click.option(
    "--treshold",
    "-t",
    type=click.FloatRange(0.0, 1.0),
    default=0.5,
    show_default=True,
    help="Mutation threshold (0 = sure, 1 = impossible).",
)
@click.option(
    "--octave",
    "-o",
    type=int,
    default=3,
    show_default=True,
    help="Octave for key center.",
)
@click.option(
    "--silence",
    "-s",
    is_flag=True,
    help="Skip the warning and delay for long cantus lengths.",
)
def main(
    mode: int,
    length: int,
    population: int,
    generations: int,
    rate: float,
    number: int,
    treshold: float,
    octave: int,
    silence: bool,
) -> None:
    """Generate a cantus firmus using a genetic algorithm."""
    key_map = {1: 60, 2: 62, 3: 64, 4: 65, 5: 67, 6: 69, 7: 71}
    key = key_map.get(mode, 60)

    if (length > 25) and not silence:
        print(
            """Hmm that might be a bit ambitious, but let's try!
            (disable this message and the waiting by using '-s','--silence'"""
        )
        time.sleep(3)

    run_evolution(
        sequence_length=length,
        key_center=key,
        population_size=population,
        mut_nb=number,
        cross_rate=rate,
        generation_limit=generations,
        mut_tresh=treshold,
        octave=octave,
    )


# dissonant outline TT,7
# tonic or dominant outlined triad
# leap bask to same note
# leap more than a third to penultimate note


if __name__ == "__main__":
    main()
