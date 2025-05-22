# Eurovision Ranking Calculator

A tool to calculate scores for Eurovision prediction competitions based on various scoring systems.

## Features

- **Multiple Scoring Systems**: Implements 7 different scoring systems with varying complexity
- **Standard & Extended Systems**: Choose between systems that only consider the top 10 or also include countries beyond
- **Flexible Data Loading**: Load predictions from CSV files and actual results from text files
- **Tiebreaker Logic**: Multiple tiebreaker criteria that can be easily customized
- **Extensible Design**: Easy to add new scoring systems by inheriting from the base class
- **Detailed Logging**: Generate detailed score breakdowns in a markdown file for analysis
- **Odds-Weighted Bonus**: Optional bonus points for correctly predicting countries not favored by bookmakers

## Scoring Systems

### Standard Systems (Top 10 Only)

These systems only award points for countries that finished in the actual top 10. Countries predicted correctly but finishing beyond the top 10 receive no points.

1. **Simple & Sweet**: Basic scoring with 2 points per correct country and 3 points per exact position
2. **Eurovision Style**: Mimics Eurovision voting (12, 10, 8, 7, ...) for exact position matches
3. **Positional Proximity**: Points based on how close the guess is to the actual position
4. **Top-Heavy Focus**: More points for correctly predicting the Top 3 positions
5. **Top-Heavy Positional Proximity**: Complex system with different point scales based on actual finish tier

### Extended Systems (Beyond Top 10)

These systems also award points for correctly predicting countries that finished beyond the top 10.

6. **Extended Positional Proximity**: Awards points based on proximity to actual position, including for countries beyond the top 10
7. **Modified Top-Heavy Proximity**: A less top-heavy version with base points for top 10 countries, plus points for countries beyond top 10 based on proximity

## Odds-Weighted Bonus

The optional odds-weighted bonus rewards players for correctly predicting countries that bookmakers didn't favor. This adds an extra level of challenge and can reward players who successfully "beat the odds."

- Higher bonus points are awarded for correctly predicting countries with higher odds (less expected to win)
- The bonus is applied to all selected scoring systems
- You can adjust the bonus factor to control how impactful the odds are on the final score

### Adjusting the Odds Factor

The `--odds-factor` argument allows you to control how much impact the odds-based bonus has on the final scores:

- **Default (1.0)**: Standard bonus calculation based on logarithmic scaling of odds
- **Higher values (e.g., 2.0)**: More bonus points for underdogs, making it more rewarding to predict surprise results
- **Lower values (e.g., 0.5)**: Reduced bonus points, making odds less impactful on the final score
- **Zero (0)**: Completely disables the odds bonus, reverting to the base scoring systems

Example effects on scoring with different odds factors:

| Bookmaker Odds | 0.5 Factor | 1.0 Factor | 2.0 Factor |
|----------------|------------|------------|------------|
| 2.0 (favorite) | +0.5 bonus | +1.0 bonus | +2.0 bonus |
| 10.0           | +0.5 bonus | +1.0 bonus | +2.0 bonus |
| 50.0           | +0.8 bonus | +1.7 bonus | +3.4 bonus |
| 200.0 (longshot)| +1.1 bonus | +2.3 bonus | +4.6 bonus |

### Proportional Scaling Across Scoring Systems

The calculator automatically scales the odds bonus proportionally for each scoring system, ensuring a balanced impact across all systems. This means:

- The relative impact of the odds bonus is consistent regardless of which scoring system is used
- Scoring systems with higher point totals have higher scaling factors to maintain proportional bonus impact
- All systems are calibrated so that the odds bonus has a similar relative percentage of the score across all systems

The scaling factors are designed to ensure that systems with higher base scores (like Top-Heavy Positional Proximity with ~130 points) provide proportionally equivalent bonuses to systems with lower base scores (like Top-Heavy Focus with ~45 points).

Current scaling factors (with the default odds factor of 1.0):
- Simple & Sweet: Scaling factor 1.0 (baseline, typical score ~50 points)
- Eurovision Style: Scaling factor 1.4 (typical score ~68 points)
- Positional Proximity: Scaling factor 2.0 (typical score ~100 points)
- Top-Heavy Focus: Scaling factor 0.9 (typical score ~45 points)
- Top-Heavy Positional Proximity: Scaling factor 2.6 (typical score ~130 points)
- Extended Positional Proximity: Scaling factor 2.0
- Modified Top-Heavy Proximity: Scaling factor 2.2

