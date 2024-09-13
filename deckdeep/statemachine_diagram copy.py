from graphviz import Digraph
from .game_state import GameState, TransitionReason, GameStateMachine

def create_state_machine_diagram():
    dot = Digraph(comment='Game State Machine', format='png')
    dot.attr(rankdir='LR', size='40,30', dpi='300')
    dot.attr('node', shape='rectangle', style='rounded,filled', fillcolor='lightblue', fontname='Arial', fontsize='16')
    dot.attr('edge', fontname='Arial', fontsize='12')

    # Add nodes
    for state in GameState:
        dot.node(state.name, state.name)

    # Create a dummy Game instance
    class DummyGame:
        pass

    dummy_game = DummyGame()
    
    # Create GameStateMachine instance
    state_machine = GameStateMachine(dummy_game)

    # Add edges
    for from_state, transitions in state_machine.transition_map.items():
        for reason, to_state in transitions:
            dot.edge(from_state.name, to_state.name, label=reason.value)

    # Save the diagram
    dot.render('game_state_machine', cleanup=True)
    print("State machine diagram saved as 'game_state_machine.png'")

if __name__ == "__main__":
    create_state_machine_diagram()
