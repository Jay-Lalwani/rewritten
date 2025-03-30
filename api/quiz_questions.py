"""
Legacy quiz questions module - used as fallback if dynamic generation fails.

NOTE: This is retained for compatibility and fallback purposes.
The primary quiz functionality now uses quiz_agent.py for dynamic generation.
"""

import random

# Static fallback questions
QUIZ_QUESTIONS = [
    {
        "id": "q1",
        "question": "Which year did the Cuban Missile Crisis occur?",
        "options": [
            {"id": "a", "text": "1960"},
            {"id": "b", "text": "1962"},
            {"id": "c", "text": "1964"}
        ],
        "correct_option_id": "b",
        "explanation": "The Cuban Missile Crisis occurred in October 1962 when the Soviet Union placed nuclear missiles in Cuba."
    },
    {
        "id": "q2",
        "question": "Who was the U.S. President during the Cuban Missile Crisis?",
        "options": [
            {"id": "a", "text": "Dwight D. Eisenhower"},
            {"id": "b", "text": "John F. Kennedy"},
            {"id": "c", "text": "Lyndon B. Johnson"}
        ],
        "correct_option_id": "b",
        "explanation": "John F. Kennedy was the 35th President of the United States during the Cuban Missile Crisis."
    },
    {
        "id": "q3",
        "question": "Which leader represented the Soviet Union during the Cuban Missile Crisis?",
        "options": [
            {"id": "a", "text": "Joseph Stalin"},
            {"id": "b", "text": "Nikita Khrushchev"},
            {"id": "c", "text": "Leonid Brezhnev"}
        ],
        "correct_option_id": "b",
        "explanation": "Nikita Khrushchev was the Premier of the Soviet Union during the crisis."
    }
]

def get_random_question():
    """Return a random quiz question - legacy method for backward compatibility."""
    return random.choice(QUIZ_QUESTIONS) 