"""
Tactical Explainer Module

This module uses IBM Granite LLM to generate natural language explanations
of spatial analysis results from soccer tracking data.
"""

import os
import json
from typing import Dict, Optional
import warnings

# Try to import IBM Granite LLM clients
try:
    from langchain_ibm import WatsonxLLM
    LANGCHAIN_IBM_AVAILABLE = True
except ImportError:
    LANGCHAIN_IBM_AVAILABLE = False
    warnings.warn("langchain_ibm not available. Install with: pip install langchain-ibm")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    warnings.warn("requests not available. Install with: pip install requests")


class TacticalExplainer:
    """
    Generate tactical explanations using IBM Granite LLM.
    
    This class takes spatial analysis results and generates human-friendly
    tactical explanations as if from an elite football coach.
    
    Attributes
    ----------
    api_key : str
        IBM Watsonx API key
    project_id : str
        IBM Watsonx project ID
    url : str
        IBM Watsonx API endpoint URL
    model_id : str
        IBM Granite model identifier
    use_mock : bool
        Whether to use mock responses (for testing without API)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        url: Optional[str] = None,
        model_id: str = "ibm/granite-13b-chat-v2",
        use_mock: bool = False
    ):
        """
        Initialize the TacticalExplainer.
        
        Parameters
        ----------
        api_key : str, optional
            IBM Watsonx API key (or set IBM_API_KEY env var)
        project_id : str, optional
            IBM Watsonx project ID (or set IBM_PROJECT_ID env var)
        url : str, optional
            IBM Watsonx URL (or set IBM_WATSONX_URL env var)
        model_id : str, optional
            Model identifier (default: ibm/granite-13b-chat-v2)
        use_mock : bool, optional
            Use mock responses for testing (default: False)
        """
        self.api_key = api_key or os.getenv('IBM_API_KEY')
        self.project_id = project_id or os.getenv('IBM_PROJECT_ID')
        self.url = url or os.getenv('IBM_WATSONX_URL', 'https://us-south.ml.cloud.ibm.com')
        self.model_id = model_id
        self.use_mock = use_mock
        
        # System prompt optimized for tactical analysis
        self.system_prompt = """You are an elite football tactical analyst with the analytical mind of Pep Guardiola and the directness of Jose Mourinho. 

Your role is to explain complex spatial data from match freeze-frames to casual football fans in a way that's insightful yet accessible.

Key principles:
- Be concise: Maximum 4 sentences
- Be specific: Reference actual numbers and player positions
- Be insightful: Explain WHY things happened tactically
- Be engaging: Use vivid football language

Focus on:
1. Spatial dominance paradoxes (e.g., why a team with more space still conceded)
2. Individual player positioning errors or brilliance
3. Tactical implications of the space distribution

Avoid:
- Generic statements
- Overly technical jargon
- Speculation without data support
- More than 4 sentences"""

    def _format_prompt(self, analysis_result: Dict) -> str:
        """
        Format the spatial analysis results into a structured prompt.
        
        Parameters
        ----------
        analysis_result : Dict
            Dictionary from SoccerVoronoiAnalyzer.analyze_shot_event()
        
        Returns
        -------
        str
            Formatted prompt for the LLM
        """
        shot_id = analysis_result.get('shot_id', 'Unknown')
        player_areas = analysis_result.get('player_areas', {})
        team_dominance = analysis_result.get('team_dominance', {})
        coverage = analysis_result.get('total_pitch_coverage', 0)
        attacking_third = analysis_result.get('attacking_third_coverage', {})
        
        # Sort players by controlled area
        sorted_players = sorted(player_areas.items(), key=lambda x: x[1], reverse=True)
        
        # Identify players with largest and smallest areas
        largest_areas = sorted_players[:3] if len(sorted_players) >= 3 else sorted_players
        smallest_areas = sorted_players[-3:] if len(sorted_players) >= 3 else sorted_players
        
        # Format player area information
        largest_str = ", ".join([f"{name} ({area:.0f} sq yards)" for name, area in largest_areas])
        smallest_str = ", ".join([f"{name} ({area:.0f} sq yards)" for name, area in smallest_areas])
        
        prompt = f"""Analyze this shot event from a tactical perspective:

SPATIAL DOMINANCE:
- Attacking Team controls {team_dominance.get('Attacking Team', 0):.1f}% of the attacking third
- Defending Team controls {team_dominance.get('Defending Team', 0):.1f}% of the attacking third
- Total pitch coverage: {coverage:.1f}%

PLAYER POSITIONING:
- Players with MOST space (likely isolated or out of position): {largest_str}
- Players with LEAST space (in congested areas): {smallest_str}

