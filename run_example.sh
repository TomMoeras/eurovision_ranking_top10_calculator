#!/bin/bash

# Create sample results
python src/create_sample_results.py

# Run calculator using all scoring systems (default)
echo "===== Running with all scoring systems ====="
python src/main.py --predictions "data/Top 10 Eurovision 2025_ (Responses) - Form responses 1.csv" --results data/sample_results.txt

# Run with just two specific scoring systems and generate a log file
echo -e "\n\n===== Running with scoring systems and generating detailed log ====="
python src/main.py --predictions "data/Top 10 Eurovision 2025_ (Responses) - Form responses 1.csv" --results data/sample_results.txt --systems "Simple & Sweet" "Eurovision Style" --log-file "logs/detailed_score_breakdown.md"

# Let the user know the log file location
if [ -f logs/detailed_score_breakdown.md ]; then
    echo -e "\nDetailed score breakdown written to logs/detailed_score_breakdown.md"
fi 