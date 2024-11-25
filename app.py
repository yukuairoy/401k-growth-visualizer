import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="401(k) Growth Visualizer", layout="wide")

# IRS Uniform Lifetime Table for RMD calculations
uniform_lifetime_table = {
    72: 27.4,
    73: 26.5,
    74: 25.5,
    75: 24.6,
    76: 23.7,
    77: 22.9,
    78: 22.0,
    79: 21.1,
    80: 20.2,
    81: 19.4,
    82: 18.5,
    83: 17.7,
    84: 16.8,
    85: 16.0,
    86: 15.2,
    87: 14.4,
    88: 13.7,
    89: 12.9,
    90: 12.2,
    91: 11.5,
    92: 10.8,
    93: 10.1,
    94: 9.5,
    95: 8.9,
    96: 8.4,
    97: 7.8,
    98: 7.3,
    99: 6.8,
    100: 6.4,
}


def calculate_401k_growth(
    initial_balance,
    annual_contributions,
    retirement_age,
    current_age,
    withdrawal_rate,
    enable_rmd,
    growth_rate_aggressive,
    growth_rate_conservative,
):
    balance = round(initial_balance)
    annual_data = []
    withdrawals = []

    for i, contribution in enumerate(annual_contributions):
        age = current_age + i

        # Add contributions until retirement age
        if age <= retirement_age:
            balance += contribution

        # Apply growth rate
        if age + 5 <= retirement_age:
            balance *= 1 + growth_rate_aggressive / 100
        else:
            balance *= 1 + growth_rate_conservative / 100

        # Calculate withdrawal rate amount
        withdrawal = 0
        if age >= retirement_age:
            withdrawal = balance * (withdrawal_rate / 100)

        # Apply RMD if enabled and the user is 72 or older
        if enable_rmd and age >= 72:
            if age in uniform_lifetime_table:
                rmd = balance / uniform_lifetime_table[age]

                # Adjust withdrawal to meet RMD if it's less than RMD
                if withdrawal < rmd:
                    withdrawal = rmd

        # Deduct the withdrawal from the balance
        balance -= withdrawal
        balance = max(balance, 0)  # Prevent negative balances

        # Record data
        annual_data.append(round(balance))
        withdrawals.append(round(withdrawal))

    return annual_data, withdrawals


def get_max_contribution_by_year(year, age):
    base_contribution = 23000 + (year - 2024) * 500
    catch_up = 7500 if age >= 50 else 0
    return base_contribution + catch_up


# Streamlit UI
st.markdown(
    "<h1 style='text-align: center;'>401(k) Growth Visualizer 📈</h1>",
    unsafe_allow_html=True,
)
st.sidebar.header("🛠️ Configure Your Inputs")

# Configure inputs
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

# Withdrawal Rates
st.sidebar.markdown("### 💵 Post-Retirement Withdrawals")
withdrawal_rate = st.sidebar.slider(
    "💸 Annual Withdrawal Rate (%)", 0.0, 10.0, 5.0, 0.5
)

# Enable RMD Options
enable_rmd = st.sidebar.checkbox("Enable RMD (Required Minimum Distribution)")
st.sidebar.info(
    "🛡️ **RMD Information:** Based on IRS Uniform Lifetime Table starting at age 72. "
    "Roth 401(k)s are exempt from RMD requirements."
)

# Calculate balances and withdrawals
balances, withdrawals = calculate_401k_growth(
    initial_balance,
    annual_contributions,
    retirement_age,
    current_age,
    withdrawal_rate,
    enable_rmd,
    growth_rate_aggressive,
    growth_rate_conservative,
)

# Prepare age range and table
ages_to_project = list(range(current_age, 101))

# Plot balances
fig_balances = go.Figure()
fig_balances.add_trace(
    go.Bar(
        x=ages_to_project,
        y=balances,
        name="401(k) Balance",
        marker_color="blue",
        hovertemplate="Age: %{x}<br>Balance: $%{y:,.0f}<extra></extra>",
    )
)

# Highlight significant years
significant_ages = [
    age for age in ages_to_project if age % 10 == 0 or age == retirement_age - 1
]
for age in significant_ages:
    fig_balances.add_shape(
        type="rect",
        x0=age - 0.5,
        x1=age + 0.5,
        y0=0,
        y1=max(balances),
        fillcolor="rgba(244, 164, 96, 0.2)",  # Light orange transparent shade
        line=dict(width=0),
        layer="below",
    )

