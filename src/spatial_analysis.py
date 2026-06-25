"""
Spatial Analysis Module for Soccer Tracking Data

This module provides functionality to compute bounded Voronoi diagrams on a soccer pitch
and analyze spatial dominance patterns during shot events.
"""

import numpy as np
import pandas as pd
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from typing import Dict, List, Tuple, Optional
import warnings


class SoccerVoronoiAnalyzer:
    """
    Analyzer for computing bounded Voronoi diagrams on a soccer pitch.
    
    This class takes player tracking data from a single shot event and computes
    bounded Voronoi cells for each player, calculating spatial dominance metrics.
    
    Attributes
    ----------
    pitch_length : float
        Length of the soccer pitch (default: 120)
    pitch_width : float
        Width of the soccer pitch (default: 80)
    attacking_third_start : float
        X-coordinate where the attacking third begins (default: 80)
    """
    
    def __init__(
        self,
        pitch_length: float = 120.0,
        pitch_width: float = 80.0,
        attacking_third_start: float = 80.0
    ):
        """
        Initialize the SoccerVoronoiAnalyzer.
        
        Parameters
        ----------
        pitch_length : float, optional
            Length of the soccer pitch in yards (default: 120)
        pitch_width : float, optional
            Width of the soccer pitch in yards (default: 80)
        attacking_third_start : float, optional
            X-coordinate where attacking third begins (default: 80)
        """
        self.pitch_length = pitch_length
        self.pitch_width = pitch_width
        self.attacking_third_start = attacking_third_start
        
        # Create pitch boundary polygon
        self.pitch_boundary = box(0, 0, pitch_length, pitch_width)
        
        # Create attacking third boundary
        self.attacking_third = box(
            attacking_third_start, 0,
            pitch_length, pitch_width
        )
    
    def _add_boundary_points(
        self,
        points: np.ndarray,
        margin: float = 50.0
    ) -> np.ndarray:
        """
        Add dummy boundary points around the pitch to bound Voronoi cells.
        
        Parameters
        ----------
        points : np.ndarray
            Array of player positions (N x 2)
        margin : float, optional
            Distance of boundary points from pitch edges (default: 50)
        
        Returns
        -------
        np.ndarray
            Extended array including boundary points
        """
        # Create a grid of boundary points around the pitch
        x_min, y_min = -margin, -margin
        x_max = self.pitch_length + margin
        y_max = self.pitch_width + margin
        
        # Number of boundary points per side
        n_points = 20
        
        # Top edge
        top_x = np.linspace(x_min, x_max, n_points)
        top_y = np.full(n_points, y_max)
        
        # Bottom edge
        bottom_x = np.linspace(x_min, x_max, n_points)
        bottom_y = np.full(n_points, y_min)
        
        # Left edge
        left_x = np.full(n_points, x_min)
        left_y = np.linspace(y_min, y_max, n_points)
        
        # Right edge
        right_x = np.full(n_points, x_max)
        right_y = np.linspace(y_min, y_max, n_points)
        
        # Combine all boundary points
        boundary_x = np.concatenate([top_x, bottom_x, left_x, right_x])
        boundary_y = np.concatenate([top_y, bottom_y, left_y, right_y])
        boundary_points = np.column_stack([boundary_x, boundary_y])
        
        # Combine with original points
        extended_points = np.vstack([points, boundary_points])
        
        return extended_points
    
    def _compute_voronoi_cell(
        self,
        vor: Voronoi,
        point_idx: int
    ) -> Optional[Polygon]:
        """
        Compute the bounded Voronoi cell for a specific point.
        
        Parameters
        ----------
        vor : Voronoi
            Scipy Voronoi object
        point_idx : int
            Index of the point to compute cell for
        
        Returns
        -------
        Optional[Polygon]
            Shapely Polygon representing the bounded cell, or None if invalid
        """
        # Get the region index for this point
        region_idx = vor.point_region[point_idx]
        region = vor.regions[region_idx]
        
        # Skip if region is empty or contains -1 (infinite vertex)
        if not region or -1 in region:
            return None
        
        # Get vertices of the Voronoi cell
        vertices = vor.vertices[region]
        
        # Create polygon from vertices
        try:
            cell_polygon = Polygon(vertices)
            
            # Intersect with pitch boundary to bound the cell
            bounded_cell = cell_polygon.intersection(self.pitch_boundary)
            
            # Return only if it's a valid polygon
            if bounded_cell.is_valid and not bounded_cell.is_empty:
                return bounded_cell
            else:
                return None
                
        except Exception as e:
            warnings.warn(f"Error creating polygon for point {point_idx}: {str(e)}")
            return None
    
    def analyze_shot_event(
        self,
        shot_df: pd.DataFrame
    ) -> Dict:
        """
        Analyze a single shot event and compute Voronoi-based spatial metrics.
        
        Parameters
        ----------
        shot_df : pd.DataFrame
            DataFrame containing player positions for a single shot event.
            Must have columns: shot_id, player_name, team_name, x, y
        
        Returns
        -------
        Dict
            Dictionary containing:
            - shot_id: Identifier for the shot
            - player_areas: Dict mapping player_name to cell_area
            - team_dominance: Dict with attacking/defending team percentages
            - total_pitch_coverage: Percentage of pitch covered by all cells
            - attacking_third_coverage: Detailed coverage in attacking third
        
        Raises
        ------
        ValueError
            If DataFrame is empty or missing required columns
        """
        # Validate input
        required_cols = ['shot_id', 'player_name', 'team_name', 'x', 'y']
        missing_cols = [col for col in required_cols if col not in shot_df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        if shot_df.empty:
            raise ValueError("Input DataFrame is empty")
        
        # Extract shot_id (should be same for all rows)
        shot_id = shot_df['shot_id'].iloc[0]
        
        # Extract player positions
        points = shot_df[['x', 'y']].values
        
        # Check if we have enough points for Voronoi
        if len(points) < 3:
            warnings.warn(f"Shot {shot_id} has fewer than 3 players, skipping Voronoi analysis")
            return {
                'shot_id': shot_id,
                'player_areas': {},
                'team_dominance': {'Attacking Team': 0.0, 'Defending Team': 0.0},
                'total_pitch_coverage': 0.0,
                'attacking_third_coverage': {}
            }
        
        # Add boundary points to ensure bounded cells
        extended_points = self._add_boundary_points(points)
        
        # Compute Voronoi diagram
        try:
            vor = Voronoi(extended_points)
        except Exception as e:
            warnings.warn(f"Failed to compute Voronoi for shot {shot_id}: {str(e)}")
            return {
                'shot_id': shot_id,
                'player_areas': {},
                'team_dominance': {'Attacking Team': 0.0, 'Defending Team': 0.0},
                'total_pitch_coverage': 0.0,
                'attacking_third_coverage': {}
            }
        
        # Compute bounded cells for each player
        player_areas = {}
        
        # Get unique team names from the data
        unique_teams = shot_df['team_name'].unique()
        team_areas = {team: 0.0 for team in unique_teams}
        attacking_third_areas = {team: 0.0 for team in unique_teams}
        
        total_covered_area = 0.0
        
        for idx, row in shot_df.iterrows():
            player_name = row['player_name']
            team_name = row['team_name']
            
            # Get the index in the original points array
            point_idx = shot_df.index.get_loc(idx)
            
            # Compute bounded Voronoi cell
            cell = self._compute_voronoi_cell(vor, point_idx)
            
            if cell is not None:
                # Calculate total area
                cell_area = cell.area
                player_areas[player_name] = cell_area
                total_covered_area += cell_area
                
                # Add to team total
                team_areas[team_name] += cell_area
                
                # Calculate area in attacking third
                attacking_third_cell = cell.intersection(self.attacking_third)
                if not attacking_third_cell.is_empty:
                    attacking_area = attacking_third_cell.area
                    attacking_third_areas[team_name] += attacking_area
            else:
                player_areas[player_name] = 0.0
        
        # Calculate dominance percentages for attacking third
        attacking_third_total = self.attacking_third.area
        
        # Determine which team is attacking vs defending
        # Heuristic: team with more area in attacking third is likely attacking
        if len(attacking_third_areas) >= 2:
            sorted_teams = sorted(attacking_third_areas.items(), key=lambda x: x[1], reverse=True)
            attacking_team_name = sorted_teams[0][0]
            defending_team_name = sorted_teams[1][0] if len(sorted_teams) > 1 else sorted_teams[0][0]
            
            attacking_team_area = attacking_third_areas[attacking_team_name]
            defending_team_area = attacking_third_areas[defending_team_name]
        else:
            # Fallback if only one team
            team_name = list(attacking_third_areas.keys())[0] if attacking_third_areas else 'Unknown'
            attacking_team_area = attacking_third_areas.get(team_name, 0.0)
            defending_team_area = 0.0
        
        total_attacking_third_controlled = attacking_team_area + defending_team_area
        
        if total_attacking_third_controlled > 0:
            attacking_pct = (attacking_team_area / total_attacking_third_controlled) * 100
            defending_pct = (defending_team_area / total_attacking_third_controlled) * 100
        else:
            attacking_pct = 0.0
            defending_pct = 0.0
        
        # Calculate total pitch coverage
        pitch_area = self.pitch_boundary.area
        coverage_pct = (total_covered_area / pitch_area) * 100 if pitch_area > 0 else 0.0
        
        return {
            'shot_id': shot_id,
            'player_areas': player_areas,
            'team_dominance': {
                'Attacking Team': round(attacking_pct, 2),
                'Defending Team': round(defending_pct, 2)
            },
            'total_pitch_coverage': round(coverage_pct, 2),
            'attacking_third_coverage': {
                'Attacking Team Area': round(attacking_team_area, 2),
                'Defending Team Area': round(defending_team_area, 2),
                'Total Controlled': round(total_attacking_third_controlled, 2),
                'Attacking Third Total': round(attacking_third_total, 2)
            }
        }
    
    def analyze_multiple_shots(
        self,
        tracking_df: pd.DataFrame
    ) -> List[Dict]:
        """
        Analyze multiple shot events from a tracking DataFrame.
        
        Parameters
        ----------
        tracking_df : pd.DataFrame
            DataFrame containing multiple shot events with player positions
        
        Returns
        -------
        List[Dict]
            List of analysis results, one per shot event
        """
        results = []
        
        # Group by shot_id
        for shot_id, shot_group in tracking_df.groupby('shot_id'):
            try:
                result = self.analyze_shot_event(shot_group)
                results.append(result)
            except Exception as e:
                warnings.warn(f"Error analyzing shot {shot_id}: {str(e)}")
                continue
        
        return results
    
    def get_summary_statistics(
        self,
        results: List[Dict]
    ) -> Dict:
        """
        Compute summary statistics across multiple shot analyses.
        
        Parameters
        ----------
        results : List[Dict]
            List of analysis results from analyze_multiple_shots
        
        Returns
        -------
        Dict
            Summary statistics including average dominance, coverage, etc.
        """
        if not results:
            return {}
        
        attacking_dominance = [r['team_dominance']['Attacking Team'] for r in results]
        defending_dominance = [r['team_dominance']['Defending Team'] for r in results]
        coverage = [r['total_pitch_coverage'] for r in results]
        
        return {
            'total_shots_analyzed': len(results),
            'average_attacking_dominance': round(np.mean(attacking_dominance), 2),
            'average_defending_dominance': round(np.mean(defending_dominance), 2),
            'std_attacking_dominance': round(np.std(attacking_dominance), 2),
            'std_defending_dominance': round(np.std(defending_dominance), 2),
            'average_pitch_coverage': round(np.mean(coverage), 2),
            'max_attacking_dominance': round(np.max(attacking_dominance), 2),
            'min_attacking_dominance': round(np.min(attacking_dominance), 2)
        }


def main():
    """
    Example usage of the SoccerVoronoiAnalyzer class.
    """
    # Create sample data for demonstration
    sample_data = pd.DataFrame({
        'shot_id': ['shot_1'] * 8,
        'timestamp': ['00:10:30'] * 8,
        'player_name': ['Player A', 'Player B', 'Player C', 'Player D',
                       'Player E', 'Player F', 'Player G', 'Player H'],
        'team_name': ['Teammate', 'Teammate', 'Teammate', 'Teammate',
                     'Opponent', 'Opponent', 'Opponent', 'Opponent'],
        'x': [85, 95, 100, 90, 88, 92, 98, 105],
        'y': [40, 35, 45, 50, 30, 42, 38, 48],
        'is_goalkeeper': [False] * 8
    })
    
    print("="*70)
    print("SOCCER VORONOI SPATIAL ANALYSIS - EXAMPLE")
    print("="*70)
    
    # Initialize analyzer
    analyzer = SoccerVoronoiAnalyzer()
    
    print(f"\nPitch dimensions: {analyzer.pitch_length}x{analyzer.pitch_width}")
    print(f"Attacking third starts at X = {analyzer.attacking_third_start}")
    
    # Analyze the shot event
    print(f"\nAnalyzing shot event with {len(sample_data)} players...")
    result = analyzer.analyze_shot_event(sample_data)
    
    # Display results
    print("\n" + "="*70)
    print("ANALYSIS RESULTS")
    print("="*70)
    
    print(f"\nShot ID: {result['shot_id']}")
    print(f"Total Pitch Coverage: {result['total_pitch_coverage']}%")
    
    print("\n--- Player Controlled Areas ---")
    for player, area in result['player_areas'].items():
        print(f"  {player}: {area:.2f} sq yards")
    
    print("\n--- Team Dominance in Attacking Third (X > 80) ---")
    for team, pct in result['team_dominance'].items():
        print(f"  {team}: {pct}%")
    
    print("\n--- Attacking Third Details ---")
    for key, value in result['attacking_third_coverage'].items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

# Made with Bob