These factors were adjusted from their previous values to ensure a more consistent proportional impact of the odds bonus across all scoring systems.

The detailed log file now correctly displays the odds scaling factor used for each scoring system, making it easy to understand how bonus points were calculated.

## Tiebreakers

1. Most exact positions overall
2. Most exact positions within the actual top 3
3. Early bird submission (earlier timestamp wins)

## Usage

```bash
# Basic usage with manual results
python src/main.py --predictions data/predictions.csv --manual-results Sweden Finland Israel Italy Ukraine France Spain Norway Portugal Lithuania

# Or using a results file
python src/main.py --predictions data/predictions.csv --results data/results.txt

# Specify which scoring systems to calculate
python src/main.py --predictions data/predictions.csv --results data/results.txt --systems "Simple & Sweet" "Eurovision Style"

# Generate a detailed log file with score breakdowns
python src/main.py --predictions data/predictions.csv --results data/results.txt --log-file logs/detailed_breakdown.md

# Use odds-weighted bonus
python src/main.py --predictions data/predictions.csv --results data/results.txt --odds-file data/eurovision_2025_odds.csv

# Adjust the odds bonus factor (higher values = more bonus points)
python src/main.py --predictions data/predictions.csv --results data/results.txt --odds-file data/eurovision_2025_odds.csv --odds-factor 2.0
```

### Command Line Options

- `--predictions` or `-p`: Path to the CSV file with participant predictions (required)
- `--results` or `-r`: Path to the file with actual results
- `--manual-results` or `-m`: Manually specify the actual results as a list of countries
- `--systems` or `-s`: Choose which scoring systems to use (any combination of the available systems)
- `--log-file` or `-l`: Generate a detailed log file with score breakdowns for each participant
- `--odds-file` or `-o`: Path to CSV file with bookmaker odds for calculating bonus points
- `--odds-factor` or `-f`: Multiplier for odds-based bonus points (default: 1.0). Increase for more emphasis on underdog predictions, decrease for less impact.
- `--json` or `-j`: Generate a JSON file with all data for analysis (enabled by default)
- `--no-json`: Disable JSON file generation
- `--json-dir`: Directory to store the generated JSON file (default: data)

## Detailed Score Breakdown

The log file generated with the `--log-file` option provides comprehensive details about how scores were calculated for each participant in each scoring system. The log file includes:

- The official Eurovision results
- Bookmaker odds (if available)
- Rankings for each scoring system
- A breakdown of each participant's points for every country they predicted
- A detailed explanation of how each point was awarded, including odds-based bonus points
- A summary of correct predictions and their point values
- Machine-readable JSON data for further analysis

### Example log file excerpt:

```markdown
# Eurovision Prediction Contest - Detailed Score Breakdown

## Bookmaker Odds

| Rank | Country | Median Odds |
|------|---------|-------------|
| 1 | Sweden | 1.91 |
| 2 | Austria | 3.80 |
| 3 | France | 8.00 |
...

## Actual Results

1. Sweden
2. Finland
3. Israel
...

## Scoring System: Simple & Sweet

### 1. Thomas - 18 points

Base Score: 12 points + Odds Bonus: 6 points = 18 total points
(Odds scaling factor for this scoring system: 1.00)

#### Prediction vs Actual

| Position | Prediction | Actual | Points | Explanation |
|----------|------------|--------|--------|--------------|
| 1 | Sweden | Sweden | 5 | +2 points (in top 10), +3 points (exact position), +1.0 bonus (odds: 1.91, scaling: 1.00) |
| 2 | Finland | Not in Top 10 | 0 | No points |
| 10 | Malta | Not in Top 10 | 0 | No points |
...

## Scoring System: Extended Positional Proximity

### 1. Thomas - 37 points

#### Prediction vs Actual

| Position | Prediction | Actual | Points | Explanation |
|----------|------------|--------|--------|--------------|
| 1 | Sweden | Sweden (4) | 3 | +3 points (off by 3 positions) |
| 2 | Finland | Finland (11) | 5 | +5 points (off by 2 positions), (country finished at position 11) |
...
```

In this example, note how "Standard" systems like "Simple & Sweet" only award points for countries in the top 10, while "Extended" systems like "Extended Positional Proximity" also award points for countries like Finland that finished outside the top 10 (at position 11).

## Odds CSV Format

The odds CSV file should have the following format: