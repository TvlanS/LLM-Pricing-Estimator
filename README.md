# Pricing from Historical Value

AI-powered price estimation tool for home renovation jobs using historical vendor data. Generate accurate invoice tables based on past job costs with semantic search and LLM-powered analysis. Note : Pricing in sample may not reflect actual prices as dataset sample is synthetically generated.

<p align="center">
  <img src="https://github.com/TvlanS/LLM-Pricing-Estimator/blob/b66546cabcc530701df4de02fe679ef3a2cb941d/Sample%20Img/Part%201.png" width="600" alt="LLM Pricing Part 1">
  <br>
  <em>Output example - Part 1</em>
</p>

## Motivation

Estimating renovation costs manually is time-consuming and prone to errors. This tool automates the process by leveraging historical job data to provide precise price estimates, reducing the risk of costly mistakes and saving valuable time for contractors and customers.

## Key Features

- **CSV to Vector Database Conversion**: Automatically convert historical job CSV files into SQLite databases with vector embeddings for efficient similarity search.
- **Semantic Job Matching**: Use sentence-transformers to find the most relevant historical jobs based on job description similarity.
- **LLM-Powered Invoice Generation**: Generate professional invoice tables using DeepSeek LLM with strict formatting rules and validation.
- **Interactive Web Interface**: Clean, modern Gradio-based UI for easy interaction without technical expertise.
- **Historical Logging**: All estimation requests and outputs are automatically saved as JSON files for audit and analysis.
- **Multi-Job Support**: Process multiple job types in a single request with separate quantity specifications.
- **Outlier Detection**: Automatically exclude extreme price outliers when calculating average costs.

## Tech Stack

- **Python 3.12+** - Core programming language
- **Gradio** - Web interface framework
- **LangChain Community** - HuggingFace embeddings integration
- **Sentence Transformers** - `all-MiniLM-L6-v2` for text embeddings
- **SQLite + sqlite-vec** - Vector database for similarity search
- **DeepSeek LLM API** - AI model for invoice generation
- **pandas** - Data manipulation and CSV processing
- **numpy** - Numerical operations
- **pyprojroot** - Project path management

## Installation

### Prerequisites

- Python 3.12 or higher
- DeepSeek API key (free tier available at [deepseek.com](https://www.deepseek.com/))
- Git (optional, for cloning)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd "47.1 Price Estimation Updated"
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

pip install -r requirements.txt


### Step 4: Configure API Key

Edit `config/config.yml` and replace `<input your deepseek api key>` with your actual DeepSeek API key:

```yaml
deepseek:
  api_key: "your-deepseek-api-key-here"
  website_url: "https://api.deepseek.com"
```

### Step 5: Prepare Historical Data

Place your CSV files in the `Excel/` directory. The CSV should contain at minimum these columns:
- `Job Scope` - Description of the work
- `Job Scope Cost` - Cost for the job (can be per unit or total)
- `Quantity` - Number of units (optional, defaults to 1)

Sample data is provided in `Excel/vendor_style_home_renovation_jobs_malaysia.csv`.

## Troubleshooting

### sqlite-vec Installation Issues
The `sqlite-vec` package may require building from source on some systems. If you encounter installation errors:

1. **Windows**: Install pre-built binaries from the [sqlite-vec releases page](https://github.com/asg017/sqlite-vec/releases) or use WSL.
2. **macOS/Linux**: Ensure you have Rust and Cargo installed, then build from source:
   ```bash
   pip install sqlite-vec --no-binary sqlite-vec
   ```

### DeepSeek API Errors
- Verify your API key in `config/config.yml`
- Ensure you have sufficient credits in your DeepSeek account
- Check network connectivity to `https://api.deepseek.com`

### CSV File Format Issues
- Ensure your CSV uses UTF-8 encoding
- Required columns: `Job Scope`, `Job Scope Cost`
- Optional column: `Quantity` (defaults to 1 if missing)

## Usage

### Starting the Application

Run the main script:

```bash
python main.py
```

The application will:
1. Process CSV files and create SQLite databases with vector embeddings
2. Start a local web server
3. Print the local URL (typically `http://127.0.0.1:7860`)

### Using the Web Interface

1. **Open your browser** to the provided URL
2. **Enter job requests** in the text box using natural language:
   - Separate different job types with commas
   - Include quantities in the description
   - Example: `install 6 door knobs, replace 4 light switches in kitchen`
3. **Click Send** or press Enter
4. **View the results**:
   - Invoice table with job descriptions, unit costs, quantities, and totals
   - Notes about any assumptions or unmatched jobs
   - Raw embedding output (expandable section)

### Example Request and Output

**Input:**
```
install 6 door knobs, replace 4 light switches in kitchen
```

**Output (simplified):**

| Job Description | Cost of the Job for 1 qty (RM) | Quantity | Total Cost (RM) | Final Cost in (RM) |
|----------------|--------------------------------|----------|-----------------|-------------------|
| Door Knob Installation | 45.50 | 6 | 273.00 | 273.00 |
| Light Switch Replacement | 32.75 | 4 | 131.00 | 131.00 |

**Notes:**
- Average costs calculated from 8 similar historical jobs
- Excluded one outlier at RM 120.00

## Project Structure

```
.
├── main.py                    # Gradio application entry point
├── config/
│   └── config.yml            # API keys and prompt configurations
├── Excel/                    # Input CSV files with historical data
├── SQL/                      # Generated SQLite databases with embeddings
├── Historical/               # JSON logs of all estimations
├── utils/
│   ├── classes.py            # TableEmbedding class with database and LLM logic
│   ├── config_step.py        # Configuration loader
│   └── __init__.py
└── README.md
```

## Configuration

### Model Settings

Edit `config/config.yml` to adjust:

- `Models.embedding`: Change the embedding model (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `prompt.system_prompt2`: Primary LLM instructions for invoice generation (used by default)
- `prompt.system_prompt`: Alternative prompt template (not used by default)
- `prompt.prompt_xero`: Xero accounting API integration prompts

### Embedding Parameters

In `utils/classes.py`, the `TableEmbedding` class constructor accepts a `model_name` parameter to use different sentence transformer models.

### Search Parameters

The `search_embeddings` method in `TableEmbedding` accepts a `top_k` parameter to control how many historical records are retrieved for each job type.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -m 'Add some improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints for new functions
- Update documentation for any changes
- Include tests for new functionality

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [DeepSeek](https://www.deepseek.com/) for providing the LLM API
- [Hugging Face](https://huggingface.co/) for the sentence-transformers library
- [Gradio](https://www.gradio.app/) for the intuitive web interface framework

## Support

For issues, questions, or suggestions:
1. Check the [GitHub Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed description of the problem
3. Include steps to reproduce and error messages if applicable

---

**Disclaimer**: This tool provides estimates based on historical data. Always verify prices with current market rates and consult professionals for critical financial decisions.