# Beautify chart layout
fig_balances.update_layout(
    title="401(k) Balance Over Time",
    xaxis=dict(title="Age", showgrid=True, zeroline=False, tickmode="linear", dtick=5),
    yaxis=dict(
        title="Balance ($)",
        showgrid=True,
        zeroline=False,
        tickprefix="$",
        tickformat=",",
    ),
    template="plotly_white",
    hovermode="x",
    margin=dict(l=40, r=40, t=50, b=40),
)

# Plot withdrawals
fig_withdrawals = go.Figure()
fig_withdrawals.add_trace(
    go.Bar(
        x=ages_to_project[ages_to_project.index(retirement_age) :],
        y=withdrawals[ages_to_project.index(retirement_age) :],
        name="Withdrawals",
        marker_color="orange",
        hovertemplate="Age: %{x}<br>Withdrawals: $%{y:,.0f}<extra></extra>",
    )
)

fig_withdrawals.update_layout(
    title="Withdrawals Over Time",
    xaxis=dict(title="Age", showgrid=True, zeroline=False, tickmode="linear", dtick=5),
    yaxis=dict(
        title="Withdrawals ($)",
        showgrid=True,
        zeroline=False,
        tickprefix="$",
        tickformat=",",
    ),
    template="plotly_white",
    hovermode="x",
    margin=dict(l=40, r=40, t=50, b=40),
)

# Display the balance chart
st.plotly_chart(fig_balances, use_container_width=True)

# Show balance at retirement
balance_at_retirement = balances[retirement_age - current_age - 1]
st.markdown(f"### 🏆 Balance at Retirement: **${balance_at_retirement:,}**")

# Conditionally display the withdrawals chart
if withdrawal_rate > 0 or enable_rmd:
    fig_withdrawals = go.Figure()
    fig_withdrawals.add_trace(
        go.Bar(
            x=ages_to_project[ages_to_project.index(retirement_age) :],
            y=withdrawals[ages_to_project.index(retirement_age) :],
            name="Withdrawals",
            marker_color="orange",
            hovertemplate="Age: %{x}<br>Withdrawals: $%{y:,.0f}<extra></extra>",
        )
    )

    fig_withdrawals.update_layout(
        title="Withdrawals Over Time (Bar Chart)",
        xaxis=dict(
            title="Age", showgrid=True, zeroline=False, tickmode="linear", dtick=5
        ),
        yaxis=dict(
            title="Withdrawals ($)",
            showgrid=True,
            zeroline=False,
            tickprefix="$",
            tickformat=",",
        ),
        template="plotly_white",
        hovermode="x",
        margin=dict(l=40, r=40, t=50, b=40),
    )

    st.plotly_chart(fig_withdrawals, use_container_width=True)

# Show contributions, balances, and withdrawals in a collapsible table
contribution_table = pd.DataFrame(
    {
        "Age": ages_to_project,
        "End of Year Balance ($)": balances,
        "Annual Contribution ($)": annual_contributions,
        "Withdrawals ($)": withdrawals,
    }
)

# Format table columns
contribution_table["End of Year Balance ($)"] = contribution_table[
    "End of Year Balance ($)"
].apply(lambda x: f"{x:,}")
contribution_table["Annual Contribution ($)"] = contribution_table[
    "Annual Contribution ($)"
].apply(lambda x: f"{x:,}")
contribution_table["Withdrawals ($)"] = contribution_table["Withdrawals ($)"].apply(
    lambda x: f"{x:,}"
)

# Highlight significant rows in the table
styled_contribution_table = contribution_table.style.apply(
    lambda row: (
        ["background-color: #f4f4a3; font-weight: bold"] * len(row)
        if row["Age"] in significant_ages
        else [""] * len(row)
    ),
    axis=1,
)

# Collapsible section for the table
with st.expander("📊 401(k) Contributions, Balances, and Withdrawals", expanded=False):
    st.dataframe(styled_contribution_table, use_container_width=True, hide_index=True)

# Streamlit UI for RMD Table
with st.expander("📑 IRS Uniform Lifetime Table for RMD", expanded=False):
    rmd_table = pd.DataFrame.from_dict(
        uniform_lifetime_table, orient="index", columns=["Divisor"]
    )
    rmd_table.index.name = "Age"
    rmd_table.reset_index(inplace=True)
    st.markdown(
        "The table below shows the IRS uniform lifetime divisors used to calculate RMDs:"
    )
    st.dataframe(
        rmd_table.style.format({"Divisor": "{:.1f}"}),
        use_container_width=True,
        hide_index=True,
    )
