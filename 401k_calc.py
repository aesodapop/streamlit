import streamlit as st
import pandas as pd

# Function to calculate 401(k) contributions
def calculate_401k_contributions(
    base_salary, aip_april, aip_october, age,
    pre_tax_percentage, roth_percentage, after_tax_percentage, add_catch_up, employer_match
):
    salary_cap = 350000  # IRS salary cap for 401(k) contributions
    annual_pre_tax_roth_limit = 23500  # IRS limit for combined pre-tax and Roth contributions
    catch_up_limit = 7500  # Catch-up contribution limit for age 50+
    add_catch_up_limit = 3750  # Additional catch-up for ages 60-63
    contribution_limit = 70000  # Total contribution limit, including employee and employer contributions
    pay_periods = 26  # Number of pay periods

    # Cap the base salary at the IRS salary cap
    base_salary = min(base_salary, salary_cap)

    # Adjust limits
    if add_catch_up == "No":
        if age >= 50:
            contribution_limit += catch_up_limit
            remaining_catch_up_limit = catch_up_limit
        else:
            catch_up_limit = 0  # No catch-up contributions if under 50
            remaining_catch_up_limit = 0
    elif add_catch_up == "Yes":
        if age >= 50 and age not in range(60, 64):
            contribution_limit += catch_up_limit
            remaining_catch_up_limit = catch_up_limit
        elif age in range(60, 64):
            catch_up_limit += add_catch_up_limit
            contribution_limit += catch_up_limit
            remaining_catch_up_limit = catch_up_limit
        else:
            catch_up_limit = 0  # No catch-up contributions if under 50
            remaining_catch_up_limit = 0

    total_pre_tax = 0
    total_roth = 0
    total_pre_tax_catch_up = 0
    total_roth_catch_up = 0
    total_after_tax = 0
    total_company_match = 0
    total_contributions = 0

    # Initialize limit reached flags
    limits_reached = {
        'pre_tax_roth_limit': False,
        'catch_up_limit': False,
        'match_limit': False,
        'total_contribution_limit': False
    }

    breakdown = []

    # Loop through each pay period
    for period in range(1, pay_periods + 1):

        # Initialize limit messages and flags for this period

        period_limits_hit = {
            'pre_tax_roth_limit_hit': False,
            'catch_up_limit_hit': False,
            'match_limit_hit': False,
            'total_contribution_limit_hit': False
        }

        # Calculate salary per period and include AIP if applicable
        salary_per_period = base_salary / pay_periods
        if period == 8:
            salary_per_period += aip_april
        elif period == 21:
            salary_per_period += aip_october

        # Remaining annual limits
        remaining_pre_tax_roth_limit = annual_pre_tax_roth_limit - (total_pre_tax + total_roth)
        remaining_catch_up_limit = catch_up_limit - (total_pre_tax_catch_up + total_roth_catch_up)
        remaining_contribution_limit = contribution_limit - (
            total_pre_tax + total_roth + total_pre_tax_catch_up + total_roth_catch_up +
            total_company_match + total_after_tax
        )

        # Initialize contributions for this period
        pre_tax_contrib_desired = salary_per_period * (pre_tax_percentage / 100)
        roth_contrib_desired = salary_per_period * (roth_percentage / 100)
        after_tax_contrib_desired = salary_per_period * (after_tax_percentage / 100)

        # Step 1: Calculate pre-tax contributions
        pre_tax_contrib = min(pre_tax_contrib_desired, remaining_pre_tax_roth_limit, remaining_contribution_limit)
        total_pre_tax += pre_tax_contrib
        remaining_contribution_limit -= pre_tax_contrib

        # Step 2: Calculate Roth contributions
        remaining_pre_tax_roth_limit -= pre_tax_contrib
        roth_contrib = min(roth_contrib_desired, remaining_pre_tax_roth_limit, remaining_contribution_limit)
        total_roth += roth_contrib
        remaining_contribution_limit -= roth_contrib

        # Update remaining pre-tax/Roth limit after contributions
        remaining_pre_tax_roth_limit -= roth_contrib

        # Check if pre-tax/Roth limit reached
        if remaining_pre_tax_roth_limit <= 0:
            limits_reached['pre_tax_roth_limit'] = True
            period_limits_hit['pre_tax_roth_limit_hit'] = True
 
        # Step 3: Calculate pre-tax catch-up contributions
        pre_tax_catch_up_contrib = 0
        if age >= 50 and remaining_catch_up_limit > 0 and remaining_contribution_limit > 0:
            pre_tax_catch_up_contrib_desired = max(0, pre_tax_contrib_desired - pre_tax_contrib)
            pre_tax_catch_up_contrib = min(pre_tax_catch_up_contrib_desired, remaining_catch_up_limit, remaining_contribution_limit)
            total_pre_tax_catch_up += pre_tax_catch_up_contrib
            remaining_contribution_limit -= pre_tax_catch_up_contrib
            remaining_catch_up_limit -= pre_tax_catch_up_contrib

        # Step 4: Calculate Roth catch-up contributions
        roth_catch_up_contrib = 0
        if age >= 50 and remaining_catch_up_limit > 0 and remaining_contribution_limit > 0:
            roth_catch_up_contrib_desired = max(0, roth_contrib_desired - roth_contrib)
            roth_catch_up_contrib = min(roth_catch_up_contrib_desired, remaining_catch_up_limit, remaining_contribution_limit)
            total_roth_catch_up += roth_catch_up_contrib
            remaining_contribution_limit -= roth_catch_up_contrib
            remaining_catch_up_limit -= roth_catch_up_contrib

        # Check if catch-up limit reached
        if remaining_catch_up_limit <= 0:
            limits_reached['catch_up_limit'] = True
            period_limits_hit['catch_up_limit_hit'] = True

        # Step 5: Calculate company match
        max_company_match = salary_per_period * employer_match
        eligible_for_match = pre_tax_contrib + roth_contrib + pre_tax_catch_up_contrib + roth_catch_up_contrib
        company_match_contrib = min(eligible_for_match, max_company_match, remaining_contribution_limit)
        total_company_match += company_match_contrib
        remaining_contribution_limit -= company_match_contrib

        # Check if match limit reached
        if total_company_match == base_salary * employer_match:
            limits_reached['match_limit'] = True
            period_limits_hit['match_limit_hit'] = True

        # Update total contributions prior to adding after-tax
        total_contributions = (
            total_pre_tax + total_roth + total_pre_tax_catch_up + total_roth_catch_up +
            total_company_match + total_after_tax
        )

        # Step 6: Calculate after-tax contributions
        after_tax_contrib = 0
        # disabled - AT stopping after exceeding annual additions limit
        #if total_contributions >= contribution_limit - catch_up_limit and remaining_catch_up_limit > 0:
            #after_tax_contrib = 0
        if total_contributions < contribution_limit - catch_up_limit and total_contributions + after_tax_contrib_desired > contribution_limit - catch_up_limit and remaining_catch_up_limit > 0:
            after_tax_contrib = (contribution_limit - catch_up_limit) - total_contributions
            total_after_tax += after_tax_contrib
            remaining_contribution_limit -= after_tax_contrib
        else:
            after_tax_contrib = min(after_tax_contrib_desired, remaining_contribution_limit)
            total_after_tax += after_tax_contrib
            remaining_contribution_limit -= after_tax_contrib

        # Update total contributions post after-tax
        total_contributions = (
            total_pre_tax + total_roth + total_pre_tax_catch_up + total_roth_catch_up +
            total_company_match + total_after_tax
        )

        # Check if total contribution limit reached
        if remaining_contribution_limit <= 0:
            limits_reached['total_contribution_limit'] = True
            period_limits_hit['total_contribution_limit_hit'] = True

        # Calculate total contributions for this period
        period_total_contributions = (
            pre_tax_contrib + roth_contrib + pre_tax_catch_up_contrib +
            roth_catch_up_contrib + company_match_contrib + after_tax_contrib
        )

        # Store the breakdown for this period
        if period_total_contributions > 0:
            breakdown.append({
                'Period': period,
                'Wages This Period': salary_per_period,
                'Pay Period Contributions': '',
                'Pre-Tax': pre_tax_contrib,
                'Roth': roth_contrib,
                'Pre-Tax Catch-Up': pre_tax_catch_up_contrib,
                'Roth Catch-Up': roth_catch_up_contrib,
                'Company Match': company_match_contrib,
                'After-Tax': after_tax_contrib,
                'Contributions to Date': '',
                'Pre-tax/Roth': total_pre_tax + total_roth,
                'Catch-Up': total_pre_tax_catch_up + total_roth_catch_up,
                'Match': total_company_match,
                'Total': total_contributions,
                'pre_tax_roth_limit_hit': period_limits_hit['pre_tax_roth_limit_hit'],
                'catch_up_limit_hit': period_limits_hit['catch_up_limit_hit'],
                'match_limit_hit': period_limits_hit['match_limit_hit'],
                'total_contribution_limit_hit': period_limits_hit['total_contribution_limit_hit']
            })

        # Stop contributions once the overall contribution limit is reached
        if remaining_contribution_limit <= 0:
            break

    # Estimate the true-up contribution based on company match eligibility
    eligible_contributions_for_match = total_pre_tax + total_roth + total_pre_tax_catch_up + total_roth_catch_up
    expected_match_percent = min(employer_match, eligible_contributions_for_match / (base_salary + aip_april + aip_october))

    expected_company_match = expected_match_percent * (base_salary + aip_april + aip_october)

    if total_company_match != expected_company_match:
        estimated_true_up = expected_company_match - total_company_match
    else:
        estimated_true_up = 0

    return (
        breakdown, total_pre_tax, total_roth, total_pre_tax_catch_up, total_roth_catch_up,
        total_company_match, total_after_tax, total_contributions, estimated_true_up,
        annual_pre_tax_roth_limit, catch_up_limit, contribution_limit
    )


