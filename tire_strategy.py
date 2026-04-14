"""
WEC Tire Strategy Optimizer
============================

Predicts tire degradation and optimal stint length for endurance racing.

Based on:
- Previous tire degradation modeling experience (MacGyver toolkit)
- Engineering principles for compound behavior
- To be refined with Chapter 10 (Tire Management) technical data

Author: Alexandru
Version: 1.0 (Pre-book baseline)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class TireCompound:
    """Tire compound characteristics"""
    name: str
    peak_grip: float  # Relative grip coefficient (1.0 = baseline)
    initial_degradation_rate: float  # % per lap initial
    degradation_acceleration: float  # How quickly deg rate increases
    optimal_temp_c: float  # Optimal operating temperature
    cliff_lap: int  # Lap where performance falls off cliff


@dataclass
class TrackConditions:
    """Track and environmental conditions"""
    ambient_temp_c: float = 25.0
    track_temp_c: float = 35.0
    track_length_km: float = 13.626  # Le Mans
    avg_speed_kmh: float = 220.0
    fuel_load_kg: float = 75.0  # Starting fuel load
    fuel_consumption_kg_per_lap: float = 2.5


class TireStrategyOptimizer:
    """Optimizes tire stint length and compound selection"""
    
    # Tire compound library
    COMPOUNDS = {
        'soft': TireCompound('Soft', 1.0, 0.08, 0.002, 95.0, 25),
        'medium': TireCompound('Medium', 0.97, 0.05, 0.0015, 100.0, 40),
        'hard': TireCompound('Hard', 0.94, 0.03, 0.001, 105.0, 60),
    }
    
    def __init__(self, conditions: TrackConditions):
        self.conditions = conditions
        
    def calculate_degradation(self, compound: TireCompound, lap: int, track_temp: float) -> float:
        """Calculate tire degradation at a given lap"""
        # Base degradation increases polynomially
        base_deg = compound.initial_degradation_rate + (compound.degradation_acceleration * lap)
        
        # Temperature effect (simplified)
        temp_delta = abs(track_temp - compound.optimal_temp_c)
        temp_factor = 1.0 + (temp_delta / 100.0)  # 1% increase per degree off optimal
        
        total_deg = base_deg * temp_factor
        
        # Cliff effect
        if lap >= compound.cliff_lap:
            cliff_multiplier = 1.0 + (0.1 * (lap - compound.cliff_lap))
            total_deg *= cliff_multiplier
        
        return total_deg
    
    def simulate_stint(self, compound_name: str, max_laps: int = 60) -> pd.DataFrame:
        """Simulate tire performance over a stint"""
        compound = self.COMPOUNDS[compound_name]
        
        results = []
        current_grip = compound.peak_grip
        current_fuel = self.conditions.fuel_load_kg
        
        for lap in range(1, max_laps + 1):
            # Degradation this lap
            deg_rate = self.calculate_degradation(compound, lap, self.conditions.track_temp_c)
            current_grip *= (1.0 - deg_rate)
            
            # Fuel effect on lap time (lighter = faster)
            fuel_effect_s = (current_fuel / 100.0) * 0.5  # ~0.5s per 100kg fuel
            current_fuel = max(0, current_fuel - self.conditions.fuel_consumption_kg_per_lap)
            
            # Baseline lap time (assuming ~3:30 for Le Mans LMP)
            baseline_lap_s = 210.0
            
            # Grip effect on lap time (simplified: 1% grip loss = 0.3s slower)
            grip_loss = compound.peak_grip - current_grip
            grip_effect_s = grip_loss * 30.0  # Scaling factor
            
            lap_time_s = baseline_lap_s + grip_effect_s + fuel_effect_s
            
            results.append({
                'lap': lap,
                'grip_level': current_grip,
                'degradation_rate': deg_rate * 100,  # As percentage
                'lap_time_s': lap_time_s,
                'fuel_remaining_kg': current_fuel,
                'compound': compound_name
            })
        
        return pd.DataFrame(results)
    
    def find_optimal_stint_length(self, compound_name: str, max_acceptable_lap_time_s: float = 218.0) -> int:
        """Find optimal stint length before tire performance degrades too much"""
        stint_data = self.simulate_stint(compound_name, max_laps=80)
        
        # Find first lap where lap time exceeds threshold by 3 seconds
        baseline = stint_data['lap_time_s'].min()
        slow_laps = stint_data[stint_data['lap_time_s'] > (baseline + 8.0)]
        
        if len(slow_laps) == 0:
            return len(stint_data)
        
        return max(1, slow_laps.iloc[0]['lap'] - 1)
    
    def compare_compounds(self, max_laps: int = 50) -> Dict[str, pd.DataFrame]:
        """Compare all tire compounds"""
        return {
            name: self.simulate_stint(name, max_laps)
            for name in self.COMPOUNDS.keys()
        }


def visualize_tire_comparison(compound_data: Dict[str, pd.DataFrame]):
    """Visualize tire compound comparison"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    colors = {'soft': 'red', 'medium': 'orange', 'hard': 'blue'}
    
    # Grip evolution
    for compound, df in compound_data.items():
        ax1.plot(df['lap'], df['grip_level'], label=compound.title(), 
                color=colors[compound], linewidth=2.5)
    ax1.set_xlabel('Lap Number', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Grip Level (Coefficient)', fontsize=12, fontweight='bold')
    ax1.set_title('Tire Grip Degradation Over Stint', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best', fontsize=11)
    ax1.axhline(y=0.90, color='gray', linestyle='--', alpha=0.5, label='Critical Threshold')
    
    # Lap time evolution
    for compound, df in compound_data.items():
        ax2.plot(df['lap'], df['lap_time_s'], label=compound.title(), 
                color=colors[compound], linewidth=2.5)
    ax2.set_xlabel('Lap Number', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Lap Time (seconds)', fontsize=12, fontweight='bold')
    ax2.set_title('Lap Time Evolution (Tire + Fuel Effect)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='best', fontsize=11)
    ax2.axhline(y=215, color='gray', linestyle='--', alpha=0.5, label='Target Lap Time')
    
    # Degradation rate
    for compound, df in compound_data.items():
        ax3.plot(df['lap'], df['degradation_rate'], label=compound.title(), 
                color=colors[compound], linewidth=2.5)
    ax3.set_xlabel('Lap Number', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Degradation Rate (%/lap)', fontsize=12, fontweight='bold')
    ax3.set_title('Tire Degradation Rate Acceleration', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='best', fontsize=11)
    
    # Cumulative time loss
    for compound, df in compound_data.items():
        baseline = df['lap_time_s'].min()
        cumulative_loss = (df['lap_time_s'] - baseline).cumsum()
        ax4.plot(df['lap'], cumulative_loss, label=compound.title(), 
                color=colors[compound], linewidth=2.5)
    ax4.set_xlabel('Lap Number', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Cumulative Time Loss (seconds)', fontsize=12, fontweight='bold')
    ax4.set_title('Cumulative Time Lost vs. Optimal Performance', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend(loc='best', fontsize=11)
    
    plt.tight_layout()
    return fig


def main():
    """Demo the tire strategy optimizer"""
    print("=" * 70)
    print("WEC TIRE STRATEGY OPTIMIZER - Le Mans 24 Hours")
    print("=" * 70)
    print()
    
    # Setup conditions
    conditions = TrackConditions(
        ambient_temp_c=25.0,
        track_temp_c=35.0,
        track_length_km=13.626,
        avg_speed_kmh=220.0,
        fuel_load_kg=75.0
    )
    
    print(f"Track Conditions:")
    print(f"  Track Temperature: {conditions.track_temp_c}°C")
    print(f"  Track Length: {conditions.track_length_km} km")
    print(f"  Starting Fuel Load: {conditions.fuel_load_kg} kg")
    print()
    
    optimizer = TireStrategyOptimizer(conditions)
    
    # Compare compounds
    print("Tire Compound Comparison:")
    print("-" * 70)
    comparison = optimizer.compare_compounds(max_laps=50)
    
    for compound_name, df in comparison.items():
        compound = optimizer.COMPOUNDS[compound_name]
        optimal_stint = optimizer.find_optimal_stint_length(compound_name)
        
        # Calculate stint performance
        stint_data = df[df['lap'] <= optimal_stint]
        avg_lap_time = stint_data['lap_time_s'].mean()
        total_stint_time = stint_data['lap_time_s'].sum()
        
        print(f"\n{compound_name.upper()} Compound:")
        print(f"  Peak Grip: {compound.peak_grip:.2f}")
        print(f"  Optimal Temperature: {compound.optimal_temp_c}°C")
        print(f"  Performance Cliff: Lap {compound.cliff_lap}")
        print(f"  Recommended Stint Length: {optimal_stint} laps")
        print(f"  Average Lap Time: {avg_lap_time:.2f}s")
        print(f"  Total Stint Time: {total_stint_time/60:.2f} minutes")
    
    # Strategy recommendation
    print("\n" + "=" * 70)
    print("RACE STRATEGY RECOMMENDATION:")
    print("=" * 70)
    print()
    print("For 24-hour endurance:")
    print("  • Start on SOFT for qualifying pace and track position")
    print("  • Switch to MEDIUM for consistency during daylight")
    print("  • Use HARD for overnight stints (cooler temps, driver fatigue)")
    print("  • Return to MEDIUM/SOFT for final 4 hours push")
    print()
    print("NOTE: Actual strategy depends on:")
    print("  - Traffic patterns")
    print("  - Safety car periods")
    print("  - Weather changes")
    print("  - Competitor strategies")
    print()
    print("=" * 70)
    print("v1.0 baseline model - Will refine with Chapter 10 (Tire Management)")
    print("=" * 70)
    
    # Visualize
    fig = visualize_tire_comparison(comparison)
    plt.savefig('tire_strategy_comparison.png', dpi=150, bbox_inches='tight')
    print("\nVisualization saved to: tire_strategy_comparison.png")
    plt.show()


if __name__ == "__main__":
    main()