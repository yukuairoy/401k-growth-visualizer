import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="401(k) Growth Visualizer",
    layout="wide",
    menu_items={
        "About": """
        💡 Aggressive growth applies until 5 years before retirement. RMDs start at age 72. 
        This tool provides general illustrations only.
        """
    },
)

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

        # Store the previous year's balance for withdrawal calculations
        previous_balance = balance

        # Add contributions until retirement age
        if age < retirement_age:
            balance += contribution

        # Apply growth rate
        if age + 5 < retirement_age:
            balance *= 1 + growth_rate_aggressive / 100
        else:
            balance *= 1 + growth_rate_conservative / 100

        # Calculate withdrawal rate amount based on the previous year's balance
        withdrawal = 0
        if age >= retirement_age:
            withdrawal = previous_balance * (withdrawal_rate / 100)

        # Apply RMD if enabled and the user is 72 or older
        if enable_rmd and age >= 72:
            if age in uniform_lifetime_table:
                rmd = previous_balance / uniform_lifetime_table[age]

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

st.divider()

# Sidebar inputs for current and retirement age
current_age = st.sidebar.slider("🧑 Current Age", 22, 65, 40)
retirement_age = st.sidebar.slider("🏖️ Retirement Age", current_age, 100, 65)
initial_balance = st.sidebar.number_input(
    "💰 Initial Balance ($)", value=10000, step=500
)

# Define global age range for projections
ages_to_project = list(range(current_age, 101))

# Contributions and Employer Match Section
with st.sidebar.expander("📊 Contributions and Employer Match", expanded=True):
    use_max_contribution = st.checkbox("Use IRS Max Contribution 💼")
    if use_max_contribution:
        st.info("📌 Catch-up contributions of $7,500 included for users aged 50+.")
        annual_contributions = [
            (
                round(get_max_contribution_by_year(2024 + i, current_age + i))
                if current_age + i < retirement_age
                else 0
            )
            for i in range(len(ages_to_project))
        ]
    else:
        annual_contribution = st.number_input(
            "🤑 Annual Contribution ($)", value=12000, step=500
        )
        annual_contributions = [
            round(annual_contribution) if current_age + i < retirement_age else 0
            for i in range(len(ages_to_project))
        ]

    match_type = st.radio(
        "🏢 Company Match Type", ["Absolute Amount", "Percentage of Contribution"]
    )
    if match_type == "Percentage of Contribution":
        match_percentage = st.slider("📊 Company Match (%)", 0, 100, 0)
        company_match = [
            (
                round(contribution * match_percentage / 100)
                if current_age + i < retirement_age
                else 0
            )
            for i, contribution in enumerate(annual_contributions)
        ]
    else:
        match_amount = st.number_input(
            "🏢 Company Match Amount ($)", value=5000, step=500
        )
        company_match = [
            round(match_amount) if current_age + i < retirement_age else 0
            for i in range(len(annual_contributions))
        ]

    annual_contributions = [
        contribution + match
        for contribution, match in zip(annual_contributions, company_match)
    ]

# Sidebar group for growth rates
with st.sidebar.expander("📈 Growth Rates"):
    growth_rate_aggressive = st.slider(
        "🚀 Aggressive Growth Rate (%)", 0.0, 20.0, 8.0, 0.5
    )
    growth_rate_conservative = st.slider(
        "🛡️ Conservative Growth Rate (%)", 0.0, 10.0, 4.0, 0.5
    )

# Sidebar group for withdrawals
with st.sidebar.expander("💵 Withdrawals and RMD"):
    withdrawal_rate = st.slider("💸 Annual Withdrawal Rate (%)", 0.0, 10.0, 4.5, 0.5)
    enable_rmd = st.checkbox("Enable RMD (Required Minimum Distribution)", value=True)
    st.info(
        "🛡️ **RMD Information:** Based on IRS Uniform Lifetime Table starting at age 72."
    )

# Calculate balances and withdrawals
balances, withdrawals = calculate_401k_growth(
    initial_balance=initial_balance,
    annual_contributions=annual_contributions,
    retirement_age=retirement_age,
    current_age=current_age,
    withdrawal_rate=withdrawal_rate,
    enable_rmd=enable_rmd,
    growth_rate_aggressive=growth_rate_aggressive,
    growth_rate_conservative=growth_rate_conservative,
)

# Summary Section
st.markdown("### 💰 Retirement Milestones")
col1, col2, col3 = st.columns(3)

# First row
with col1:
    st.metric(
        "Balance at Retirement", f"${balances[retirement_age - current_age - 1]:,}"
    )
with col2:
    first_withdrawal = next((w for w in withdrawals if w > 0), 0)
    st.metric("First Year Withdrawal", f"${first_withdrawal:,}")
with col3:
    # Find first RMD amount (at age 72)
    if 72 >= current_age:
        rmd_index = 72 - current_age
        if rmd_index < len(withdrawals):
            first_rmd = withdrawals[rmd_index]
            st.metric("First RMD (Age 72)", f"${first_rmd:,}")
        else:
            st.metric("First RMD (Age 72)", "N/A")
    else:
        st.metric("First RMD (Age 72)", "N/A")

# Second row
key_ages = [70, 80, 90]
for i, age in enumerate(key_ages):
    with [col1, col2, col3][i]:
        if age >= current_age:
            balance_index = age - current_age
            if balance_index < len(balances):
                st.metric(f"Balance at {age}", f"${balances[balance_index]:,}")
            else:
                st.metric(f"Balance at {age}", "N/A")
        else:
            st.metric(f"Balance at {age}", "N/A")

st.divider()

# Chart for balances
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
st.plotly_chart(fig_balances, use_container_width=True)

# Withdrawals Chart
if withdrawal_rate > 0 or enable_rmd:
    if retirement_age in ages_to_project:
        retirement_index = ages_to_project.index(retirement_age)
    else:
        st.error(
            "Error: Retirement age is outside the valid range. Adjust your settings."
        )
        retirement_index = 0

    fig_withdrawals = go.Figure()
    fig_withdrawals.add_trace(
        go.Bar(
            x=ages_to_project[retirement_index:],
            y=withdrawals[retirement_index:],
            name="Withdrawals",
            marker_color="orange",
            hovertemplate="Age: %{x}<br>Withdrawals: $%{y:,.0f}<extra></extra>",
        )
    )
    fig_withdrawals.update_layout(
        title="Withdrawals Over Time",
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

st.divider()

# Contributions, Balances, and Withdrawals Table
contribution_table = pd.DataFrame(
    {
        "Age": ages_to_project,
        "End of Year Balance ($)": balances,
        "Annual Contribution ($)": annual_contributions,
        "Withdrawals ($)": withdrawals,
    }
)

# Format columns for better readability
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
significant_ages = [retirement_age - 1] + [
    age for age in ages_to_project if age % 10 == 0
]
styled_contribution_table = contribution_table.style.apply(
    lambda row: (
        ["background-color: #f4f4a3; font-weight: bold"] * len(row)
        if row["Age"] in significant_ages
        else [""] * len(row)
    ),
    axis=1,
)

# Display contributions table in a collapsible section
with st.expander("📊 401(k) Contributions, Balances, and Withdrawals", expanded=False):
    st.dataframe(styled_contribution_table, use_container_width=True, hide_index=True)

# Move this AFTER all visualizations, tables, and download button
csv = contribution_table.to_csv(index=False)
st.download_button(
    label="📥 Download Data as CSV",
    data=csv,
    file_name="401k_projections.csv",
    mime="text/csv",
)
