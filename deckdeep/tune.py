import math
import plotly.graph_objects as go

def calculate_baseline_monster_power(level):
    base_health = 12 + math.log(level + 1, 3) * 8
    base_damage = 6 + math.log(level + 1, 3) * 3
    base_spell_power = 6 + math.log(level + 1, 3) * 3
    
    # Assuming average multipliers for monster types
    avg_health_mult = 1.0
    avg_damage_mult = 1.0
    avg_spell_power_mult = 1.0
    
    health = base_health * avg_health_mult
    damage = base_damage * avg_damage_mult
    spell_power = base_spell_power * avg_spell_power_mult
    
    # Simplified power rating calculation
    base_survivability = health / 6
    ability_power = (damage + spell_power) / 2  # Simplified ability power calculation
    
    return base_survivability * ability_power

def calculate_monster_group_power_limit(level):
    return math.log(level + 1, 3) * 100

def plot_monster_power_scaling():
    levels = list(range(1, 51))  # Plot for levels 1 to 50
    
    baseline_powers = [calculate_baseline_monster_power(level) for level in levels]
    group_power_limits = [calculate_monster_group_power_limit(level) for level in levels]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=levels, y=baseline_powers, mode='lines', name='Baseline Monster Power'))
    fig.add_trace(go.Scatter(x=levels, y=group_power_limits, mode='lines', name='Monster Group Power Limit'))
    
    fig.update_layout(
        title='Monster Power Scaling',
        xaxis_title='Level',
        yaxis_title='Power',
        legend_title='Legend',
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        )
    )
    
    fig.write_html("monster_power_scaling.html")

if __name__ == "__main__":
    plot_monster_power_scaling()
    print("Plot saved as 'monster_power_scaling.html'")