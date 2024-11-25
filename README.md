# 401(k) Growth Visualizer 📈

The **401(k) Growth Visualizer** is a [Streamlit-based app](https://401k-growth.streamlit.app/) to simulate your 401(k) growth. It models contributions, employer matching, withdrawals, growth rates, and Required Minimum Distributions.

## Features 🌟
- **Dynamic Bar Charts:** Visualize 401(k) balance and withdrawals over time.
- **IRS Contribution Limits:** Includes $500 annual increases and $7,500 catch-up contributions for those aged 50+.
- **Highlighted Milestones:** Emphasizes key years (e.g., multiples of 10 and the year before retirement).
- **Withdrawals:** Configure a percentage-based withdrawal post-retirement.
- **RMDs:** Automatically calculates RMD based on the IRS Uniform Lifetime Table.  
  - Example: At age 73 with $100,000 balance, RMD = $100,000 ÷ 26.5 ≈ $3,774.
  - **Source:** [IRS Publication 590-B](https://www.irs.gov/pub/irs-pdf/p590b.pdf)

## Demo 🎥
Try the live demo at: https://401k-growth.streamlit.app/

## Prerequisites 📋
- Python 3.7+
- Dependencies: `streamlit`, `pandas`, `plotly`

## Installation & Setup 🛠️
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Clone the repository:
   ```bash
   git clone https://github.com/yukuairoy/401k-growth-visualizer.git
   ```
3. Navigate to the directory:
   ```bash
   cd 401k-growth-visualizer
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Contributing 🤝
Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.