# Streamlit App
def main():

    st.markdown(
        '<h1 style="color: #FFFFFF; font-size: 40px;">401(k) Contribution Calculator</h1>',
        unsafe_allow_html=True
    )
    st.markdown("**Estimate your annual contributions and your contributions per pay period to help determine your 2025 contribution percentages.**")
    st.markdown(" ")

    errors = []

    col1, col3, col2 = st.columns([2.5, 0.5, 3])

    with col1:

        # Select box for additional catch-up
        add_catch_up = st.selectbox("My 401(k) plan has additional catch-up contributions ages 60-63?", ("Yes", "No"))

        # Employer match input box
        employer_match_input = st.text_input('Enter your employer match percentage', placeholder='e.g. 5')
        if employer_match_input != '':
            try:
                employer_match = float(employer_match_input) / 100
            except ValueError:  
                st.markdown(f"**:red[{employer_match_input}]** Please input a valid percentage.")
                return
        else:
            employer_match = 0.05  # Default to 5% if not entered

        # Base salary input box
        base_salary_input = st.text_input('Enter your base salary', placeholder='e.g. 100000')
        if base_salary_input != '':
            try:
                base_salary = int(base_salary_input)
            except ValueError:  
                st.markdown(f"**:red[{base_salary_input}]** Please input an integer.")
                return
        else:
            base_salary = 0

        # Age input box
        age_input = st.text_input('Enter your age as of Dec 31st', placeholder='e.g. 37')
        if age_input != '':
            try:
                age = int(age_input)
            except ValueError:  
                st.markdown(f"**:red[{age_input}]** Please input an integer.")
                return
        else:
            age = 0

        # 1st bonus input box
        aip_april_input = st.text_input('Enter your 1st half of the year bonus', placeholder='e.g. 5000')
        if aip_april_input != '':
            try:
                aip_april = int(aip_april_input)
            except ValueError:
                st.markdown(f"**:red[{aip_april_input}]** Please input an integer.")
                return
        else:
            aip_april = 0

        # 2nd bonus input box
        aip_october_input = st.text_input('Enter your 2nd half of the year bonus', placeholder='e.g. 2000')
        if aip_october_input != '':
            try:
                aip_october = int(aip_october_input)
            except ValueError:  
                st.markdown(f"**:red[{aip_october_input}]** Please input an integer.")
                return
        else:
            aip_october = 0

        # Pre-tax input box
        pre_tax_percentage_input = st.text_input('Enter your pre-tax contribution percentage', placeholder='e.g. 5')
        if pre_tax_percentage_input != '':
            try:
                pre_tax_percentage = int(pre_tax_percentage_input)
            except ValueError:  
                st.markdown(f"**:red[{pre_tax_percentage_input}]** Please input an integer.")
                return
        else:
            pre_tax_percentage = 0

        # Roth input box
        roth_percentage_input = st.text_input('Enter your Roth contribution percentage', placeholder='e.g. 10')
        if roth_percentage_input != '':
            try:
                roth_percentage = int(roth_percentage_input)
            except ValueError:  
                st.markdown(f"**:red[{roth_percentage_input}]** Please input an integer.")
                return
        else:
            roth_percentage = 0

        # After-tax input box
        after_tax_percentage_input = st.text_input('Enter your after-tax contribution percentage', placeholder='e.g. 15')
        if after_tax_percentage_input != '':
            try:
                after_tax_percentage = int(after_tax_percentage_input)
            except ValueError:  
                st.markdown(f"**:red[{after_tax_percentage_input}]** Please input an integer.")
                return
        else:
            after_tax_percentage = 0

        # Check total contribution percentage input does not exceed 75%
        total_percentage = pre_tax_percentage + roth_percentage + after_tax_percentage
        if total_percentage > 75:
            st.error("Error: Please adjust your contribution percentages to not exceed 75%.")
            return

        # Calculate button
        calculate_button = st.button("Calculate")

    if calculate_button:
        with col2:
            try:
                (
                    breakdown, total_pre_tax, total_roth, total_pre_tax_catch_up, total_roth_catch_up,
                    total_company_match, total_after_tax, total_contributions, estimated_true_up,
                    annual_pre_tax_roth_limit, catch_up_limit, contribution_limit
                ) = calculate_401k_contributions(
                    base_salary, aip_april, aip_october, age,
                    pre_tax_percentage, roth_percentage, after_tax_percentage, add_catch_up, employer_match
                )

                if not breakdown:
                    st.warning("No contributions were made based on the input percentages.")
                    return

                st.markdown("**Annual Contribution Limits**")
                st.markdown(f"  Pre-tax/Roth: :green[${annual_pre_tax_roth_limit:,.0f}]")
                st.markdown(f"  Catch-Up: :green[${catch_up_limit:,.0f}]")
                st.markdown(f"  Total: :green[${contribution_limit:,.0f}]")
                
                st.write("---")
                
                st.markdown("**Total Annual Contributions**")
                st.markdown(f"  Pre-tax: :green[${total_pre_tax:,.2f}]")
                st.markdown(f"  Roth: :green[${total_roth:,.2f}]")
                if age >= 50:
                    st.markdown(f"  Pre-tax catch-up: :green[${total_pre_tax_catch_up:,.2f}]")
                    st.markdown(f"  Roth catch-up: :green[${total_roth_catch_up:,.2f}]")
                else:
                    st.markdown("  Catch-up contributions: N/A")
                st.markdown(f"  Company match: :green[${total_company_match:,.2f}]")
                st.markdown(f"  After-tax: :green[${total_after_tax:,.2f}]")
                st.markdown(f"  Total (not including Estimated True-Up): :green[${total_contributions:,.2f}]")
                st.markdown(f"  Estimated True-Up: :green[${estimated_true_up:,.2f}]")

                st.write("---")
            
            except Exception as e:
                st.error(f"An error occurred: {e}")

            # Create a DataFrame from the breakdown list of dictionaries
            df_breakdown = pd.DataFrame(breakdown)

            # Set 'Period' as the index
            df_breakdown.set_index('Period', inplace=True)

            # Transpose the DataFrame to swap rows and columns
            df_transposed = df_breakdown.transpose()

            # Format numeric values
            numeric_rows = ['Wages This Period', 'Pre-Tax', 'Roth', 'Pre-Tax Catch-Up',
                            'Roth Catch-Up', 'After-Tax', 'Company Match', 'Pre-tax/Roth', 'Catch-Up',
                            'Match', 'Total']

            # Apply formatting to numeric rows
            for row in numeric_rows:
                df_transposed.loc[row] = df_transposed.loc[row].apply(lambda x: '$     -  ' if x==0 else f"${x:,.2f}")

            # Define a function to highlight specific cells when limits are hit
            def highlight_limits(df):
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                for col in df.columns:
                    # Highlight 'Total Pre-tax/Roth Contributions' if limit hit
                    if df_transposed.loc['pre_tax_roth_limit_hit', col]:
                        styles.loc['Pre-tax/Roth', col] = 'background-color: green'
                    if catch_up_limit != 0:
                        # Highlight 'Total Catch-Up Contributions' if limit hit
                        if df_transposed.loc['catch_up_limit_hit', col]:
                            styles.loc['Catch-Up', col] = 'background-color: green'
                    # Highlight 'Total Match Contributions' if limit hit
                    if df_transposed.loc['match_limit_hit', col]:
                        styles.loc['Match', col] = 'background-color: green'
                    # Highlight 'Total Contributions to Date' if total limit hit
                    if df_transposed.loc['total_contribution_limit_hit', col]:
                        styles.loc['Total', col] = 'background-color: green'
                return styles

            # Remove limit hit flags before displaying
            df_transposed_display = df_transposed.drop(['pre_tax_roth_limit_hit', 'catch_up_limit_hit', 'match_limit_hit', 'total_contribution_limit_hit'])

            # Apply the highlighting
            styled_df = df_transposed_display.style.apply(highlight_limits, axis=None)

        # Display the styled DataFrame
        st.subheader("Breakdown of Your Contributions")
        st.markdown(f" **Note:** Blank cells indicate no contributions. :green[Green] cells indicate a limit has been hit.")
        st.write(styled_df)

if __name__ == "__main__":
    main()