ATTACKING THIRD DETAILS:
- Attacking team area: {attacking_third.get('Attacking Team Area', 0):.0f} sq yards
- Defending team area: {attacking_third.get('Defending Team Area', 0):.0f} sq yards

THE PARADOX: Despite the defending team controlling {team_dominance.get('Defending Team', 0):.1f}% of the attacking third, a shot was still taken.

Explain in exactly 4 sentences:
1. Why did the defending team's spatial dominance fail to prevent the shot?
2. Which specific players (based on their area values) were out of position or created exploitable spaces?
3. What tactical lesson can we learn from this spatial distribution?
4. What should the defending team have done differently?"""

        return prompt

    def _call_ibm_granite_langchain(self, prompt: str) -> str:
        """
        Call IBM Granite using langchain_ibm.
        
        Parameters
        ----------
        prompt : str
            The formatted prompt
        
        Returns
        -------
        str
            LLM response
        """
        if not LANGCHAIN_IBM_AVAILABLE:
            raise ImportError("langchain_ibm not installed. Install with: pip install langchain-ibm")
        
        try:
            llm = WatsonxLLM(
                model_id=self.model_id,
                url=self.url,
                apikey=self.api_key,
                project_id=self.project_id,
                params={
                    "max_new_tokens": 300,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 50
                }
            )
            
            full_prompt = f"{self.system_prompt}\n\n{prompt}"
            response = llm.invoke(full_prompt)
            return response
            
        except Exception as e:
            raise RuntimeError(f"Error calling IBM Granite via langchain: {str(e)}")

    def _call_ibm_granite_requests(self, prompt: str) -> str:
        """
        Call IBM Granite using direct REST API with requests.
        
        Parameters
        ----------
        prompt : str
            The formatted prompt
        
        Returns
        -------
        str
            LLM response
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests not installed. Install with: pip install requests")
        
        if not self.api_key or not self.project_id:
            raise ValueError("API key and project ID required for REST API calls")
        
        endpoint = f"{self.url}/ml/v1/text/generation?version=2023-05-29"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        body = {
            "model_id": self.model_id,
            "input": f"{self.system_prompt}\n\n{prompt}",
            "parameters": {
                "max_new_tokens": 300,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 50
            },
            "project_id": self.project_id
        }
        
        try:
            response = requests.post(endpoint, headers=headers, json=body)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get('results', [{}])[0].get('generated_text', '')
            return generated_text
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error calling IBM Granite via REST API: {str(e)}")

    def _generate_mock_explanation(self, analysis_result: Dict) -> str:
        """
        Generate a mock explanation for testing without API access.
        
        Parameters
        ----------
        analysis_result : Dict
            Dictionary from SoccerVoronoiAnalyzer
        
        Returns
        -------
        str
            Mock tactical explanation
        """
        team_dominance = analysis_result.get('team_dominance', {})
        player_areas = analysis_result.get('player_areas', {})
        
        defending_pct = team_dominance.get('Defending Team', 0)
        attacking_pct = team_dominance.get('Attacking Team', 0)
        
        # Find players with extreme areas
        sorted_players = sorted(player_areas.items(), key=lambda x: x[1], reverse=True)
        if not sorted_players:
            return (
                f"Despite controlling {defending_pct:.1f}% of the attacking third, the defending team's spatial dominance did not convert into a clear player-level advantage because the freeze-frame data did not contain enough tracked players to isolate individual positioning patterns. "
                f"That makes the shot more likely to reflect a team structure problem than a single outlier. "
                f"The tactical lesson is that territory alone is not enough if the defense cannot turn it into pressure on the ball carrier and nearby passing lanes."
            )

        largest_player = sorted_players[0][0] if sorted_players else "Unknown"
        smallest_player = sorted_players[-1][0] if sorted_players else "Unknown"
        
        explanation = f"""Despite controlling {defending_pct:.1f}% of the attacking third, the defending team's spatial dominance was undermined by poor individual positioning. {largest_player}'s massive controlled area ({sorted_players[0][1]:.0f} sq yards) indicates they were isolated and out of position, creating a dangerous gap that the attackers exploited. Meanwhile, {smallest_player} was caught in congestion ({sorted_players[-1][1]:.0f} sq yards), suggesting multiple defenders were drawn to the same zone, leaving other areas vulnerable. The lesson is clear: spatial dominance means nothing if players aren't positioned to deny the most dangerous passing lanes and shooting angles."""
        
        return explanation

    def generate_explanation(
        self,
        analysis_result: Dict,
        method: str = "auto"
    ) -> str:
        """
        Generate a tactical explanation from spatial analysis results.
        
        Parameters
        ----------
        analysis_result : Dict
            Dictionary output from SoccerVoronoiAnalyzer.analyze_shot_event()
            Must contain: shot_id, player_areas, team_dominance
        method : str, optional
            Method to use: "auto", "langchain", "requests", or "mock"
            Default "auto" tries langchain, then requests, then mock
        
        Returns
        -------
        str
            Natural language tactical explanation (max 4 sentences)
        
        Examples
        --------
        >>> explainer = TacticalExplainer(use_mock=True)
        >>> result = analyzer.analyze_shot_event(shot_df)
        >>> explanation = explainer.generate_explanation(result)
        >>> print(explanation)
        """
        # Validate input
        required_keys = ['shot_id', 'player_areas', 'team_dominance']
        missing_keys = [k for k in required_keys if k not in analysis_result]
        if missing_keys:
            raise ValueError(f"Missing required keys in analysis_result: {missing_keys}")
        
        # Format the prompt
        prompt = self._format_prompt(analysis_result)
        
        # Use mock if requested or if no API credentials
        if self.use_mock or method == "mock":
            return self._generate_mock_explanation(analysis_result)
        
        # Try different methods based on preference
        if method == "auto":
            # Try langchain first
            if LANGCHAIN_IBM_AVAILABLE and self.api_key and self.project_id:
                try:
                    return self._call_ibm_granite_langchain(prompt)
                except Exception as e:
                    warnings.warn(f"Langchain method failed: {e}. Trying requests...")
            
            # Try requests
            if REQUESTS_AVAILABLE and self.api_key and self.project_id:
                try:
                    return self._call_ibm_granite_requests(prompt)
                except Exception as e:
                    warnings.warn(f"Requests method failed: {e}. Using mock...")
            
            # Fall back to mock
            warnings.warn("No API credentials or methods available. Using mock explanation.")
            return self._generate_mock_explanation(analysis_result)
        
        elif method == "langchain":
            return self._call_ibm_granite_langchain(prompt)
        
        elif method == "requests":
            return self._call_ibm_granite_requests(prompt)
        
        else:
            raise ValueError(f"Unknown method: {method}. Use 'auto', 'langchain', 'requests', or 'mock'")


