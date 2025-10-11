# TOPSISX 📊

[![PyPI Version](https://img.shields.io/pypi/v/topsisx.svg)](https://pypi.org/project/topsisx/)
[![Python Version](https://img.shields.io/pypi/pyversions/topsisx.svg)](https://pypi.org/project/topsisx/)
[![Downloads](https://static.pepy.tech/badge/topsisx)](https://pepy.tech/project/topsisx)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/SuvitKumar003/ranklib/blob/main/LICENSE)

**TOPSISX** is a comprehensive Python library for **Multi-Criteria Decision Making (MCDM)** with an intuitive web interface. Make data-driven decisions using proven algorithms like TOPSIS, VIKOR, AHP, and Entropy weighting.

---

## ✨ Features

- 🌐 **Web Interface** - Beautiful, user-friendly Streamlit dashboard
- 📊 **Multiple Methods** - TOPSIS, VIKOR, AHP, Entropy weighting
- 📁 **Easy Input** - CSV upload, sample data, or manual entry
- 📈 **Visualizations** - Interactive charts and rankings
- 📄 **PDF Reports** - Professional report generation
- 💻 **CLI Support** - Command-line interface for automation
- 🎯 **Simple API** - Easy integration into your projects

---

## 🚀 Quick Start

### Installation

```bash
pip install topsisx
```

### Option 1: Web Interface (Recommended)

Launch the interactive web app with a single command:

```bash
topsisx --web
```

This will open a beautiful interface in your browser where you can:
- 📤 Upload your CSV file
- 📋 Use sample datasets
- ✏️ Enter data manually
- 🎨 Configure methods and parameters
- 📊 View results and visualizations
- 💾 Download results

### Option 2: Python API

```python
from topsisx.pipeline import DecisionPipeline
import pandas as pd

# Your data
data = pd.DataFrame({
    'Cost': [250, 200, 300, 275, 225],
    'Quality': [16, 16, 32, 32, 16],
    'Time': [12, 8, 16, 8, 16]
})

# Create pipeline
pipeline = DecisionPipeline(weights='entropy', method='topsis')

# Run analysis
result = pipeline.run(data, impacts=['-', '+', '-'])

print(result)
```

### Option 3: Command Line

```bash
# Basic usage
topsisx data.csv --impacts "+,-,+" --output results.csv

# With specific methods
topsisx data.csv --method vikor --weights entropy --impacts "+,-,+"

# Generate PDF report
topsisx data.csv --impacts "+,-,+" --report
```

---

## 📖 Supported Methods

### 1. TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)

Ranks alternatives based on their distance from ideal and anti-ideal solutions.

```python
from topsisx.topsis import topsis

result = topsis(data, weights=[0.3, 0.3, 0.4], impacts=['+', '-', '+'])
```

**Best for:** General-purpose ranking, balanced decision-making

### 2. VIKOR (Compromise Ranking)

Finds compromise solutions considering both group utility and individual regret.

```python
from topsisx.vikor import vikor

result = vikor(data, weights=[0.3, 0.3, 0.4], impacts=['+', '-', '+'], v=0.5)
```

**Best for:** Conflicting criteria, compromise solutions

### 3. AHP (Analytic Hierarchy Process)

Calculates weights through pairwise comparisons.

```python
from topsisx.ahp import ahp
import pandas as pd

# Pairwise comparison matrix
pairwise = pd.DataFrame([
    [1, 3, 5],
    ['1/3', 1, 4],
    ['1/5', '1/4', 1]
])

weights = ahp(pairwise, verbose=True)
```

**Best for:** Subjective criteria, expert judgments

### 4. Entropy Weighting

Calculates objective weights based on data variance.

```python
from topsisx.entropy import entropy_weights

weights = entropy_weights(data.values)
```

**Best for:** Objective weighting, data-driven decisions

---

## 💡 Usage Examples

### Example 1: Laptop Selection

```python
from topsisx.pipeline import DecisionPipeline
import pandas as pd

# Data
laptops = pd.DataFrame({
    'Model': ['Laptop A', 'Laptop B', 'Laptop C', 'Laptop D'],
    'Price': [800, 1200, 1000, 900],
    'RAM_GB': [8, 16, 16, 8],
    'Battery_Hours': [6, 4, 8, 7],
    'Weight_KG': [2.0, 2.5, 1.8, 2.2]
})

# Analysis
pipeline = DecisionPipeline(weights='entropy', method='topsis')
result = pipeline.run(
    laptops,
    impacts=['-', '+', '+', '-']  # Price and Weight are costs
)

print(result)
```

### Example 2: Supplier Selection with AHP

```python
from topsisx.pipeline import DecisionPipeline
import pandas as pd

# Supplier data
suppliers = pd.DataFrame({
    'Supplier': ['S1', 'S2', 'S3'],
    'Cost': [250, 200, 300],
    'Quality': [16, 16, 32],
    'Delivery': [12, 8, 16]
})

# AHP pairwise matrix (Quality > Cost > Delivery)
ahp_matrix = pd.DataFrame([
    [1, 3, 5],      # Quality
    ['1/3', 1, 3],  # Cost
    ['1/5', '1/3', 1]  # Delivery
])

# Analysis with AHP weights
pipeline = DecisionPipeline(weights='ahp', method='topsis')
result = pipeline.run(
    suppliers,
    impacts=['-', '+', '-'],
    pairwise_matrix=ahp_matrix
)

print(result)
```

### Example 3: Compare Methods

```python
from topsisx.pipeline import DecisionPipeline

pipeline = DecisionPipeline(weights='entropy', method='topsis')

# Compare TOPSIS vs VIKOR
comparison = pipeline.compare_methods(
    data=data,
    impacts=['+', '-', '+']
)

print(comparison['comparison'])
```

---

## 🌐 Web Interface Guide

### Starting the Web App

```bash
topsisx --web
```

### Features:

1. **Data Input Options:**
   - 📤 Upload CSV files
   - 📋 Use pre-loaded sample datasets
   - ✏️ Manual data entry

2. **Configuration:**
   - Choose weighting method (Entropy, AHP, Equal)
   - Select ranking method (TOPSIS, VIKOR)
   - Define impact directions (+/-)
   - Set method parameters

3. **Results:**
   - 📊 Interactive ranking tables
   - 📈 Visual charts and graphs
   - 🥇 Top-3 alternatives highlight
   - 💾 Download results as CSV
   - 📄 Generate PDF reports

---

## 🎯 CLI Reference

### Basic Commands

```bash
# Launch web interface
topsisx --web

# Basic analysis
topsisx data.csv --impacts "+,-,+"

# Specify method and weighting
topsisx data.csv --method vikor --weights equal --impacts "+,-,+"

# With ID column preservation
topsisx data.csv --impacts "+,-,+" --id-col "Model"

# Generate report
topsisx data.csv --impacts "+,-,+" --report

# AHP weighting
topsisx data.csv --weights ahp --ahp-matrix ahp.csv --impacts "+,-,+"

# VIKOR with custom v parameter
topsisx data.csv --method vikor --vikor-v 0.7 --impacts "+,-,+"

# Verbose output
topsisx data.csv --impacts "+,-,+" --verbose
```

### Full Options

```
usage: topsisx [-h] [--web] [--weights {entropy,ahp,equal}] 
               [--method {topsis,vikor}] [--impacts IMPACTS]
               [--ahp-matrix AHP_MATRIX] [--vikor-v VIKOR_V]
               [--output OUTPUT] [--report] [--id-col ID_COL]
               [--verbose] [--version] [input]

Options:
  --web                 Launch web interface
  --weights             Weighting method (default: entropy)
  --method              Decision method (default: topsis)
  --impacts             Impact directions (e.g., '+,-,+')
  --ahp-matrix          Path to AHP pairwise comparison matrix
  --vikor-v             VIKOR strategy weight (0-1, default: 0.5)
  --output              Output CSV file path
  --report              Generate PDF report
  --id-col              ID column to preserve
  --verbose             Show detailed information
```

---

## 📁 Data Format

### CSV Format

Your CSV should have:
- **Rows:** Alternatives/options to rank
- **Columns:** Criteria for evaluation
- **Optional:** ID column (will be preserved)

Example `data.csv`:

```csv
Model,Price,RAM,Battery,Weight
Laptop A,800,8,6,2.0
Laptop B,1200,16,4,2.5
Laptop C,1000,16,8,1.8
Laptop D,900,8,7,2.2
```

### Impact Direction

- `+` : Benefit criterion (higher is better) - e.g., Quality, Speed, RAM
- `-` : Cost criterion (lower is better) - e.g., Price, Time, Weight

---

## 📊 Output Format

Results include original data plus:

**TOPSIS:**
- `Topsis_Score`: Similarity to ideal solution (0-1, higher is better)
- `Rank`: Final ranking (1 is best)

**VIKOR:**
- `S`: Group utility measure
- `R`: Individual regret measure
- `Q`: Compromise ranking index
- `Rank`: Final ranking (1 is best)

---

## 🔧 Advanced Usage

### Custom Pipeline

```python
from topsisx.pipeline import DecisionPipeline

# Create custom pipeline
pipeline = DecisionPipeline(
    weights='entropy',
    method='topsis',
    verbose=True  # Show detailed logs
)

# Run with custom parameters
result = pipeline.run(
    data=df,
    impacts=['+', '-', '+'],
    v=0.7  # VIKOR parameter
)
```

### Generate Reports

```python
from topsisx.reports import generate_report

generate_report(
    result,
    method='topsis',
    filename='my_report.pdf'
)
```

### Batch Processing

```python
import glob
from topsisx.pipeline import DecisionPipeline

pipeline = DecisionPipeline(weights='entropy', method='topsis')

# Process multiple CSV files
for csv_file in glob.glob('data/*.csv'):
    df = pd.read_csv(csv_file)
    result = pipeline.run(df, impacts=['+', '-', '+'])
    result.to_csv(f'results/{csv_file}', index=False)
```

---

## 🎓 Methodology

### TOPSIS Algorithm

1. Normalize decision matrix
2. Apply criteria weights
3. Determine ideal (A+) and anti-ideal (A-) solutions
4. Calculate Euclidean distances to A+ and A-
5. Rank by relative closeness to ideal

### VIKOR Algorithm

1. Determine ideal and anti-ideal values
2. Calculate S (group utility) and R (individual regret)
3. Compute Q values as weighted combination
4. Rank alternatives by Q values

### AHP Process

1. Create pairwise comparison matrix (1-9 scale)
2. Normalize matrix by column sums
3. Calculate priority weights (row averages)
4. Check consistency ratio (CR < 0.1)

### Entropy Weighting

1. Normalize data to probability distribution
2. Calculate entropy for each criterion
3. Derive diversity measure (1 - entropy)
4. Normalize diversity to get weights

---

## 📚 API Reference

### DecisionPipeline

```python
DecisionPipeline(weights='entropy', method='topsis', verbose=False)
```

**Methods:**
- `run(data, impacts, pairwise_matrix=None, **kwargs)` - Run analysis
- `compute_weights(data, pairwise_matrix=None)` - Calculate weights
- `compare_methods(data, impacts, pairwise_matrix=None)` - Compare TOPSIS vs VIKOR

### Individual Methods

```python
topsis(data, weights, impacts) -> DataFrame
vikor(data, weights, impacts, v=0.5) -> DataFrame
ahp(pairwise_matrix, verbose=False) -> ndarray
entropy_weights(matrix) -> ndarray
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Suvit Kumar**
- GitHub: [@SuvitKumar003](https://github.com/SuvitKumar003)
- Email: suvitkumar03@gmail.com

---

## 🙏 Acknowledgments

- Based on established MCDM methodologies
- Built with Python, Pandas, NumPy, Streamlit, and Matplotlib
- Inspired by the need for accessible decision-making tools

---

## 📞 Support

- 📖 [Documentation](https://github.com/SuvitKumar003/ranklib/blob/main/README.md)
- 🐛 [Report Issues](https://github.com/SuvitKumar003/ranklib/issues)
- 💬 [Discussions](https://github.com/SuvitKumar003/ranklib/discussions)

---

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

---

**Made with ❤️ for better decision making**