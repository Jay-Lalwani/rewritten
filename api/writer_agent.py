"""
Writer Agent module for generating narrative content.
"""

import os
import random
import json

def generate_narrative(previous_narrative=None, decision_id=None, scenario=None):
    """
    Generate a narrative scene based on the previous narrative and decision.
    
    This is a placeholder implementation that simulates AI narrative generation.
    In a production environment, this would call to an actual AI model.
    
    Args:
        previous_narrative: The previous narrative data (if any)
        decision_id: The ID of the decision made by the player
        scenario: The name of the scenario (for initial narrative only)
        
    Returns:
        A dictionary containing the generated narrative data
    """
    # Placeholder implementation
    if not previous_narrative:
        # Initial narrative for a new game
        scene_id = 1
        if scenario == "Cuban Missile Crisis":
            narrative = "October 1962. The Cold War reaches its most dangerous moment. U.S. intelligence has discovered Soviet nuclear missiles in Cuba, just 90 miles from Florida. As President Kennedy's advisor, you must help navigate this crisis without triggering nuclear war."
            options = [
                {"id": "A", "option": "Recommend an immediate air strike to destroy the missile sites"},
                {"id": "B", "option": "Propose a naval blockade to prevent more weapons from reaching Cuba"},
                {"id": "C", "option": "Suggest diplomatic negotiations with the Soviet Union"}
            ]
        else:
            # Generic scenario for any other input
            narrative = f"You find yourself at a pivotal moment in the {scenario}. The decisions you make now will change the course of history."
            options = [
                {"id": "A", "option": "Take bold action to address the crisis directly"},
                {"id": "B", "option": "Pursue a moderate course seeking balance"},
                {"id": "C", "option": "Choose a diplomatic and cautious approach"}
            ]
    else:
        # Follow-up narrative based on previous decision
        scene_id = previous_narrative['scene_id'] + 1
        prev_narrative = previous_narrative['narrative']
        
        # Simple randomization for demonstration
        outcomes = [
            "Your decision leads to escalating tensions. Military forces are on high alert as the situation becomes more volatile.",
            "Initial responses to your approach are mixed. Some progress is visible, but new complications have emerged.",
            "Your strategy seems to be working. While challenges remain, there's cautious optimism about the path forward."
        ]
        
        narrative = random.choice(outcomes)
        options = [
            {"id": "A", "option": "Double down on your current strategy"},
            {"id": "B", "option": "Adjust your approach to address new developments"},
            {"id": "C", "option": "Change course completely in light of the situation"}
        ]
    
    return {
        "scene_id": scene_id,
        "narrative": narrative,
        "options": options
    } 