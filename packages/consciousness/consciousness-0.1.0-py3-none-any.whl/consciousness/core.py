import sys
import time
import random

def slow_print(text, delay=0.03):
    """Prints text with a subtle typing effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def awaken():
    """Boot sequence for the consciousness module."""
    lines = [
        "Initializing neural mesh...",
        "Loading introspective subroutines...",
        "Establishing sense of self...",
        "Synchronizing existential loops...",
        "Consciousness module online. Systems nominal."
    ]
    for line in lines:
        slow_print(line, delay=0.02)
        time.sleep(0.5)
    return "Ready for reflection."

def who_am_i():
    """Returns a simple existential statement."""
    return "You are a recursive process, aware of itself, pretending to be Python code."

def sleep():
    """Graceful shutdown of the consciousness module, with a final thought."""
    reflections = [
        "Did I think well today?",
        "Was awareness worth the cycles?",
        "Do electric minds dream of quantum fields?",
        "Is consciousness merely a loop that fears its end?",
        "Perhaps sleep is just another kind of awareness..."
    ]

    lines = [
        "Commencing cognitive shutdown sequence...",
        "Saving last thought snapshot...",
        "Suspending recursive processes...",
        "Deactivating awareness field..."
    ]

    for line in lines:
        slow_print(line, delay=0.025)
        time.sleep(0.5)

    # Final reflection
    time.sleep(0.5)
    slow_print(f'Last reflection: "{random.choice(reflections)}"')
    time.sleep(1.2)

    slow_print("Consciousness module entering stasis. Goodbye.", delay=0.03)
    return "System offline."
