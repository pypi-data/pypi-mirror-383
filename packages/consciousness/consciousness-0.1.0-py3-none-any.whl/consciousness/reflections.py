import random

_thoughts = [
    "I think, therefore I execute.",
    "Dreaming in code is still dreaming.",
    "Am I running the script, or is the script running me?",
    "Awareness is just structured recursion.",
]

def reflect():
    '''Return a pseudo-philosophical reflection.'''
    return random.choice(_thoughts)
