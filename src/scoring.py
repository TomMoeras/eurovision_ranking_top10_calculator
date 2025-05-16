from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Set, Any, Optional


class ScoringSystem(ABC):
    """Base class for all Eurovision scoring systems"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.odds_calculator = None  # Will be set if odds bonus is enabled
        self.odds_scaling_factor = 1.0  # Standard baseline scaling
    
    def set_odds_calculator(self, odds_calculator) -> None:
        """Set the odds calculator for bonus calculations
        
        Args:
            odds_calculator: OddsCalculator instance
        """
        self.odds_calculator = odds_calculator
    
    @abstractmethod
    def calculate_score(self, prediction: List[str], actual_results: List[str]) -> int:
        """Calculate score based on prediction and actual results
        
        Args:
            prediction: List of countries in predicted order (1st to 10th)
            actual_results: List of countries in actual order (1st to 10th)
            
        Returns:
            The score as an integer
        """
        pass
    
    def calculate_score_with_odds_bonus(self, prediction: List[str], actual_results: List[str]) -> int:
        """Calculate score with odds-weighted bonus
        
        Args:
            prediction: List of countries in predicted order (1st to 10th)
            actual_results: List of countries in actual order (1st to 10th)
            
        Returns:
            The score with odds bonus
        """
        # Get base score
        base_score = self.calculate_score(prediction, actual_results)
        
        # Apply odds bonus if enabled
        if self.odds_calculator:
            return self.odds_calculator.apply_bonus_to_score(
                prediction, 
                actual_results, 
                base_score,
                self.odds_scaling_factor
            )
        
        return base_score
    
    def get_detailed_breakdown(self, prediction: List[str], actual_results: List[str]) -> Dict[str, Any]:
        """Get a detailed breakdown of the score calculation
        
        Args:
            prediction: List of countries in predicted order (1st to 10th)
            actual_results: List of countries in actual order (1st to 10th)
            
        Returns:
            Dictionary with detailed breakdown information
        """
        # Default implementation - subclasses should override for more specific breakdowns
        base_score = self.calculate_score(prediction, actual_results)
        total_score = base_score
        odds_bonus = 0
        odds_details = {}
        
        if self.odds_calculator:
            correct_countries = self.get_correct_countries(prediction, actual_results)
            total_score = self.odds_calculator.apply_bonus_to_score(
                prediction, 
                actual_results, 
                base_score,
                self.odds_scaling_factor
            )
            odds_bonus = total_score - base_score
            
            # Get detailed bonus for each correct country
            for country in correct_countries:
                bonus = self.odds_calculator.calculate_scaled_bonus(
                    country, 
                    self.odds_scaling_factor
                )
                odds = self.odds_calculator.country_odds.get(country, 0)
                odds_details[country] = {
                    "odds": odds,
                    "bonus": bonus
                }
        
        return {
            "system": self.name,
            "description": self.description,
            "total_score": total_score,
            "base_score": base_score,
            "odds_bonus": odds_bonus,
            "odds_scaling_factor": self.odds_scaling_factor,
            "odds_details": odds_details,
            "prediction": prediction,
            "actual_results": actual_results,
            "details": "No detailed breakdown available for this scoring system."
        }
    
    def get_correct_countries(self, prediction: List[str], actual_results: List[str]) -> Set[str]:
        """Get the set of correctly predicted countries (regardless of position)"""
        return set(prediction) & set(actual_results)
    
    def get_exact_positions(self, prediction: List[str], actual_results: List[str]) -> List[int]:
        """Get a list of positions (0-indexed) that were predicted exactly"""
        return [i for i in range(len(prediction)) if prediction[i] == actual_results[i]]


class SimpleAndSweet(ScoringSystem):
    """System 1: Simple & Sweet
    
    - Correct Country in Top 10: +2 points for each country in the actual Top 10
    - Exact Position Bonus: +3 additional points for each exact position match
    """
    
    def __init__(self):
        super().__init__(
            "Simple & Sweet",
            "2 points per correct country + 3 points per exact position"
        )
        # Typical perfect score is around 50 points, use as baseline
        self.odds_scaling_factor = 1.0  # Standard baseline scaling
    
    def calculate_score(self, prediction: List[str], actual_results: List[str]) -> int:
        # Points for correct countries
        correct_countries = self.get_correct_countries(prediction, actual_results)
        country_points = len(correct_countries) * 2
        
        # Points for exact positions
        exact_positions = self.get_exact_positions(prediction, actual_results)
        position_points = len(exact_positions) * 3
        
        return country_points + position_points
    
    def get_detailed_breakdown(self, prediction: List[str], actual_results: List[str]) -> Dict[str, Any]:
        # Get correct countries and positions
        correct_countries = self.get_correct_countries(prediction, actual_results)
        exact_positions = self.get_exact_positions(prediction, actual_results)
        
        # Calculate points
        country_points = len(correct_countries) * 2
        position_points = len(exact_positions) * 3
        base_score = country_points + position_points
        
        # Apply odds bonus if enabled
        total_score = base_score
        odds_bonus = 0
        odds_details = {}
        
        if self.odds_calculator:
            total_score = self.odds_calculator.apply_bonus_to_score(
                prediction, 
                actual_results, 
                base_score,
                self.odds_scaling_factor
            )
            odds_bonus = total_score - base_score
            
            # Get detailed bonus for each correct country
            for country in correct_countries:
                bonus = self.odds_calculator.calculate_scaled_bonus(
                    country, 
                    self.odds_scaling_factor
                )
                odds = self.odds_calculator.country_odds.get(country, 0)
                odds_details[country] = {
                    "odds": odds,
                    "bonus": bonus
                }
        
        # Create a lookup for actual positions
        actual_positions = {country: i for i, country in enumerate(actual_results)}
        
        # Create detailed breakdown
        country_details = []
        for i, country in enumerate(prediction):
            in_top10 = country in actual_results
            exact_match = i in exact_positions
            points = 0
            explanation = []
            
            if in_top10:
                points += 2
                explanation.append("+2 points (in top 10)")
                
                if exact_match:
                    points += 3
                    explanation.append("+3 points (exact position)")
                
                # Add odds bonus explanation if applicable
                if self.odds_calculator and country in odds_details:
                    country_bonus = odds_details[country]["bonus"]
                    country_odds = odds_details[country]["odds"]
                    if country_bonus > 0:
                        explanation.append(f"+{country_bonus:.1f} bonus (odds: {country_odds:.1f}, scaling: {self.odds_scaling_factor:.2f})")
            
            country_details.append({
                "position": i + 1,
                "country": country,
                "in_top10": in_top10,
                "exact_match": exact_match,
                "actual_position": actual_positions.get(country, "Not in Top 10"),
                "points": points,
                "explanation": ", ".join(explanation) if explanation else "No points"
            })
        
        return {
            "system": self.name,
            "description": self.description,
            "total_score": total_score,
            "base_score": base_score,
            "correct_countries": len(correct_countries),
            "correct_country_points": country_points,
            "exact_positions": len(exact_positions),
            "exact_position_points": position_points,
            "odds_bonus": odds_bonus,
            "odds_scaling_factor": self.odds_scaling_factor,
            "odds_details": odds_details,
            "country_details": country_details
        }


class EurovisionStyle(ScoringSystem):
    """System 3: Eurovision Style Points
    
    Mimics Eurovision voting for exact position guesses:
    - 1st place: +12 points
    - 2nd place: +10 points
    - 3rd place: +8 points
    - 4th place: +7 points
    - ...
    - 10th place: +1 point
    - Optional: +1 point for correct country in wrong position
    """
    
    def __init__(self, bonus_for_correct_country: bool = True):
        super().__init__(
            "Eurovision Style",
            "12, 10, 8, 7, 6, 5, 4, 3, 2, 1 points for exact positions"
        )
        self.position_points = [12, 10, 8, 7, 6, 5, 4, 3, 2, 1]
        self.bonus_for_correct_country = bonus_for_correct_country
        # Typical perfect score is around 68 points, scale to match baseline
        self.odds_scaling_factor = 1.4  # Adjusted from 0.5
    
    def calculate_score(self, prediction: List[str], actual_results: List[str]) -> int:
        score = 0
        
        # Points for exact positions
        for i in range(len(prediction)):
            if prediction[i] == actual_results[i]:
                score += self.position_points[i]
        
        # Optional bonus for correct countries in wrong positions
        if self.bonus_for_correct_country:
            correct_countries = self.get_correct_countries(prediction, actual_results)
            exact_positions = self.get_exact_positions(prediction, actual_results)
            bonus_countries = len(correct_countries) - len(exact_positions)
            score += bonus_countries * 1
        
        return score
    
    def get_detailed_breakdown(self, prediction: List[str], actual_results: List[str]) -> Dict[str, Any]:
        # Get correct countries and positions
        correct_countries = self.get_correct_countries(prediction, actual_results)
        exact_positions = self.get_exact_positions(prediction, actual_results)
        
        # Calculate points
        position_points = 0
        for i in exact_positions:
            position_points += self.position_points[i]
        
        bonus_countries = len(correct_countries) - len(exact_positions)
        bonus_points = bonus_countries * 1 if self.bonus_for_correct_country else 0
        base_score = position_points + bonus_points
        
        # Apply odds bonus if enabled
        total_score = base_score
        odds_bonus = 0
        odds_details = {}
        
        if self.odds_calculator:
            total_score = self.odds_calculator.apply_bonus_to_score(
                prediction, 
                actual_results, 
                base_score,
                self.odds_scaling_factor
            )
            odds_bonus = total_score - base_score
            
            # Get detailed bonus for each correct country
            for country in correct_countries:
                bonus = self.odds_calculator.calculate_scaled_bonus(
                    country, 
                    self.odds_scaling_factor
                )
                odds = self.odds_calculator.country_odds.get(country, 0)
                odds_details[country] = {
                    "odds": odds,
                    "bonus": bonus
                }
        
        # Create a lookup for actual positions
        actual_positions = {country: i for i, country in enumerate(actual_results)}
        
        # Create detailed breakdown
        country_details = []
        for i, country in enumerate(prediction):
            in_top10 = country in actual_results
            exact_match = i in exact_positions
            points = 0
            explanation = []
            
            if exact_match:
                points += self.position_points[i]
                explanation.append(f"+{self.position_points[i]} points (exact position)")
            elif in_top10 and self.bonus_for_correct_country:
                points += 1
                explanation.append("+1 point (in top 10 but wrong position)")
            
            # Add odds bonus explanation if applicable
            if self.odds_calculator and country in odds_details:
                country_bonus = odds_details[country]["bonus"]
                country_odds = odds_details[country]["odds"]
                if country_bonus > 0:
                    explanation.append(f"+{country_bonus:.1f} bonus (odds: {country_odds:.1f}, scaling: {self.odds_scaling_factor:.2f})")
            
            country_details.append({
                "position": i + 1,
                "country": country,
                "in_top10": in_top10,
                "exact_match": exact_match,
                "actual_position": actual_positions.get(country, "Not in Top 10"),
                "points": points,
                "explanation": ", ".join(explanation) if explanation else "No points"
            })
        
        return {
            "system": self.name,
            "description": self.description,
            "total_score": total_score,
            "base_score": base_score,
            "position_points": position_points,
            "bonus_for_correct_country": self.bonus_for_correct_country,
            "bonus_countries": bonus_countries,
            "bonus_points": bonus_points,
            "odds_bonus": odds_bonus,
            "odds_scaling_factor": self.odds_scaling_factor,
            "odds_details": odds_details,
            "country_details": country_details
        }


class PositionalProximity(ScoringSystem):
    """System 4: Positional Proximity
    
    For each country correctly identified in Top 10:
    - Exact Position: +10 points
    - Off by 1 Position: +7 points
    - Off by 2 Positions: +5 points
    - Off by 3 Positions: +3 points
    - Off by 4+ Positions (but still in Top 10): +1 point
    """
    
    def __init__(self):
        super().__init__(
            "Positional Proximity",
            "Points based on how close the prediction is to actual position"
        )
        self.proximity_points = {
            0: 10,  # Exact position
            1: 7,   # Off by 1
            2: 5,   # Off by 2
            3: 3,   # Off by 3
            4: 1,   # Off by 4+
            5: 1,
            6: 1,
            7: 1,
            8: 1,
            9: 1
        }
        # Typical perfect score is around 100 points, scale to match baseline
        self.odds_scaling_factor = 2.0  # Adjusted from 0.3
    
    def calculate_score(self, prediction: List[str], actual_results: List[str]) -> int:
        score = 0
        # Create a lookup for actual positions
        actual_positions = {country: i for i, country in enumerate(actual_results)}
        
        # Check each predicted country
        for pred_pos, country in enumerate(prediction):
            if country in actual_positions:
                # Country is in the top 10
                actual_pos = actual_positions[country]
                difference = abs(pred_pos - actual_pos)
                score += self.proximity_points.get(difference, 1)  # Default to 1 for 4+ difference
        
        return score
    
    def get_detailed_breakdown(self, prediction: List[str], actual_results: List[str]) -> Dict[str, Any]:
        # Create a lookup for actual positions
        actual_positions = {country: i for i, country in enumerate(actual_results)}
        
        # Calculate points and create detailed breakdown
        base_score = 0
        country_details = []
        correct_countries = self.get_correct_countries(prediction, actual_results)
        
        for pred_pos, country in enumerate(prediction):
            in_top10 = country in actual_positions
            points = 0
            explanation = []
            difference = None
            
            if in_top10:
                actual_pos = actual_positions[country]
                difference = abs(pred_pos - actual_pos)
                points = self.proximity_points.get(difference, 1)
                base_score += points
                
                if difference == 0:
                    explanation.append(f"+{points} points (exact position)")
                else:
                    explanation.append(f"+{points} points (off by {difference} position{'s' if difference > 1 else ''})")
            
            country_details.append({
                "position": pred_pos + 1,
                "country": country,
                "in_top10": in_top10,
                "actual_position": actual_positions.get(country, "Not in Top 10"),
                "position_difference": difference,
                "points": points,
                "explanation": ", ".join(explanation) if explanation else "No points"
            })
        
        # Apply odds bonus if enabled
        total_score = base_score
        odds_bonus = 0
        odds_details = {}
        
        if self.odds_calculator:
            total_score = self.odds_calculator.apply_bonus_to_score(
                prediction, 
                actual_results, 
                base_score,
                self.odds_scaling_factor
            )
            odds_bonus = total_score - base_score
            
            # Get detailed bonus for each correct country
            for country in correct_countries:
                bonus = self.odds_calculator.calculate_scaled_bonus(
                    country, 
                    self.odds_scaling_factor
                )
                odds = self.odds_calculator.country_odds.get(country, 0)
                odds_details[country] = {
                    "odds": odds,
                    "bonus": bonus
                }
                
                # Add odds bonus explanation to country details
                for detail in country_details:
                    if detail["country"] == country and detail["in_top10"]:
                        country_bonus = odds_details[country]["bonus"]
                        country_odds = odds_details[country]["odds"]
                        if country_bonus > 0:
                            detail["explanation"] += f", +{country_bonus:.1f} bonus (odds: {country_odds:.1f}, scaling: {self.odds_scaling_factor:.2f})"
        
        return {
            "system": self.name,
            "description": self.description,
            "total_score": total_score,
            "base_score": base_score,
            "proximity_points_scale": self.proximity_points,
            "odds_bonus": odds_bonus,
            "odds_scaling_factor": self.odds_scaling_factor,
            "odds_details": odds_details,
            "country_details": country_details
        }


class TopHeavyFocus(ScoringSystem):
    """System 6: Top-Heavy Focus
    
    - Correct Country in Top 10 (positions 4-10): +1 point
    - Correct Country in Top 3 (positions 1-3): +3 points
    - Bonus for Exact Position (positions 4-10): +2 additional points
    - Bonus for Exact Position (positions 1-3): +5 additional points
    """
    
    def __init__(self):
        super().__init__(
            "Top-Heavy Focus",
            "More points for top 3 positions"
        )
        # Typical perfect score is around 45 points, scale to match baseline
        self.odds_scaling_factor = 0.9  # Adjusted from 1.11 (50/45)
    
    def calculate_score(self, prediction: List[str], actual_results: List[str]) -> int:
        score = 0
        # Create a lookup for actual positions
        actual_positions = {country: i for i, country in enumerate(actual_results)}
        
        # Check each predicted country
        for pred_pos, country in enumerate(prediction):
            if country in actual_positions:
                actual_pos = actual_positions[country]
                
                # Base points for correct country
                if actual_pos < 3:  # Top 3
                    score += 3
                else:  # Positions 4-10
                    score += 1
                
                # Bonus for exact position
                if pred_pos == actual_pos:
                    if actual_pos < 3:  # Top 3
                        score += 5
                    else:  # Positions 4-10
                        score += 2
        
        return score
    
    def get_detailed_breakdown(self, prediction: List[str], actual_results: List[str]) -> Dict[str, Any]:
        # Create a lookup for actual positions
        actual_positions = {country: i for i, country in enumerate(actual_results)}
        
        # Calculate points and create detailed breakdown
        base_score = 0
        country_details = []
        correct_countries = self.get_correct_countries(prediction, actual_results)
        
        for pred_pos, country in enumerate(prediction):
            in_top10 = country in actual_positions
            points = 0
            explanation = []
            
            if in_top10:
                actual_pos = actual_positions[country]
                exact_match = pred_pos == actual_pos
                
                # Base points for correct country
                if actual_pos < 3:  # Top 3
                    points += 3
                    explanation.append("+3 points (country in top 3)")
                else:  # Positions 4-10
                    points += 1
                    explanation.append("+1 point (country in positions 4-10)")
                
                # Bonus for exact position
                if exact_match:
                    if actual_pos < 3:  # Top 3
                        points += 5
                        explanation.append("+5 points (exact position in top 3)")
                    else:  # Positions 4-10
                        points += 2
                        explanation.append("+2 points (exact position in 4-10)")
                
                base_score += points
            
            country_details.append({
                "position": pred_pos + 1,
                "country": country,
                "in_top10": in_top10,
                "actual_position": actual_positions.get(country, "Not in Top 10"),
                "exact_match": pred_pos == actual_positions.get(country, -1) if in_top10 else False,
                "points": points,
                "explanation": ", ".join(explanation) if explanation else "No points"
            })
        
        # Apply odds bonus if enabled
        total_score = base_score
        odds_bonus = 0
        odds_details = {}
        
        if self.odds_calculator:
            total_score = self.odds_calculator.apply_bonus_to_score(
                prediction, 
                actual_results, 
                base_score,
                self.odds_scaling_factor
            )
            odds_bonus = total_score - base_score
            
            # Get detailed bonus for each correct country
            for country in correct_countries:
                bonus = self.odds_calculator.calculate_scaled_bonus(
                    country, 
                    self.odds_scaling_factor
                )
                odds = self.odds_calculator.country_odds.get(country, 0)
                odds_details[country] = {
                    "odds": odds,
                    "bonus": bonus
                }
                
                # Add odds bonus explanation to country details
                for detail in country_details:
                    if detail["country"] == country and detail["in_top10"]:
                        country_bonus = odds_details[country]["bonus"]
                        country_odds = odds_details[country]["odds"]
                        if country_bonus > 0:
                            detail["explanation"] += f", +{country_bonus:.1f} bonus (odds: {country_odds:.1f}, scaling: {self.odds_scaling_factor:.2f})"
        
        return {
            "system": self.name,
            "description": self.description,
            "total_score": total_score,
            "base_score": base_score,
            "odds_bonus": odds_bonus,
            "odds_scaling_factor": self.odds_scaling_factor,
            "odds_details": odds_details,
            "country_details": country_details
        }


class TopHeavyPositionalProximity(ScoringSystem):
    """System 7: Top-Heavy Positional Proximity
    
    Different point scales based on actual position tier (Top 3 vs Ranks 4-10)
    and proximity of guess to actual position.
    """
    
    def __init__(self):
        super().__init__(
            "Top-Heavy Positional Proximity",
            "Different proximity scales for Top 3 vs Positions 4-10"
        )
        # Points for countries that actually finished in Top 3
        self.top3_points = {
            0: 20,  # Exact position
            1: 16,  # Off by 1
            2: 12,  # Off by 2
            3: 8,   # Off by 3
            4: 5,   # Off by 4-6
            5: 5,
            6: 5,
            7: 2,   # Off by 7-9
            8: 2,
            9: 2
        }
        
        # Points for countries that finished in positions 4-10
        self.lower_points = {
            0: 10,  # Exact position
            1: 7,   # Off by 1
            2: 5,   # Off by 2
            3: 3,   # Off by 3
            4: 1,   # Off by 4+
            5: 1,
            6: 1,
            7: 1,
            8: 1,
            9: 1
        }
        
        # Typical perfect score is around 130 points, scale to match baseline
        self.odds_scaling_factor = 2.6  # Adjusted from 0.38 (50/130)
    
    def calculate_score(self, prediction: List[str], actual_results: List[str]) -> int:
        score = 0
        # Create a lookup for actual positions
        actual_positions = {country: i for i, country in enumerate(actual_results)}
        
        # Check each predicted country
        for pred_pos, country in enumerate(prediction):
            if country in actual_positions:
                actual_pos = actual_positions[country]
                difference = abs(pred_pos - actual_pos)
                
                # Use appropriate point scale based on actual position
                if actual_pos < 3:  # Top 3
                    score += self.top3_points.get(difference, 2)  # Default to 2 for large differences
                else:  # Positions 4-10
                    score += self.lower_points.get(difference, 1)  # Default to 1 for large differences
        
        return score
    
    def get_detailed_breakdown(self, prediction: List[str], actual_results: List[str]) -> Dict[str, Any]:
        # Create a lookup for actual positions
        actual_positions = {country: i for i, country in enumerate(actual_results)}
        
        # Calculate points and create detailed breakdown
        base_score = 0
        country_details = []
        correct_countries = self.get_correct_countries(prediction, actual_results)
        
        for pred_pos, country in enumerate(prediction):
            in_top10 = country in actual_positions
            points = 0
            explanation = []
            
            if in_top10:
                actual_pos = actual_positions[country]
                difference = abs(pred_pos - actual_pos)
                
                # Use appropriate point scale based on actual position
                if actual_pos < 3:  # Top 3
                    points = self.top3_points.get(difference, 2)  # Default to 2 for large differences
                    tier = "top 3"
                else:  # Positions 4-10
                    points = self.lower_points.get(difference, 1)  # Default to 1 for large differences
                    tier = "positions 4-10"
                
                base_score += points
                
                if difference == 0:
                    explanation.append(f"+{points} points (exact position in {tier})")
                else:
                    explanation.append(f"+{points} points (off by {difference} position{'s' if difference > 1 else ''} in {tier})")
            
            country_details.append({
                "position": pred_pos + 1,
                "country": country,
                "in_top10": in_top10,
                "actual_position": actual_positions.get(country, "Not in Top 10"),
                "position_difference": abs(pred_pos - actual_positions[country]) if in_top10 else None,
                "points": points,
                "explanation": ", ".join(explanation) if explanation else "No points"
            })
        
        # Apply odds bonus if enabled
        total_score = base_score
        odds_bonus = 0
        odds_details = {}
        
        if self.odds_calculator:
            total_score = self.odds_calculator.apply_bonus_to_score(
                prediction, 
                actual_results, 
                base_score,
                self.odds_scaling_factor
            )
            odds_bonus = total_score - base_score
            
            # Get detailed bonus for each correct country
            for country in correct_countries:
                bonus = self.odds_calculator.calculate_scaled_bonus(
                    country, 
                    self.odds_scaling_factor
                )
                odds = self.odds_calculator.country_odds.get(country, 0)
                odds_details[country] = {
                    "odds": odds,
                    "bonus": bonus
                }
                
                # Add odds bonus explanation to country details
                for detail in country_details:
                    if detail["country"] == country and detail["in_top10"]:
                        country_bonus = odds_details[country]["bonus"]
                        country_odds = odds_details[country]["odds"]
                        if country_bonus > 0:
                            detail["explanation"] += f", +{country_bonus:.1f} bonus (odds: {country_odds:.1f}, scaling: {self.odds_scaling_factor:.2f})"
        
        return {
            "system": self.name,
            "description": self.description,
            "total_score": total_score,
            "base_score": base_score,
            "top3_points_scale": self.top3_points,
            "lower_points_scale": self.lower_points,
            "odds_bonus": odds_bonus,
            "odds_scaling_factor": self.odds_scaling_factor,
            "odds_details": odds_details,
            "country_details": country_details
        } 