def main():
    """
    Example usage with mock data from terminal output.
    """
    print("="*70)
    print("TACTICAL EXPLAINER - MOCK EXECUTION")
    print("="*70)
    
    # Mock analysis result from terminal output
    mock_analysis_result = {
        'shot_id': 'shot_1',
        'player_areas': {
            'Player A': 2439.81,
            'Player B': 401.00,
            'Player C': 76.42,
            'Player D': 1478.88,
            'Player E': 1982.02,
            'Player F': 58.75,
            'Player G': 302.28,
            'Player H': 842.27
        },
        'team_dominance': {
            'Attacking Team': 38.26,
            'Defending Team': 61.74
        },
        'total_pitch_coverage': 78.97,
        'attacking_third_coverage': {
            'Attacking Team Area': 1224.26,
            'Defending Team Area': 1975.74,
            'Total Controlled': 3200.0,
            'Attacking Third Total': 3200.0
        }
    }
    
    print("\n[INPUT] Spatial Analysis:")
    print(f"  Shot ID: {mock_analysis_result['shot_id']}")
    print(f"  Attacking Team Dominance: {mock_analysis_result['team_dominance']['Attacking Team']:.2f}%")
    print(f"  Defending Team Dominance: {mock_analysis_result['team_dominance']['Defending Team']:.2f}%")
    print(f"  Pitch Coverage: {mock_analysis_result['total_pitch_coverage']:.2f}%")
    
    print("\n[PLAYERS] Controlled Areas:")
    for player, area in sorted(mock_analysis_result['player_areas'].items(),
                               key=lambda x: x[1], reverse=True):
        print(f"  {player}: {area:.2f} sq yards")
    
    # Initialize explainer in mock mode
    print("\n[AI] Generating Tactical Explanation (Mock Mode)...")
    print("="*70)
    
    explainer = TacticalExplainer(use_mock=True)
    explanation = explainer.generate_explanation(mock_analysis_result)
    
    print("\n[TACTICAL ANALYSIS]")
    print("="*70)
    print(explanation)
    print("="*70)
    
    print("\n[SUCCESS] Mock execution completed successfully!")
    print("\nTo use with real IBM Granite LLM:")
    print("1. Set environment variables:")
    print("   export IBM_API_KEY='your-api-key'")
    print("   export IBM_PROJECT_ID='your-project-id'")
    print("   export IBM_WATSONX_URL='https://us-south.ml.cloud.ibm.com'")
    print("2. Install dependencies:")
    print("   pip install langchain-ibm")
    print("3. Run with use_mock=False:")
    print("   explainer = TacticalExplainer(use_mock=False)")
    print("   explanation = explainer.generate_explanation(result)")


if __name__ == "__main__":
    main()

# Made with Bob
