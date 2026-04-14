"""
WEC Hybrid Deployment Optimizer
================================

Simulates MGU-K energy recovery and deployment for LMP Hypercar.

Based on:
- WEC Hypercar regulations (4MJ max deployment per lap at Le Mans)
- Engineering estimates of recovery/deployment efficiency
- To be refined with Chapter 5 (Hybrid Power Units) technical data

Author: Alexandru
Version: 1.0 (Pre-book baseline)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class TrackSection:
    """Represents a section of track with energy characteristics"""
    name: str
    length_m: float
    is_braking_zone: bool
    is_deployment_zone: bool
    entry_speed_kmh: float
    exit_speed_kmh: float


@dataclass
class HybridConfig:
    """Hypercar hybrid system configuration"""
    battery_capacity_mj: float = 3.2  # Typical LMP Hypercar
    max_deployment_per_lap_mj: float = 4.0  # Le Mans regulation
    max_power_kw: float = 200  # MGU-K power limit
    recovery_efficiency: float = 0.75  # Energy recovered vs. kinetic energy available
    deployment_efficiency: float = 0.85  # Actual power vs. energy used


class HybridDeploymentOptimizer:
    """Optimizes hybrid energy deployment for a lap"""
    
    def __init__(self, config: HybridConfig):
        self.config = config
        self.current_soc = config.battery_capacity_mj / 2  # Start at 50% SOC
        
    def calculate_recovery_energy(self, section: TrackSection) -> float:
        """Calculate energy recovered during braking"""
        if not section.is_braking_zone:
            return 0.0
        
        # Kinetic energy difference: 0.5 * m * (v1^2 - v2^2)
        # Assuming 1000kg car for LMP
        mass_kg = 1000
        v1_ms = section.entry_speed_kmh / 3.6
        v2_ms = section.exit_speed_kmh / 3.6
        
        kinetic_delta_j = 0.5 * mass_kg * (v1_ms**2 - v2_ms**2)
        kinetic_delta_mj = kinetic_delta_j / 1_000_000
        
        # Apply recovery efficiency
        recovered_mj = kinetic_delta_mj * self.config.recovery_efficiency
        
        return max(0, min(recovered_mj, self.config.battery_capacity_mj - self.current_soc))
    
    def calculate_deployment_benefit(self, section: TrackSection) -> Tuple[float, float]:
        """Calculate optimal deployment and time gained"""
        if not section.is_deployment_zone:
            return 0.0, 0.0
        
        # Available energy for this section
        available_energy = min(self.current_soc, self.config.max_deployment_per_lap_mj)
        
        # Deployment time (assume deployment over ~3 seconds at corner exit)
        deployment_time_s = 3.0
        
        # Power = Energy / Time
        deployment_power_kw = (available_energy * 1000) / deployment_time_s
        deployment_power_kw = min(deployment_power_kw, self.config.max_power_kw)
        
        # Actual energy used
        energy_used_mj = (deployment_power_kw * deployment_time_s) / 1000
        
        # Simplified lap time benefit: ~0.1s per 100kW deployed
        # TODO: Refine with Chapter 5 data
        time_benefit_s = (deployment_power_kw / 100) * 0.1
        
        return energy_used_mj, time_benefit_s
    
    def simulate_lap(self, track_sections: List[TrackSection]) -> pd.DataFrame:
        """Simulate one lap with hybrid deployment strategy"""
        results = []
        total_deployed = 0.0
        total_time_gained = 0.0
        
        for section in track_sections:
            # Recovery phase
            recovered = self.calculate_recovery_energy(section)
            self.current_soc += recovered
            self.current_soc = min(self.current_soc, self.config.battery_capacity_mj)
            
            # Deployment phase
            deployed, time_gain = self.calculate_deployment_benefit(section)
            
            # Check regulation limit
            if total_deployed + deployed > self.config.max_deployment_per_lap_mj:
                deployed = max(0, self.config.max_deployment_per_lap_mj - total_deployed)
                time_gain = time_gain * (deployed / (deployed + 0.001))  # Proportional reduction
            
            self.current_soc -= deployed
            total_deployed += deployed
            total_time_gained += time_gain
            
            results.append({
                'section': section.name,
                'soc_before': self.current_soc + deployed - recovered,
                'recovered_mj': recovered,
                'deployed_mj': deployed,
                'soc_after': self.current_soc,
                'time_gain_s': time_gain
            })
        
        return pd.DataFrame(results)


def create_le_mans_simplified() -> List[TrackSection]:
    """Create simplified Le Mans track model"""
    # Simplified to major corners and straights
    sections = [
        TrackSection("Dunlop Chicane Entry", 200, True, False, 280, 140),
        TrackSection("Dunlop Chicane Exit", 100, False, True, 140, 200),
        TrackSection("Esses", 400, False, False, 200, 180),
        TrackSection("Tertre Rouge Braking", 150, True, False, 250, 120),
        TrackSection("Tertre Rouge Exit", 100, False, True, 120, 220),
        TrackSection("Mulsanne Straight", 2000, False, True, 220, 330),
        TrackSection("Mulsanne Corner", 100, True, False, 330, 100),
        TrackSection("Mulsanne Exit", 100, False, True, 100, 200),
        TrackSection("Indianapolis", 300, True, False, 270, 90),
        TrackSection("Indianapolis Exit", 100, False, True, 90, 180),
        TrackSection("Arnage Braking", 200, True, False, 280, 80),
        TrackSection("Arnage Exit", 100, False, True, 80, 160),
        TrackSection("Porsche Curves", 800, False, False, 160, 200),
        TrackSection("Ford Chicane Entry", 150, True, False, 260, 120),
        TrackSection("Ford Chicane Exit", 100, False, True, 120, 200),
    ]
    return sections


def visualize_deployment_strategy(results: pd.DataFrame):
    """Visualize hybrid deployment over a lap"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # SOC evolution
    ax1.plot(results.index, results['soc_before'], 'b-', label='SOC Before Section', linewidth=2)
    ax1.plot(results.index, results['soc_after'], 'r--', label='SOC After Section', linewidth=2)
    ax1.fill_between(results.index, results['soc_before'], results['soc_after'], alpha=0.3)
    ax1.set_ylabel('Battery SOC (MJ)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Track Section', fontsize=12)
    ax1.set_title('Hybrid Battery State of Charge Evolution - Le Mans', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best')
    ax1.set_xticks(results.index)
    ax1.set_xticklabels(results['section'], rotation=45, ha='right')
    
    # Energy flow
    x = results.index
    ax2.bar(x - 0.2, results['recovered_mj'], 0.4, label='Energy Recovered', color='green', alpha=0.7)
    ax2.bar(x + 0.2, results['deployed_mj'], 0.4, label='Energy Deployed', color='orange', alpha=0.7)
    ax2.set_ylabel('Energy (MJ)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Track Section', fontsize=12)
    ax2.set_title('Energy Recovery vs Deployment', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.legend(loc='best')
    ax2.set_xticks(results.index)
    ax2.set_xticklabels(results['section'], rotation=45, ha='right')
    
    plt.tight_layout()
    return fig


def main():
    """Demo the hybrid optimizer"""
    print("=" * 70)
    print("WEC HYBRID DEPLOYMENT OPTIMIZER - Le Mans 24 Hours")
    print("=" * 70)
    print()
    
    # Create track and optimizer
    track = create_le_mans_simplified()
    config = HybridConfig()
    optimizer = HybridDeploymentOptimizer(config)
    
    print(f"Hybrid Configuration:")
    print(f"  Battery Capacity: {config.battery_capacity_mj:.2f} MJ")
    print(f"  Max Deployment/Lap: {config.max_deployment_per_lap_mj:.2f} MJ (Le Mans regulation)")
    print(f"  Max Power: {config.max_power_kw:.0f} kW")
    print(f"  Starting SOC: {optimizer.current_soc:.2f} MJ")
    print()
    
    # Simulate lap
    results = optimizer.simulate_lap(track)
    
    # Summary statistics
    total_recovered = results['recovered_mj'].sum()
    total_deployed = results['deployed_mj'].sum()
    total_time_gain = results['time_gain_s'].sum()
    
    print(f"Lap Summary:")
    print(f"  Total Energy Recovered: {total_recovered:.3f} MJ")
    print(f"  Total Energy Deployed: {total_deployed:.3f} MJ")
    print(f"  Net Energy Balance: {total_recovered - total_deployed:+.3f} MJ")
    print(f"  Estimated Time Gain: {total_time_gain:.3f} seconds")
    print(f"  Final SOC: {optimizer.current_soc:.2f} MJ")
    print()
    
    # Detailed breakdown
    print("Section-by-Section Breakdown:")
    print("-" * 70)
    for _, row in results.iterrows():
        if row['recovered_mj'] > 0:
            print(f"  {row['section']:30s} | RECOVERY: {row['recovered_mj']:.3f} MJ")
        if row['deployed_mj'] > 0:
            print(f"  {row['section']:30s} | DEPLOY:   {row['deployed_mj']:.3f} MJ → {row['time_gain_s']:.3f}s gain")
    
    print()
    print("=" * 70)
    print("NOTE: This is v1.0 baseline model using engineering estimates.")
    print("Will be refined with Chapter 5 (Hybrid Power Units) technical data.")
    print("=" * 70)
    
    # Visualize
    fig = visualize_deployment_strategy(results)
    plt.savefig('hybrid_deployment_le_mans.png', dpi=150, bbox_inches='tight')
    print("\nVisualization saved to: hybrid_deployment_le_mans.png")
    plt.show()


if __name__ == "__main__":
    main()