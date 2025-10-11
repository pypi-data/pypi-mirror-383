# 🧠 Universal ML Model Explorer Pro

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Cross--Platform-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)
![Maintained](https://img.shields.io/badge/Maintained%3F-Yes-blue)
![Status](https://img.shields.io/badge/Status-Active-success)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen)
![Downloads](https://img.shields.io/badge/dynamic/json?url=https://pypistats.org/api/packages/lazybrains/recent&label=Downloads&query=%24.data.last_month&suffix=%2Fmonth&color=orange)

> One-line ML pipeline that preprocesses, trains, compares, and visualizes the best model — automatically.


Automatically train, evaluate, compare, and visualize multiple machine learning models — all with one command.

## 🚀 Features

* Auto detection: Classification or Regression
* Auto preprocessing: Scaling, Encoding, Imputation, PCA
* Parallel model training on all cores
* SHAP interpretability plots
* Beautiful visual reports (Confusion Matrix, ROC, Residuals, etc.)
* CLI + Notebook compatible

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🧪 CLI Usage

```bash
python main.py path/to/dataset.csv target_column_name
```

### Optional flags:

* `--output_dir`: Folder to save results (default: `results`)
* `--pca_components`: Apply PCA on numeric features
* `--no_shap`: Disable SHAP plot (faster)

## 🧬 Python Usage

```python
from lazybrains import run_pipeline_in_notebook

run_pipeline_in_notebook(
    dataset_path="data.csv",
    target_column="target",
    pca_components=5,
    no_shap=False
)
```

## 📂 Output

* `best_model.pkl`: Trained model
* Plots: Confusion Matrix, ROC, Residuals, SHAP
* `model_report.txt`: Full model comparison

## 🛠️ Supported Models

* Linear, Tree-based, Ensemble (RF, GB, AdaBoost, XGBoost), KNN, SVM, Stacking
* Auto selection of best based on Accuracy / R²

## Run this in your terminal to install all dependencies

```cmd
pip install pandas numpy matplotlib seaborn scikit-learn xgboost shap joblib rich
```

---


# 🔍 AutoFeatSelect

**A Lightweight Python Library for Automatic Feature Selection**  
*Smart. Fast. Interpretable.*

---

## 🚀 What is AutoFeatSelect?

`AutoFeatSelect` is a fully automated feature selection tool that cleans your dataset by **removing irrelevant, redundant, or low-value features**—all with just one line of code. Whether you’re building a classification model or regression model, this tool will help you improve model performance and training speed without the hassle of manual preprocessing.

---

## ✨ Why AutoFeatSelect is Cool

- ✅ **Zero manual inspection** — It decides what to drop based on solid math.
- 🔄 **Handles both numeric & categorical features**
- 📉 Drops features using:
  - Missing value ratio
  - Low variance
  - Correlation (pairwise & clustered)
  - VIF (multicollinearity)
  - Mutual Information
  - Tree-based feature importance
- 📄 **Detailed drop report** (feature + reason)
- 🪶 Lightweight: Only uses `pandas`, `numpy`, `scikit-learn`, `statsmodels`, `scipy`

---

## 📦 Installation

```bash
pip install -U pandas numpy scikit-learn statsmodels scipy
```


## 🛠️ How to Use

```python
from lazybrains import AutoFeatSelect

selector = AutoFeatSelect(
    target_col='target',     # Optional if you want supervised feature selection
    verbose=True             # Optional for progress logs
)

# Fit + transform in one line
df_cleaned = selector.fit_transform(df, drop=True)

# Or separately
selector.fit(df)
df_cleaned = selector.transform(df)

# See what got dropped and why
report = selector.get_report()
print(report)
```

---

## 🧠 When to Use

* Before training ML models, especially with many features
* When data has potential noise, ID columns, or redundancy
* To reduce overfitting and improve model interpretability
* During automated pipelines or pre-model sanity checks

---

## 📝 Example Output

```bash
[AutoFeatSelect] Running: Drop high missing values...
[AutoFeatSelect]   Dropped: ['unimportant_column']
[AutoFeatSelect] Running: Drop single value columns...
[AutoFeatSelect]   Dropped: ['constant_feature']
...
[AutoFeatSelect] Finished selection. Kept 22 out of 48 features.
```

---

## 📊 Feature Drop Criteria

| Technique                | Purpose                                  |
| ------------------------ | ---------------------------------------- |
| Missing Ratio            | Drops features with mostly nulls         |
| Unique Ratio (ID-like)   | Removes fake IDs or row-wise unique cols |
| Variance Threshold       | Removes constant or near-constant cols   |
| Pearson Correlation      | Drops highly correlated pairs            |
| Hierarchical Clustering  | Smarter groupwise redundancy pruning     |
| VIF (Variance Inflation) | Drops multicollinear features            |
| Mutual Information       | Measures info contribution to target     |
| Tree Importance          | Uses ExtraTrees to measure signal power  |

---


# 🔍 AutoEDAPro

**AutoEDAPro** is a powerful, plug-and-play Python library for automated Exploratory Data Analysis (EDA).  
It takes a pandas DataFrame and gives you a full, beautiful report — with stats, visuals, and deep insights — either inline (Jupyter) or as an HTML file.

---

## 🚀 Features

- 📦 One-line EDA: Pass a DataFrame, get full analysis
- 🔍 Missing values, constant features, outliers detection
- 📊 Univariate & Bivariate visualizations (histograms, boxplots, KDE, correlation heatmaps)
- 🎯 Optional target column analysis for classification & regression
- 📁 HTML report export with optional logging
- ✅ Jupyter inline display or standalone HTML output
- ✨ Built using pandas, seaborn, matplotlib, plotly, numpy

---

## 📦 Installation

First, make sure you have Python 3.7+

Install required dependencies:

```bash
pip install pandas numpy matplotlib seaborn plotly scikit-learn
```


Here’s a complete `README.md` 📘 for your **AutoEDAPro** library that covers everything a user needs:

---


---

## 🧪 Example Usage

```python
from lazybrains import AutoEDA
import seaborn as sns

# Load sample dataset
df = sns.load_dataset('titanic')

# Run EDA inline (Jupyter)
eda = AutoEDA(target_col='survived')
eda.run(df)

# Run EDA and save report as HTML with logging
eda_html = AutoEDA(target_col='survived', save_report=True, enable_logging=True)
eda_html.run(df)
```

You can also test the library via CLI by running the script directly:

```bash
python autoeda.py
```

It will:

* Try to load Titanic dataset via seaborn
* Fall back to a dummy dataset if that fails
* Run both inline and saved HTML reports

---

## 🧠 Parameters

| Parameter         | Type   | Default | Description                         |
| ----------------- | ------ | ------- | ----------------------------------- |
| `target_col`      | `str`  | `None`  | Target column for supervised EDA    |
| `save_report`     | `bool` | `False` | If True, saves output as HTML       |
| `output_filename` | `str`  | `None`  | Custom filename for saved HTML      |
| `enable_logging`  | `bool` | `False` | If True, creates a log of EDA steps |

---

## 📁 Output

* **Inline Display**: Shows report directly in Jupyter notebooks
* **HTML Report**: If `save_report=True`, saves full interactive report with visualizations

---

## 🛠 Structure

Main file: `autoeda.py`
Main class: `AutoEDA`

Each report contains:

1. 📄 DataFrame shape, column types
2. ❓ Missing values overview
3. 🔁 Duplicate/constant columns
4. 📊 Univariate plots for all features
5. ⚠️ Outlier detection using IQR
6. 🔗 Bivariate correlation heatmap + pairplots
7. 🎯 Feature vs Target analysis

---

## ⚠️ Notes

* For full display in script (not Jupyter), report is saved as HTML.
* Uses Plotly CDN — make sure you're online for full interactivity.
* Logging is optional but useful for debugging long processes.

---


## 💡 Ideas for Future

* Auto feature selection preview
* Optional modeling report (LazyPredict-style)
* Model explainability (SHAP, LIME)
* CLI and web interface

---


# AutoClean 🧼  
**An advanced, scikit-learn style tabular data preprocessing pipeline.**

AutoClean simplifies and automates the process of preparing tabular data for machine learning. From imputing missing values to handling outliers, encoding categoricals, and scaling features — all steps are neatly handled in a single pipeline.

---

## 🔧 Features

- scikit-learn compatible: `fit`, `transform`, `fit_transform`
- Customizable config-based preprocessing
- Missing value imputation (mean, median, mode, constant, predictive)
- Outlier detection and capping (IQR, Z-score)
- Encoding (OneHot, Ordinal)
- Feature Scaling (Standard, MinMax, Robust)
- Detailed transformation summary (with optional Rich UI)

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

Make sure `scikit-learn`, `pandas`, `numpy` are installed. For rich logs:

```bash
pip install rich
```

---

## 🚀 Quick Start

```python
from lazybrains import AutoClean
import pandas as pd

# Sample data
df = pd.DataFrame({
    'age': [25, 30, None, 45, 50],
    'salary': [1000, 2000, 300000, 4000, None],
    'gender': ['M', 'F', None, 'F', 'M'],
    'city': ['Delhi', 'Mumbai', 'Delhi', 'Bangalore', 'Delhi']
})

# Configuration (optional)
config = {
    'impute': {'age': 'mean', 'gender': 'mode'},
    'outliers': {'salary': {'method': 'iqr', 'capping': True}},
    'encode': {'gender': 'ordinal', 'city': 'ohe'},
    'scale': {'salary': 'StandardScaler'}
}

# Use AutoClean
cleaner = AutoClean(config=config, verbose=True)
cleaned_df = cleaner.fit_transform(df)
print(cleaned_df.head())
```

---

## ⚙️ Configuration Options

```python
config = {
    'impute': {
        'age': 'mean',            # or median, mode, constant, predictive
        'gender': 'mode'
    },
    'outliers': {
        'salary': {'method': 'iqr', 'capping': True}
    },
    'encode': {
        'gender': 'ordinal',      # or 'ohe'
        'city': 'ohe'
    },
    'scale': {
        'salary': 'StandardScaler', # or MinMaxScaler, RobustScaler
    }
}
```

---

## ✅ Output

* Transformed `DataFrame` ready for ML.
* Rich summary of all preprocessing steps.
* Compatible with any sklearn pipeline.

---

## 🧠 Internals

* Uses `IterativeImputer` + `RandomForestRegressor` for predictive imputation.
* Rich logging with progress bars using the `rich` package.
* Modular & extensible design for future enhancements.

---

## 🧑‍💻 Author

Made with ❤️ by a passionate Data Scientist.

---

## 📄 License

```
MIT License
```
