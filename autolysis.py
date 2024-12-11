import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from openai import OpenAI  # Assuming you have an OpenAI-like client for GPT-4o-Mini
import sys

# Load environment variable
API_TOKEN = os.getenv("AIPROXY_TOKEN")

# Function to read CSV
def read_csv(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

# Function to perform basic analysis
def analyze_data(data):
    analysis = {
        "shape": data.shape,
        "missing_values": data.isnull().sum().to_dict(),
        "summary_stats": data.describe().to_dict(),
        "column_types": data.dtypes.to_dict(),
    }
    return analysis

# Function to create visualizations
def create_visualizations(data, output_folder):
    charts = []
    if len(data.columns) > 1:  # Correlation heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(data.corr(), annot=True, cmap='coolwarm')
        heatmap_path = os.path.join(output_folder, 'correlation_heatmap.png')
        plt.savefig(heatmap_path)
        charts.append(heatmap_path)
        plt.close()
    # Add more visualizations here
    return charts

# Function to interact with GPT-4o-Mini
def query_gpt(summary):
    # Pseudocode for querying GPT
    # Replace with actual API call
    response = OpenAI(API_TOKEN).ask(summary)
    return response

# Function to write README.md
def write_markdown(summary, insights, charts, output_folder):
    readme_path = os.path.join(output_folder, "README.md")
    with open(readme_path, "w") as f:
        f.write(f"# Analysis Summary\n\n{summary}\n\n")
        f.write("## Key Insights\n\n")
        f.write("\n".join([f"- {insight}" for insight in insights]))
        f.write("\n\n## Visualizations\n\n")
        for chart in charts:
            f.write(f"![Chart]({chart})\n\n")
    return readme_path

# Main workflow
def main():
    if len(sys.argv) < 2:
        print("Usage: python autolysis.py <csv_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    dataset_name = os.path.splitext(os.path.basename(file_path))[0]
    output_folder = os.path.join(".", dataset_name)
    os.makedirs(output_folder, exist_ok=True)

    data = read_csv(file_path)
    analysis = analyze_data(data)
    charts = create_visualizations(data, output_folder)

    summary_prompt = f"Dataset columns: {list(analysis['column_types'].keys())}\n" \
                     f"Summary Stats: {analysis['summary_stats']}\n" \
                     f"Missing Values: {analysis['missing_values']}\n" \
                     f"What insights and recommendations can you suggest?"
    summary = query_gpt(summary_prompt)

    write_markdown(summary, summary.get("insights", []), charts, output_folder)
    print(f"Results saved in {output_folder}")

if __name__ == "__main__":
    main()
