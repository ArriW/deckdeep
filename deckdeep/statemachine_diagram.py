import graphviz
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from deckdeep.game import Game
from deckdeep.game_state import GameState, GameStateMachine
from deckdeep.logger import setup_game_logger

def create_state_diagram(game_state_machine: GameStateMachine):
    dot = graphviz.Digraph(comment='DeckDeep Game State Machine')
    dot.attr(rankdir='TB', size='16,20', dpi='300', fontsize='16', overlap='false', splines='ortho')

    # Define node styles
    dot.attr('node', shape='rectangle', style='filled', fontname='Arial', fontsize='14', width='2', height='1')

    state_info = game_state_machine.get_state_info()

    # Define the main states
    states = {state.name: 'lightgray' for state in GameState}
    states.update({
        'MAIN_MENU': 'lightblue',
        'NODE_SELECTION': 'lightgreen',
        'COMBAT': 'lightpink',
        'EVENT': 'lightyellow',
        'REST_SITE': 'lightcyan',
        'TREASURE_ROOM': 'gold',
        'VICTORY_SCREEN': 'palegreen',
        'GAME_OVER': 'lightcoral',
        'DECK_VIEW': 'lavender',
        'RELIC_VIEW': 'lavender'
    })

    # Add nodes
    for state, color in states.items():
        dot.node(state, fillcolor=color)

    # Add edges
    for from_state, transitions in state_info['transitions'].items():
        for transition in transitions:
            to_state = transition['to']
            label = transition['description']
            dot.edge(from_state, to_state, label=label)

    # Add initial state
    dot.node('START', shape='circle', fillcolor='black', style='filled', fontcolor='white', width='0.5')
    dot.edge('START', 'MAIN_MENU')

    # Save the diagram
    output_path = 'docs/state_machine_diagram'
    dot.render(output_path, format='png', cleanup=True)
    print(f"State machine diagram generated at {output_path}.png")

if __name__ == "__main__":
    # Setup a mock logger
    logger = setup_game_logger(name="deckdeep_logger", log_file="deckdeep.log")
    
    # Create a Game instance with mock screen and logger
    game = Game(None, logger)
    
    # Create the state diagram
    create_state_diagram(game.state_machine)
