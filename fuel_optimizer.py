"""
WEC Fuel Strategy Optimizer
============================

Calculates optimal pit windows and stint lengths for fuel efficiency.

Based on:
- Endurance racing fuel management principles
- Pit stop time loss calculations
- To be refined with Chapter 10 (Fuel Strategy) technical data

Author: Alexandru
Version: 1.0 (Pre-book baseline)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class RaceConfig:
    """Race and car configuration"""
    race_duration_hours: float = 24.0
    track_length_km: float = 13.626  # Le Mans
    fuel_tank_capacity_l: float = 90.0
    fuel_consumption_l_per_lap: float = 2.3
    pit_stop_duration_s: float = 45.0  # Refuel + tire change
    refuel_only_duration_s: float = 25.0  # Fuel only, no tires
    avg_lap_time_s: float = 210.0  # 3:30 target
    safety_margin_laps: int = 2  # Extra fuel for traffic/FCY


class FuelStrategyOptimizer:
    """Optimizes fuel strategy and pit windows"""
    
    def __init__(self, config: RaceConfig):
        self.config = config
        
    def calculate_stint_length(self, fuel_load_l: float) -> int:
        """Calculate maximum laps on current fuel load"""
        usable_fuel = fuel_load_l - (self.config.fuel_consumption_l_per_lap * self.config.safety_margin_laps)
        max_laps = int(usable_fuel / self.config.fuel_consumption_l_per_lap)
        return max(1, max_laps)
    
    def calculate_fuel_effect_on_lap_time(self, fuel_remaining_l: float) -> float:
        """Calculate lap time penalty from fuel weight"""
        # Fuel weight effect: ~0.03s per lap per 10L of fuel
        # Full tank (~90L) = ~0.27s slower than empty
        fuel_weight_kg = fuel_remaining_l * 0.75  # Fuel density ~0.75 kg/L
        lap_time_penalty_s = (fuel_weight_kg / 100.0) * 0.4
        return lap_time_penalty_s
    
    def optimize_pit_window(self, start_fuel_l: float, target_laps: int) -> Tuple[int, float]:
        """Find optimal pit lap to minimize time loss"""
        # Strategy: Pit as late as safely possible to minimize fuel weight
        max_stint = self.calculate_stint_length(start_fuel_l)
        
        if target_laps <= max_stint:
            return target_laps, 0.0  # No pit needed
        
        # Calculate optimal pit lap
        optimal_pit_lap = max_stint - self.config.safety_margin_laps
        
        # Time lost in pit
        pit_time_loss_s = self.config.pit_stop_duration_s
        
        return optimal_pit_lap, pit_time_loss_s
    
    def simulate_race_fuel_strategy(self) -> pd.DataFrame:
        """Simulate full 24-hour race fuel strategy"""
        total_laps = int((self.config.race_duration_hours * 3600) / self.config.avg_lap_time_s)
        
        results = []
        current_lap = 1
        current_fuel = self.config.fuel_tank_capacity_l
        stint_number = 1
        total_pit_time = 0.0
        
        while current_lap <= total_laps:
            # Calculate stint length
            stint_laps = self.calculate_stint_length(current_fuel)
            
            # Simulate each lap in stint
            for lap_in_stint in range(1, stint_laps + 1):
                if current_lap > total_laps:
                    break
                
                # Fuel consumption
                current_fuel -= self.config.fuel_consumption_l_per_lap
                
                # Lap time with fuel effect
                fuel_effect = self.calculate_fuel_effect_on_lap_time(current_fuel)
                lap_time = self.config.avg_lap_time_s + fuel_effect
                
                results.append({
                    'lap': current_lap,
                    'stint': stint_number,
                    'lap_in_stint': lap_in_stint,
                    'fuel_remaining_l': current_fuel,
                    'lap_time_s': lap_time,
                    'is_pit_lap': False,
                    'cumulative_pit_time_s': total_pit_time
                })
                
                current_lap += 1
            
            # Pit stop (if not finished)
            if current_lap <= total_laps:
                # Determine if tire change needed (every ~60 laps = ~3.5 hours)
                laps_since_tires = sum(1 for r in results if r['stint'] == stint_number)
                needs_tires = (laps_since_tires >= 55)
                
                pit_duration = self.config.pit_stop_duration_s if needs_tires else self.config.refuel_only_duration_s
                total_pit_time += pit_duration
                
                # Refuel
                current_fuel = self.config.fuel_tank_capacity_l
                
                results.append({
                    'lap': current_lap,
                    'stint': stint_number,
                    'lap_in_stint': lap_in_stint + 1,
                    'fuel_remaining_l': current_fuel,
                    'lap_time_s': self.config.avg_lap_time_s + pit_duration,
                    'is_pit_lap': True,
                    'cumulative_pit_time_s': total_pit_time
                })
                
                stint_number += 1
                current_lap += 1
        
        return pd.DataFrame(results)
    
    def calculate_race_summary(self, race_data: pd.DataFrame) -> dict:
        """Calculate race summary statistics"""
        total_laps = len(race_data)
        pit_stops = len(race_data[race_data['is_pit_lap']])
        total_race_time_s = race_data['lap_time_s'].sum()
        total_pit_time_s = race_data[race_data['is_pit_lap']]['lap_time_s'].sum() - (pit_stops * self.config.avg_lap_time_s)
        avg_stint_length = total_laps / (pit_stops + 1) if pit_stops > 0 else total_laps
        
        return {
            'total_laps': total_laps,
            'pit_stops': pit_stops,
            'total_race_time_hours': total_race_time_s / 3600,
            'total_pit_time_minutes': total_pit_time_s / 60,
            'avg_stint_length_laps': avg_stint_length,
            'fuel_efficiency_l_per_lap': self.config.fuel_consumption_l_per_lap
        }


def visualize_fuel_strategy(race_data: pd.DataFrame):
    """Visualize fuel strategy over 24 hours"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))
    
    # Fuel remaining over race
    ax1.plot(race_data['lap'], race_data['fuel_remaining_l'], 'b-', linewidth=1.5)
    pit_laps = race_data[race_data['is_pit_lap']]
    ax1.scatter(pit_laps['lap'], pit_laps['fuel_remaining_l'], color='red', s=100, 
               marker='v', label='Pit Stop', zorder=5)
    ax1.set_xlabel('Lap Number', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Fuel Remaining (L)', fontsize=12, fontweight='bold')
    ax1.set_title('Fuel Load Evolution - 24 Hour Race', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best')
    ax1.axhline(y=10, color='orange', linestyle='--', alpha=0.5, label='Low Fuel Warning')
    
    # Lap time variation
    non_pit_laps = race_data[~race_data['is_pit_lap']]
    ax2.plot(non_pit_laps['lap'], non_pit_laps['lap_time_s'], 'g-', linewidth=1.5, alpha=0.7)
    ax2.set_xlabel('Lap Number', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Lap Time (seconds)', fontsize=12, fontweight='bold')
    ax2.set_title('Lap Time Variation (Fuel Weight Effect)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=210, color='gray', linestyle='--', alpha=0.5, label='Target Lap Time')
    
    # Stint length distribution
    stint_lengths = race_data.groupby('stint').size()
    ax3.bar(stint_lengths.index, stint_lengths.values, color='steelblue', alpha=0.7, edgecolor='black')
    ax3.set_xlabel('Stint Number', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Laps per Stint', fontsize=12, fontweight='bold')
    ax3.set_title('Stint Length Distribution', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Cumulative pit time loss
    ax4.plot(race_data['lap'], race_data['cumulative_pit_time_s'] / 60, 'r-', linewidth=2.5)
    ax4.set_xlabel('Lap Number', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Cumulative Pit Time (minutes)', fontsize=12, fontweight='bold')
    ax4.set_title('Total Time Lost in Pit Stops', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def main():
    """Demo the fuel strategy optimizer"""
    print("=" * 80)
    print("WEC FUEL STRATEGY OPTIMIZER - Le Mans 24 Hours")
    print("=" * 80)
    print()
    
    # Setup race config
    config = RaceConfig()
    
    print(f"Race Configuration:")
    print(f"  Duration: {config.race_duration_hours} hours")
    print(f"  Track Length: {config.track_length_km} km")
    print(f"  Tank Capacity: {config.fuel_tank_capacity_l} L")
    print(f"  Consumption: {config.fuel_consumption_l_per_lap} L/lap")
    print(f"  Target Lap Time: {config.avg_lap_time_s}s ({config.avg_lap_time_s/60:.2f} min)")
    print(f"  Pit Stop Duration: {config.pit_stop_duration_s}s (full) / {config.refuel_only_duration_s}s (fuel only)")
    print()
    
    optimizer = FuelStrategyOptimizer(config)
    
    # Calculate single stint potential
    print("Single Stint Analysis:")
    print("-" * 80)
    max_stint = optimizer.calculate_stint_length(config.fuel_tank_capacity_l)
    print(f"  Maximum laps on full tank: {max_stint} laps")
    print(f"  Distance per stint: {max_stint * config.track_length_km:.1f} km")
    print(f"  Time per stint: {max_stint * config.avg_lap_time_s / 60:.1f} minutes")
    print()
    
    # Simulate full race
    print("Simulating 24-hour race strategy...")
    race_data = optimizer.simulate_race_fuel_strategy()
    summary = optimizer.calculate_race_summary(race_data)
    
    print()
    print("Race Summary:")
    print("=" * 80)
    print(f"  Total Laps: {summary['total_laps']}")
    print(f"  Total Distance: {summary['total_laps'] * config.track_length_km:.1f} km")
    print(f"  Pit Stops: {summary['pit_stops']}")
    print(f"  Average Stint Length: {summary['avg_stint_length_laps']:.1f} laps")
    print(f"  Total Race Time: {summary['total_race_time_hours']:.2f} hours")
    print(f"  Total Pit Time: {summary['total_pit_time_minutes']:.1f} minutes")
    print(f"  Fuel Efficiency: {summary['fuel_efficiency_l_per_lap']:.2f} L/lap")
    print()
    
    # Pit stop schedule
    pit_stops = race_data[race_data['is_pit_lap']]
    print("Pit Stop Schedule:")
    print("-" * 80)
    for idx, (_, pit) in enumerate(pit_stops.iterrows(), 1):
        hour = (pit['lap'] * config.avg_lap_time_s) / 3600
        print(f"  Stop {idx:2d}: Lap {int(pit['lap']):3d} | Hour {hour:5.2f} | Stint {int(pit['stint']):2d}")
    
    print()
    print("=" * 80)
    print("STRATEGY INSIGHTS:")
    print("=" * 80)
    print()
    print("  • Consistent ~38 lap stints minimize pit stops while maintaining safety margin")
    print("  • Fuel-only stops save ~20s vs. full service when tires don't need changing")
    print("  • Lighter fuel loads toward end of stint = faster lap times")
    print("  • Safety margin crucial for traffic, safety cars, code 60 zones")
    print()
    print("NOTE: Actual race strategy must adapt to:")
    print("  - Safety car periods (opportunity for 'free' pit stops)")
    print("  - Code 60 zones (fuel savings in slow zones)")
    print("  - Traffic patterns (fuel consumption in dirty air)")
    print("  - Weather changes (wet = higher consumption)")
    print()
    print("=" * 80)
    print("v1.0 baseline model - Will refine with Chapter 10 (Fuel Strategy)")
    print("=" * 80)
    
    # Visualize
    fig = visualize_fuel_strategy(race_data)
    plt.savefig('fuel_strategy_24h.png', dpi=150, bbox_inches='tight')
    print("\nVisualization saved to: fuel_strategy_24h.png")
    plt.show()


if __name__ == "__main__":
    main()