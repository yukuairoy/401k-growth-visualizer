import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="401(k) Growth Visualizer", layout="wide")


def calculate_401k_growth(
    initial_balance,
    annual_contributions,
    retirement_age,
    current_age,
    growth_rate_aggressive,
    growth_rate_conservative,
):
    balance = round(initial_balance)
    annual_data = []

    for i, contribution in enumerate(annual_contributions):
        balance += contribution

        # Determine growth rate: Aggressive or Conservative
        if current_age + i + 5 <= retirement_age:
            balance *= 1 + growth_rate_aggressive / 100
        else:
            balance *= 1 + growth_rate_conservative / 100

        balance = round(balance)  # Round to nearest integer
        annual_data.append(balance)

    return annual_data


def get_max_contribution_by_year(year, age):
    """
    Calculate the maximum allowed contribution for a given year and age.
    Starts at $23,000 in 2024 and increases by $500 each subsequent year.
    Includes a catch-up contribution of $7,500 for ages 50 and older.
    """
    base_contribution = 23000 + (year - 2024) * 500
    catch_up = 7500 if age >= 50 else 0
    return base_contribution + catch_up


def highlight_row(row):
    """
    Highlight the row for the year before retirement and multiples of 10.
    """
    if row["Age"] == retirement_age - 1 or row["Age"] % 10 == 0:
        return ["background-color: #f4f4a3; font-weight: bold"] * len(row)
    else:
        return [""] * len(row)


# Streamlit UI
st.markdown(
    "<h1 style='text-align: center;'>401(k) Growth Visualizer 📈</h1>",
    unsafe_allow_html=True,
)
st.sidebar.header("🛠️ Configure Your Inputs")

# Configure inputs in the specified order
current_age = st.sidebar.slider("🧑 Current Age", 22, 65, 40)
retirement_age = st.sidebar.slider("🏖️ Retirement Age", current_age, 100, 65)

# Use Max Contribution
use_max_contribution = st.sidebar.checkbox("Use IRS Max Contribution 💼")
if use_max_contribution:
    st.sidebar.info(
        "⚡ **Assumption:** The IRS increases the maximum allowed contribution by $500 each year."
    )
    st.sidebar.info(
        "✨ **Catch-up Contributions:** $7,500 are included for users aged 50 or older when 'Use IRS Max Contribution' is selected."
    )

# Annual Contribution Logic
if use_max_contribution:
    years_to_project = list(range(2024, 2024 + (101 - current_age)))
    annual_contributions = [
        round(get_max_contribution_by_year(year, current_age + i))
        for i, year in enumerate(years_to_project)
    ]
else:
    annual_contribution = st.sidebar.number_input(
        "🤑 Annual Contribution ($)", value=12000, step=500
    )
    years_to_project = list(range(2024, 2024 + (101 - current_age)))
    annual_contributions = [
        round(annual_contribution) if current_age + i <= retirement_age else 0
        for i, _ in enumerate(years_to_project)
    ]

# Company Match Type
match_type = st.sidebar.radio(
    "🏢 Company Match Type", ["Absolute Amount", "Percentage of Contribution"]
)
if match_type == "Percentage of Contribution":
    match_percentage = st.sidebar.slider("📊 Company Match (%)", 0, 100, 0)
    company_match = [
        round(contribution * match_percentage / 100)
        for contribution in annual_contributions
    ]
else:
    company_match = [
        round(
            st.sidebar.number_input("🏢 Company Match Amount ($)", value=5000, step=500)
        )
    ] * len(annual_contributions)

# Add company match to contributions
annual_contributions = [
    contribution + match
    for contribution, match in zip(annual_contributions, company_match)
]

initial_balance = st.sidebar.number_input(
    "💰 Initial Balance ($)", value=10000, step=1000
)

# Growth Rates
st.sidebar.markdown("### 📈 Growth Rates")
growth_rate_aggressive = st.sidebar.slider(
    "🚀 Aggressive Growth Rate (%)", 0.0, 20.0, 8.0, 0.5
)
growth_rate_conservative = st.sidebar.slider(
    "🛡️ Conservative Growth Rate (%)", 0.0, 10.0, 4.0, 0.5
)
st.sidebar.info(
    "🛡️ **Conservative Growth Rate**: Applied starting 5 years prior to the selected retirement age."
)

# Calculate growth
balances = calculate_401k_growth(
    initial_balance,
    annual_contributions,
    retirement_age,
    current_age,
    growth_rate_aggressive,
    growth_rate_conservative,
)

# Create a concise table with "Age", "End of Year Balance", and "Annual Contribution" columns
ages_to_project = list(range(current_age, 101))
contribution_table = pd.DataFrame(
    {
        "Age": ages_to_project,
        "End of Year Balance ($)": balances,
        "Annual Contribution ($)": annual_contributions,
    }
)

# Calculate balance at retirement
balance_at_retirement = balances[retirement_age - current_age - 1]

# Format columns as integers with commas
contribution_table["End of Year Balance ($)"] = contribution_table[
    "End of Year Balance ($)"
].apply(lambda x: f"{x:,}")
contribution_table["Annual Contribution ($)"] = contribution_table[
    "Annual Contribution ($)"
].apply(lambda x: f"{x:,}")

# Highlight rows for significant ages
styled_contribution_table = contribution_table.style.apply(highlight_row, axis=1)

# Enhanced Interactive Plot with Plotly (Highlight Significant Ages)
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=ages_to_project,
        y=balances,
        mode="lines+markers",
        name="401(k) Balance",
        line=dict(color="blue", width=2),
        marker=dict(size=6),
        hovertemplate="Age: %{x}<br>Balance: $%{y:,.0f}<extra></extra>",
    )
)

# Highlight the year before retirement and multiples of 10
significant_ages = [retirement_age - 1] + [
    age for age in ages_to_project if age % 10 == 0
]
for age in significant_ages:
    fig.add_shape(
        type="rect",
        x0=age - 0.5,
        x1=age + 0.5,
        y0=0,
        y1=max(balances),
        fillcolor="rgba(244, 164, 96, 0.2)",  # Light orange transparent shade
        line=dict(width=0),
        layer="below",
    )

# Beautify the plot
fig.update_layout(
    xaxis=dict(title="Age", showgrid=True, zeroline=False, tickmode="linear", dtick=5),
    yaxis=dict(
        title="End of Year Balance ($)",
        showgrid=True,
        zeroline=False,
        tickprefix="$",
        tickformat=",",
    ),
    template="plotly_white",
    hovermode="x",
    margin=dict(l=40, r=40, t=50, b=40),
)

st.plotly_chart(fig, use_container_width=True)

# Display balance at retirement
st.markdown(f"### 🏆 Balance at Retirement: **${balance_at_retirement:,}**")

# Display contribution and balance table in a collapsible section
with st.expander("📊 401(k) Contributions and Balances Over Time", expanded=False):
    st.dataframe(styled_contribution_table, use_container_width=True, hide_index=True)
