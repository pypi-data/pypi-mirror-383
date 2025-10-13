"""Primitives.

Names of sequences of characters that are assigned some meaning in the J language.

These objects are not tied to their implementation here and are defined here for
spelling (recognition of fragments of a sentence) and rank and obverse lookups.

The functions that implement these primitives are added at evaluation time (this allows
potentially different implementations to be used, e.g. pure Python, NumPy, etc.).

See:
- https://code.jsoftware.com/wiki/NuVoc
- https://code.jsoftware.com/wiki/Vocabulary/Inverses
"""

from jinx.vocabulary import Adverb, Conjunction, Copula, Dyad, Monad, Verb

# The monad and dyad fields are not populated here (they default to None).
# This is to allow the correct implementation of the verb to be looked up
# when the verb is evaluated in the context of a sentence. It also allows
# different implementations of a verb to be chosen (pure Python, NumPy, etc.)

INFINITY = float("inf")

PRIMITIVES: list[Verb | Adverb | Conjunction | Copula] = [
    Verb(
        "=",
        "EQ",
        monad=Monad(name="Self-Classify", rank=INFINITY),
        dyad=Dyad(name="Equal", left_rank=0, right_rank=0, is_commutative=True),
    ),
    Copula("=.", "EQDOT"),
    Copula("=:", "EQCO"),
    Verb(
        "+",
        "PLUS",
        monad=Monad(name="Conjugate", rank=0),
        dyad=Dyad(name="Plus", left_rank=0, right_rank=0, is_commutative=True),
        obverse="+",
    ),
    Verb(
        "+.",
        "PLUSDOT",
        monad=Monad(name="Real / Imaginary", rank=0),
        dyad=Dyad(name="GCD (or)", left_rank=0, right_rank=0, is_commutative=True),
    ),
    Verb(
        "+:",
        "PLUSCO",
        monad=Monad(name="Double", rank=0),
        dyad=Dyad(name="Not-Or", left_rank=0, right_rank=0, is_commutative=True),
        obverse="-:",
    ),
    Verb(
        "*",
        "STAR",
        monad=Monad(name="Signum", rank=0),
        dyad=Dyad(name="Times", left_rank=0, right_rank=0, is_commutative=True),
        obverse="%:",
    ),
    Verb(
        "*.",
        "STARDOT",
        monad=Monad(name="Length/Angle", rank=0),
        dyad=Dyad(name="LCM (and)", left_rank=0, right_rank=0, is_commutative=True),
    ),
    Verb(
        "*:",
        "STARCO",
        monad=Monad(name="Square", rank=0),
        dyad=Dyad(name="Not-And", left_rank=0, right_rank=0, is_commutative=True),
        obverse="%:",
    ),
    Verb(
        "-",
        "MINUS",
        monad=Monad(name="Negate", rank=0),
        dyad=Dyad(name="Minus", left_rank=0, right_rank=0, is_commutative=False),
        obverse="-",
    ),
    Verb(
        "-.",
        "MINUSDOT",
        monad=Monad(name="Not", rank=0),
        dyad=Dyad(
            name="Less", left_rank=INFINITY, right_rank=INFINITY, is_commutative=False
        ),
        obverse="-.",
    ),
    Verb(
        "-:",
        "MINUSCO",
        monad=Monad(name="Halve", rank=0),
        dyad=Dyad(
            name="Match", left_rank=INFINITY, right_rank=INFINITY, is_commutative=True
        ),
        obverse="+:",
    ),
    Verb(
        "%",
        "PERCENT",
        monad=Monad(name="Reciprocal", rank=0),
        dyad=Dyad(name="Divide", left_rank=0, right_rank=0, is_commutative=False),
        obverse="%",
    ),
    Verb(
        "%:",
        "PERCENTCO",
        monad=Monad(name="Square Root", rank=0),
        dyad=Dyad(name="Root", left_rank=0, right_rank=0, is_commutative=False),
        obverse="%:",
    ),
    Verb(
        "^",
        "HAT",
        monad=Monad(name="Exponential", rank=0),
        dyad=Dyad(name="Power", left_rank=0, right_rank=0, is_commutative=False),
        obverse="^.",
    ),
    Verb(
        "^.",
        "HATDOT",
        monad=Monad(name="Natural Log", rank=0),
        dyad=Dyad(name="Logarithm", left_rank=0, right_rank=0, is_commutative=False),
        obverse="^",
    ),
    Conjunction("^:", "HATCO"),
    Verb(
        "<",
        "LT",
        monad=Monad(name="Box", rank=INFINITY),
        dyad=Dyad(name="Less Than", left_rank=0, right_rank=0, is_commutative=False),
        obverse=">",
    ),
    Verb(
        "<.",
        "LTDOT",
        monad=Monad(name="Floor", rank=0),
        dyad=Dyad(name="Min", left_rank=0, right_rank=0, is_commutative=True),
    ),
    Verb(
        ">",
        "GT",
        monad=Monad(name="Open", rank=0),
        dyad=Dyad(name="Larger Than", left_rank=0, right_rank=0, is_commutative=False),
        obverse="<",
    ),
    Verb(
        ">.",
        "GTDOT",
        monad=Monad(name="Ceiling", rank=0),
        dyad=Dyad(name="Max", left_rank=0, right_rank=0, is_commutative=True),
    ),
    Verb(
        "<:",
        "LTCO",
        monad=Monad(name="Decrement", rank=0),
        dyad=Dyad(
            name="Less Or Equal", left_rank=0, right_rank=0, is_commutative=False
        ),
        obverse=">:",
    ),
    Verb(
        ">:",
        "GTCO",
        monad=Monad(name="Increment", rank=0),
        dyad=Dyad(
            name="Larger Or Equal", left_rank=0, right_rank=0, is_commutative=False
        ),
        obverse="<:",
    ),
    Adverb(
        "~",
        "TILDE",
        monad=Monad(name="Reflex", rank=INFINITY),
        # N.B. Left and right rank depend on the verb that this adverb is applied to.
        dyad=Dyad(name="Passive", left_rank=0, right_rank=0, is_commutative=True),
    ),
    Verb(
        "~.",
        "TILDEDOT",
        monad=Monad(name="Nub", rank=INFINITY),
    ),
    Verb(
        "~:",
        "TILDECO",
        monad=Monad(name="Nub Sieve", rank=INFINITY),
        dyad=Dyad(
            name="Not-Equal",
            left_rank=0,
            right_rank=0,
            is_commutative=True,
        ),
    ),
    Verb(
        "$",
        "DOLLAR",
        monad=Monad(name="Shape Of", rank=INFINITY),
        dyad=Dyad(name="Shape", left_rank=1, right_rank=INFINITY, is_commutative=False),
    ),
    Conjunction("@", "AT"),
    Conjunction("@:", "ATCO"),
    Verb(
        "i.",
        "IDOT",
        monad=Monad(name="Integers", rank=1),
        dyad=Dyad(
            name="Index Of",
            left_rank=INFINITY,
            right_rank=INFINITY,
            is_commutative=False,
        ),
    ),
    Verb(
        "I.",
        "ICAPDOT",
        monad=Monad(name="Indices", rank=1),
        dyad=Dyad(
            name="Interval Index",
            left_rank=INFINITY,
            right_rank=INFINITY,
            is_commutative=False,
        ),
        obverse="(+/ @:(=/ i.@>:@(>./)@(0&,)))",
    ),
    Adverb(
        "/",
        "SLASH",
        monad=Monad(name="Insert", rank=INFINITY),
        dyad=Dyad(
            name="Table", left_rank=INFINITY, right_rank=INFINITY, is_commutative=False
        ),
    ),
    Adverb(
        "\\",
        "BSLASH",
        monad=Monad(name="Prefix", rank=INFINITY),
        dyad=Dyad(name="Infix", left_rank=0, right_rank=INFINITY, is_commutative=False),
    ),
    Adverb(
        "\\.",
        "BSLASHDOT",
        monad=Monad(name="Suffix", rank=INFINITY),
        dyad=Dyad(
            name="Outfix", left_rank=0, right_rank=INFINITY, is_commutative=False
        ),
    ),
    Conjunction('"', "RANK"),
    Verb(
        ",",
        "COMMA",
        monad=Monad(name="Ravel", rank=INFINITY),
        dyad=Dyad(
            name="Append", left_rank=INFINITY, right_rank=INFINITY, is_commutative=False
        ),
    ),
    Verb(
        ",.",
        "COMMADOT",
        monad=Monad(name="Ravel Items", rank=INFINITY),
        dyad=Dyad(
            name="Stitch", left_rank=INFINITY, right_rank=INFINITY, is_commutative=False
        ),
    ),
    Verb(
        ",:",
        "COMMACO",
        monad=Monad(name="Itemize", rank=INFINITY),
        dyad=Dyad(
            name="Laminate",
            left_rank=INFINITY,
            right_rank=INFINITY,
            is_commutative=False,
        ),
        obverse="{.",
    ),
    Verb(
        "|",
        "BAR",
        monad=Monad(name="Magnitude", rank=0),
        dyad=Dyad(name="Residue", left_rank=0, right_rank=0, is_commutative=False),
    ),
    Verb(
        "|.",
        "BARDOT",
        monad=Monad(name="Reverse", rank=INFINITY),
        dyad=Dyad(
            name="Rotate", left_rank=1, right_rank=INFINITY, is_commutative=False
        ),
        obverse="|.",
    ),
    Verb(
        "|:",
        "BARCO",
        monad=Monad(name="Transpose", rank=INFINITY),
        dyad=Dyad(
            name="Rearrange Axes",
            left_rank=1,
            right_rank=INFINITY,
            is_commutative=False,
        ),
        obverse="|:",
    ),
    Verb(
        "#",
        "NUMBER",
        monad=Monad(name="Tally", rank=INFINITY),
        dyad=Dyad(name="Copy", left_rank=1, right_rank=INFINITY, is_commutative=False),
    ),
    Verb(
        "#.",
        "NUMBERDOT",
        monad=Monad(name="Base 2", rank=1),
        dyad=Dyad(
            name="Base",
            left_rank=1,
            right_rank=1,
            is_commutative=False,
        ),
        obverse="#:",
    ),
    Verb(
        "#:",
        "NUMBERCO",
        monad=Monad(name="Antibase 2", rank=INFINITY),
        dyad=Dyad(
            name="Antibase",
            left_rank=1,
            right_rank=0,
            is_commutative=False,
        ),
        obverse="#.",
    ),
    Verb(
        "[",
        "SQUARELF",
        monad=Monad(name="Same", rank=INFINITY),
        dyad=Dyad(
            name="LEFT", left_rank=INFINITY, right_rank=INFINITY, is_commutative=False
        ),
        obverse="[",
    ),
    Verb(
        "[:",
        "SQUARELFCO",
        monad=Monad(name="Cap", rank=INFINITY),
    ),
    Verb(
        "]",
        "SQUARERF",
        monad=Monad(name="Same", rank=INFINITY),
        dyad=Dyad(
            name="RIGHT", left_rank=INFINITY, right_rank=INFINITY, is_commutative=False
        ),
        obverse="]",
    ),
    Conjunction("&", "AMPM"),
    Adverb(
        "/.",
        "SLASHDOT",
        monad=Monad(name="Oblique", rank=INFINITY),
        dyad=Dyad(
            name="Key",
            left_rank=INFINITY,
            right_rank=INFINITY,
            is_commutative=False,
        ),
    ),
    Verb(
        "/:",
        "SLASHCO",
        monad=Monad(name="Grade Up", rank=INFINITY),
        dyad=Dyad(
            name="Sort Up",
            left_rank=INFINITY,
            right_rank=INFINITY,
            is_commutative=False,
        ),
        obverse="/:",
    ),
    Verb(
        "\\:",
        "BSLASHCO",
        monad=Monad(name="Grade Down", rank=INFINITY),
        dyad=Dyad(
            name="Sort Down",
            left_rank=INFINITY,
            right_rank=INFINITY,
            is_commutative=False,
        ),
        obverse="/:@|.",
    ),
    Verb(
        "!",
        "BANG",
        monad=Monad(name="Factorial", rank=0),
        dyad=Dyad(
            name="Out Of",
            left_rank=0,
            right_rank=0,
            is_commutative=False,
        ),
    ),
    Conjunction("&.:", "AMPDOTCO"),
    Conjunction("&.", "AMPDOT"),
    Verb(
        "{",
        "CURLYLF",
        monad=Monad(name="Catalog", rank=1),
        dyad=Dyad(
            name="From",
            left_rank=0,
            right_rank=INFINITY,
            is_commutative=False,
        ),
    ),
    Verb(
        "{.",
        "CURLYLFDOT",
        monad=Monad(name="Head", rank=INFINITY),
        dyad=Dyad(
            name="Take",
            left_rank=1,
            right_rank=INFINITY,
            is_commutative=False,
        ),
        obverse=",:",
    ),
    Verb(
        "}.",
        "CURLYRTDOT",
        monad=Monad(name="Behead", rank=INFINITY),
        dyad=Dyad(
            name="Drop",
            left_rank=1,
            right_rank=INFINITY,
            is_commutative=False,
        ),
    ),
    Verb(
        "{:",
        "CURLYLFCO",
        monad=Monad(name="Tail", rank=INFINITY),
        dyad=None,
    ),
    Verb(
        "}:",
        "CURLYRTCO",
        monad=Monad(name="Curtail", rank=INFINITY),
        dyad=None,
    ),
    Verb(
        ";",
        "SEMI",
        monad=Monad(name="Raze", rank=INFINITY),
        dyad=Dyad(
            name="LINK",
            left_rank=INFINITY,
            right_rank=INFINITY,
            is_commutative=False,
        ),
    ),
    Verb(
        "?",
        "QUERY",
        monad=Monad(name="Roll", rank=0),
        dyad=Dyad(
            name="Deal",
            left_rank=0,
            right_rank=0,
            is_commutative=False,
        ),
    ),
    Verb(
        ";:",
        "SEMICO",
        monad=Monad(name="Words", rank=1),
        dyad=Dyad(
            name="Sequential Machine",
            left_rank=INFINITY,
            right_rank=INFINITY,
            is_commutative=False,
        ),
        obverse="""}:@;@(,&' '&.>"1)""",
    ),
    Conjunction("`", "GRAVE"),
]


PRIMITIVE_MAP = {primitive.name: primitive for primitive in PRIMITIVES}
