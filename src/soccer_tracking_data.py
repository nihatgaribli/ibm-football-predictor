"""
Soccer Tracking Data Extraction Module

This module provides functionality to extract player tracking data from StatsBomb's
freeze-frame data for shot events in soccer matches.
"""

import pandas as pd
from statsbombpy import sb
from typing import Optional, Dict
import warnings


def get_world_cup_matches() -> Dict[int, Dict]:
    """
    Fetch all available FIFA World Cup 2022 matches from StatsBomb.
    
    Returns
    -------
    Dict[int, Dict]
        Dictionary mapping match IDs to match information (home, away, date)
    
    Examples
    --------
    >>> matches = get_world_cup_matches()
    >>> print(matches)
    {3869151: {'home': 'Argentina', 'away': 'France', 'date': '2022-12-18'}, ...}
    """
    try:
        # Fetch matches for FIFA World Cup 2022
        # Competition ID: 43 (FIFA World Cup)
        # Season ID: 106 (2022)
        matches_df = sb.matches(competition_id=43, season_id=106)
        
        # Create dictionary mapping match IDs to match info
        match_dict = {}
        for _, match in matches_df.iterrows():
            home_team = match.get('home_team', 'Unknown')
            away_team = match.get('away_team', 'Unknown')
            match_id = match.get('match_id')
            match_date = match.get('match_date', '')
            home_score = match.get('home_score', None)
            away_score = match.get('away_score', None)
            
            match_dict[match_id] = {
                'home': home_team,
                'away': away_team,
                'date': match_date,
                'home_score': home_score,
                'away_score': away_score,
            }
        
        print(f"Successfully loaded {len(match_dict)} World Cup 2022 matches")
        return match_dict
        
    except Exception as e:
        warnings.warn(f"Error fetching World Cup matches: {str(e)}")
        # Return a fallback with at least one known match
        return {3869151: {'home': 'Argentina', 'away': 'France', 'date': '2022-12-18',
                          'home_score': 3, 'away_score': 3}}


def get_soccer_tracking_data(match_id: int) -> pd.DataFrame:
    """
    Extract player tracking data from StatsBomb freeze-frame data for a specific match.
    
    This function fetches match events, filters for shot events, and extracts the X and Y
    coordinates of all players visible in the freeze-frame along with their metadata.
    
    Parameters
    ----------
    match_id : int
        The StatsBomb match ID to fetch data for (e.g., 3869151)
    
    Returns
    -------
    pd.DataFrame
        A DataFrame where each row represents a single player's location during a shot.
        Columns include:
        - shot_id: Unique identifier for the shot event
        - timestamp: Time of the shot event
        - player_name: Name of the player in the freeze-frame
        - team_name: Name of the player's team
        - x: X coordinate of the player's position
        - y: Y coordinate of the player's position
        - is_goalkeeper: Boolean indicating if the player is a goalkeeper
    
    Raises
    ------
    ValueError
        If no shot events with freeze-frame data are found in the match
    
    Examples
    --------
    >>> df = get_soccer_tracking_data(match_id=3869151)
    >>> print(df.head())
    """
    
    # Fetch match events
    try:
        events = sb.events(match_id=match_id)
    except Exception as e:
        raise ValueError(f"Failed to fetch events for match_id {match_id}: {str(e)}")
    
    # Filter for shot events only
    shot_events = events[events['type'] == 'Shot'].copy()
    
    if shot_events.empty:
        raise ValueError(f"No shot events found for match_id {match_id}")
    
    # List to store all player tracking data
    tracking_data = []
    
    # Counter for shots with freeze-frame data
    shots_with_data = 0
    
    # Iterate through each shot event
    for idx, shot in shot_events.iterrows():
        try:
            # Check if freeze-frame data exists
            freeze_frame = shot.get('shot_freeze_frame')
            if freeze_frame is None or (isinstance(freeze_frame, float) and pd.isna(freeze_frame)):
                continue
            
            # Skip if freeze_frame is not a list or is empty
            if not isinstance(freeze_frame, list) or len(freeze_frame) == 0:
                continue
            
            shots_with_data += 1
            
            # Extract shot metadata
            shot_id = shot.get('id', idx)
            timestamp = shot.get('timestamp', None)
            
            # Iterate through each player in the freeze-frame
            for player_data in freeze_frame:
                try:
                    # Extract player information
                    player_name = player_data.get('player', {}).get('name', 'Unknown')
                    team_name = player_data.get('teammate', None)
                    
                    # Convert teammate boolean to actual team name if possible
                    teammate_flag = player_data.get('teammate', None)
                    if teammate_flag is True:
                        raw_team = shot.get('team', 'Teammate')
                        # StatsBomb sometimes returns a dict {'id': .., 'name': ..}
                        if isinstance(raw_team, dict):
                            team_name = raw_team.get('name', 'Teammate')
                        else:
                            team_name = str(raw_team) if raw_team else 'Teammate'
                    elif teammate_flag is False:
                        team_name = 'Opponent'
                    else:
                        team_name = 'Unknown'
                    
                    # Extract position coordinates
                    location = player_data.get('location', [None, None])
                    x = location[0] if len(location) > 0 else None
                    y = location[1] if len(location) > 1 else None
                    
                    # Check if player is goalkeeper
                    is_goalkeeper = player_data.get('position', {}).get('name', '') == 'Goalkeeper'
                    
                    # Append to tracking data list
                    tracking_data.append({
                        'shot_id': shot_id,
                        'timestamp': timestamp,
                        'player_name': player_name,
                        'team_name': team_name,
                        'x': x,
                        'y': y,
                        'is_goalkeeper': is_goalkeeper
                    })
                    
                except (KeyError, TypeError, IndexError) as e:
                    # Log warning but continue processing other players
                    warnings.warn(
                        f"Error extracting player data from shot {shot_id}: {str(e)}",
                        UserWarning
                    )
                    continue
                    
        except (KeyError, TypeError) as e:
            # Log warning but continue processing other shots
            warnings.warn(
                f"Error processing shot at index {idx}: {str(e)}",
                UserWarning
            )
            continue
    
    # Check if any tracking data was extracted
    if not tracking_data:
        raise ValueError(
            f"No freeze-frame tracking data found for match_id {match_id}. "
            f"Found {len(shot_events)} shot events, but none contained valid freeze-frame data."
        )
    
    # Create DataFrame from tracking data
    df = pd.DataFrame(tracking_data)
    
    # Print summary information
    print(f"Successfully extracted tracking data:")
    print(f"  - Total shots with freeze-frame data: {shots_with_data}")
    print(f"  - Total player positions extracted: {len(df)}")
    print(f"  - Unique shots: {df['shot_id'].nunique()}")
    
    return df


def main():
    """
    Example usage of the get_soccer_tracking_data function.
    """
    # Example match ID
    match_id = 3869151
    
    try:
        # Get tracking data
        tracking_df = get_soccer_tracking_data(match_id=match_id)
        
        # Display basic information
        print("\n" + "="*60)
        print("DataFrame Info:")
        print("="*60)
        print(tracking_df.info())
        
        print("\n" + "="*60)
        print("First 10 rows:")
        print("="*60)
        print(tracking_df.head(10))
        
        print("\n" + "="*60)
        print("Summary Statistics:")
        print("="*60)
        print(f"Total players tracked: {len(tracking_df)}")
        print(f"Unique shots: {tracking_df['shot_id'].nunique()}")
        print(f"Goalkeepers in data: {tracking_df['is_goalkeeper'].sum()}")
        print(f"Teams: {tracking_df['team_name'].unique()}")
        
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()

# Made with Bob
