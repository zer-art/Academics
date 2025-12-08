# Word Suggest 📝

A lightweight, probability-based autocorrect system built with Python. This tool leverages **Levenshtein distance** and **word frequency analysis** to suggest corrections for misspelled words.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Pandas](https://img.shields.io/badge/Pandas-Using-150458)
![Status](https://img.shields.io/badge/Status-Active-success)

## 🚀 Features

- **Probabilistic Correction**: Uses a dataset-driven probability model to suggest the most likely words.
- **Top-N Suggestions**: Returns a ranked list of potential corrections, not just one.
- **Customizable Dataset**: Easily swap the source text to train the model on different domains.

## 📊 Benchmarks & Metrics

We believe in transparency and tracking performance. The following metrics were collected using a test set of 15 common misspellings on a local machine (M1/M2/Intel Mac).

| Metric | Value | Description |
| :--- | :--- | :--- |
| **Top-1 Accuracy** | **6.67%** | Correct word is the first suggestion |
| **Top-5 Accuracy** | **46.67%** | Correct word is in the top 5 suggestions |
| **Avg Latency** | **~594 ms** | Average time to process a single word |

> **Note**: This is a baseline probabilistic model. Performance relies heavily on the coverage of the training text (`autocorrect book.txt`).

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd word-suggest
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

Run the `suggest.py` script (or import it) to use the autocorrect function.

```python
import suggest

# Get suggestions for a misspelled word
result = suggest.autocorrect("helllo")
print(result)
```

**Example Output:**
```
     word  probability
0   hello     0.000451
1   hell      0.000120
...
```

## 📂 Project Structure

- `suggest.py`: Core logic for probability calculation and word suggestion.
- `autocorrect book.txt`: Source text used to build the vocabulary and frequency model.
- `benchmark.py`: Script to evaluating model performance.
- `requirements.txt`: Project dependencies.

## 🧪 Testing

To run the benchmarks yourself:
```bash
python benchmark.py
```
