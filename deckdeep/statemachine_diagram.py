from graphviz import Digraph
from .game_state import GameState, TransitionReason, GameStateMachine

def create_state_machine_diagram():
    dot = Digraph(comment='Game State Machine', format='png')
    dot.attr(rankdir='TB', size='40,60', dpi='300', overlap='false', splines='ortho')
    dot.attr('node', shape='rectangle', style='rounded,filled', fontname='Arial', fontsize='14', height='0.6', width='2.5')
    dot.attr('edge', fontname='Arial', fontsize='10', len='2')

    # Color scheme
    colors = {
        'menu': '#FFB3BA',  # Light pink
        'combat': '#BAFFC9',  # Light green
        'exploration': '#BAE1FF',  # Light blue
        'other': '#FFFFBA',  # Light yellow
    }

    # Group and color-code states
    with dot.subgraph(name='cluster_menu') as c:
        c.attr(label='Menu States', style='filled', color=colors['menu'])
        c.node('MAIN_MENU')
        c.node('DECK_VIEW')
        c.node('RELIC_VIEW')
        c.node('CARD_SELECT')

    with dot.subgraph(name='cluster_combat') as c:
        c.attr(label='Combat States', style='filled', color=colors['combat'])
        c.node('COMBAT_START')
        c.node('COMBAT_PLAYER_TURN')
        c.node('COMBAT_MONSTER_TURN')
        c.node('COMBAT_END')

    with dot.subgraph(name='cluster_exploration') as c:
        c.attr(label='Exploration States', style='filled', color=colors['exploration'])
        c.node('NODE_SELECTION')
        c.node('EVENT')
        c.node('REST_SITE')
        c.node('TREASURE_ROOM')

    # Other states
    dot.node('VICTORY_SCREEN', fillcolor=colors['other'])
    dot.node('GAME_OVER', fillcolor=colors['other'])

    # Create a dummy Game instance and GameStateMachine
    class DummyGame:
        pass
    state_machine = GameStateMachine(DummyGame())

    # Add edges
    for from_state, transitions in state_machine.transition_map.items():
        for reason, to_state in transitions:
            dot.edge(from_state.name, to_state.name, label=reason.value)

    # Add a simplified legend
    with dot.subgraph(name='cluster_legend') as legend:
        legend.attr(label='Legend', rankdir='LR', style='filled', color='lightgrey')
        legend.node('state_types', 'State Types:', shape='plaintext')
        legend.node('menu_legend', 'Menu', style='filled', fillcolor=colors['menu'])
        legend.node('combat_legend', 'Combat', style='filled', fillcolor=colors['combat'])
        legend.node('exploration_legend', 'Exploration', style='filled', fillcolor=colors['exploration'])
        legend.node('other_legend', 'Other', style='filled', fillcolor=colors['other'])

    # Save the diagram
    dot.render('game_state_machine', cleanup=True)
    print("Enhanced state machine diagram saved as 'game_state_machine.png'")

if __name__ == "__main__":
    create_state_machine_diagram()
