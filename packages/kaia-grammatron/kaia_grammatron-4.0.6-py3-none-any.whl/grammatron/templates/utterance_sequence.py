from typing import *
from .utterance import Utterance
from eaglesong.core.testing.scenario import IAsserter
from unittest import TestCase

class UtterancesSequence(IAsserter):
    def __init__(self, *utterances: Utterance|str):
        self.utterances = tuple(utterances)

    def __str__(self):
        return ' | '.join(str(u) for u in self.utterances)

    def __add__(self, other: Union[Utterance, 'UtterancesSequence', str]) -> 'UtterancesSequence':
        if isinstance(other, Utterance) or isinstance(other, str):
            return UtterancesSequence(*self.utterances, other)
        elif isinstance(other, UtterancesSequence):
            return UtterancesSequence(*self.utterances, *other.utterances)
        else:
            raise ValueError(f'Cannot add {other} to {self}')

    def assertion(self, actual, test_case: TestCase):
        test_case.assertIsInstance(actual, UtterancesSequence)
        test_case.assertEqual(len(self.utterances), len(actual.utterances))
        for e, a in zip(self.utterances, actual.utterances):
            if isinstance(e, str):
                test_case.assertEqual(e, a)
            else:
                e.assertion(a, test_case)