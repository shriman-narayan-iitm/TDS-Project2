# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
#   "matplotlib",
#   "seaborn",
#   "openai",
#   "chardet"
# ]
# ///

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openai
import chardet

# Function to detect and load CSV with proper encoding
def load_csv_with_encoding(file_path):
    try:
        # Detect the file encoding
        with open(file_path, 'rb') as file:
            detected_encoding = chardet.detect(file.read())['encoding']

        # Load the CSV with the detected encoding
        data = pd.read_csv(file_path, encoding=detected_encoding)
        print(f"File loaded successfully with encoding: {detected_encoding}")
        return data
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        sys.exit(1)

# Initialize OpenAI with the API Proxy Token
def initialize_openai():
    api_token ='eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDU1OTdAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.mGtFocaNamOEpoh3Y6WUB-xoAJJzW3EQntzLwbHUSXg'
    if not api_token:
        print("Error: AIPROXY_TOKEN environment variable is not set.")
        sys.exit(1)
    openai.api_base = "https://aiproxy.sanand.workers.dev/"
    openai.api_key = api_token

# Generate visualizations
def generate_visualizations(data, output_prefix):
    try:
        # Example visualization: Correlation heatmap
        correlation_matrix = data.corr(numeric_only=True)
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f")
        heatmap_file = f"{output_prefix}_correlation_heatmap.png"
        plt.savefig(heatmap_file)
        plt.close()
        print(f"Saved heatmap to {heatmap_file}")
        return [heatmap_file]
    except Exception as e:
        print(f"Error generating visualizations: {e}")
        return []

# Analyze data with GPT-4o-Mini
def analyze_with_llm(data, filename):
    try:
        prompt = f"""You are analyzing a dataset named {filename}. Here are the column names and their data types:\n\n"""
        prompt += "\n".join([f"{col}: {dtype}" for col, dtype in zip(data.columns, data.dtypes)])
        prompt += "\n\nProvide insights and recommendations based on the data."  # Example prompt

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a data analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error during LLM analysis: {e}")
        return ""

# Main script
def main():
    if len(sys.argv) != 2:
        print("Usage: uv run autolysis.py <dataset.csv>")
        sys.exit(1)

    csv_file = sys.argv[1]

    # Step 1: Load the CSV file
    data = load_csv_with_encoding(csv_file)

    # Step 2: Initialize OpenAI
    initialize_openai()

    # Step 3: Perform analysis with GPT-4o-Mini
    analysis_result = analyze_with_llm(data, csv_file)

    # Step 4: Generate visualizations
    visualizations = generate_visualizations(data, "analysis")

    # Step 5: Write results to README.md
    try:
        with open("README.md", "w") as readme:
            readme.write(f"# Analysis of {csv_file}\n\n")
            readme.write("## Insights\n\n")
            readme.write(analysis_result + "\n\n")
            readme.write("## Visualizations\n\n")
            for viz in visualizations:
                readme.write(f"![{viz}]({viz})\n")
        print("Saved analysis to README.md")
    except Exception as e:
        print(f"Error writing README.md: {e}")

if __name__ == "__main__":
    main()
