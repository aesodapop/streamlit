#link - https://nxp-401k-calc.streamlit.app/

import streamlit as st
import pandas as pd

# Function to calculate 401(k) contributions
def calculate_401k_contributions(
    base_salary, aip_april, aip_october, age,
    pre_tax_percentage, roth_percentage, after_tax_percentage, merit_increase, merit_time, pre_tax_effective, roth_effective, after_tax_effective, pt_ytd, r_ytd, pt_cu_ytd, r_cu_ytd,
    m_ytd, at_ytd
):
    salary_cap = 350000  # IRS salary cap for 401(k) contributions
    annual_pre_tax_roth_limit = 23500  # IRS limit for combined pre-tax and Roth contributions
    catch_up_limit = 7500  # Catch-up contribution limit for age 50+
    add_catch_up_limit = 3750  # Additional catch-up for ages 60-63
    contribution_limit = 70000  # Total contribution limit, including employee and employer contributions
    pay_periods = 26  # Number of pay periods
    employer_match = 0.05
    match_limit = 17500

    match_limit = min(base_salary + aip_april + aip_october, salary_cap) * employer_match
    

    # Cap the base salary at the IRS salary cap
    base_salary = min(base_salary, salary_cap)
    

    # Adjust limits
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

    total_pre_tax = 0 + pt_ytd
    total_roth = 0 + r_ytd
    total_pre_tax_catch_up = 0 + pt_cu_ytd
    total_roth_catch_up = 0 + r_cu_ytd
    total_after_tax = 0 + at_ytd
    total_company_match = 0 + m_ytd
    total_contributions = 0
    salary_per_period = 0
    merit_increase = merit_increase / 100

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

        #merit calculations 
        if merit_increase == 0:
            salary_per_period = base_salary / pay_periods
        elif merit_increase > 0:
            if period >= merit_time:
                salary_per_period = (base_salary * (1 + merit_increase)) / pay_periods
            else:
                salary_per_period = base_salary / pay_periods 

        # Calculate salary per period and include AIP if applicable
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
        if pre_tax_effective <= period:
            pre_tax_contrib = min(pre_tax_contrib_desired, remaining_pre_tax_roth_limit, remaining_contribution_limit)
            total_pre_tax += pre_tax_contrib
            remaining_contribution_limit -= pre_tax_contrib
            # Update remaining pre-tax/Roth limit after contributions
            remaining_pre_tax_roth_limit -= pre_tax_contrib
        else:
            pre_tax_contrib = 0

        # Step 2: Calculate Roth contributions
        if roth_effective <= period:
            roth_contrib = min(roth_contrib_desired, remaining_pre_tax_roth_limit, remaining_contribution_limit)
            total_roth += roth_contrib
            remaining_contribution_limit -= roth_contrib
            # Update remaining pre-tax/Roth limit after contributions
            remaining_pre_tax_roth_limit -= roth_contrib
        else:
            roth_contrib = 0

        # Check if pre-tax/Roth limit reached
        if remaining_pre_tax_roth_limit <= 0:
            limits_reached['pre_tax_roth_limit'] = True
            period_limits_hit['pre_tax_roth_limit_hit'] = True
 
        # Step 3: Calculate pre-tax catch-up contributions
        if pre_tax_effective <= period:
            pre_tax_catch_up_contrib = 0
            if age >= 50 and remaining_catch_up_limit > 0 and remaining_contribution_limit > 0:
                pre_tax_catch_up_contrib_desired = max(0, pre_tax_contrib_desired - pre_tax_contrib)
                pre_tax_catch_up_contrib = min(pre_tax_catch_up_contrib_desired, remaining_catch_up_limit, remaining_contribution_limit)
                total_pre_tax_catch_up += pre_tax_catch_up_contrib
                remaining_contribution_limit -= pre_tax_catch_up_contrib
                remaining_catch_up_limit -= pre_tax_catch_up_contrib
        else:
            pre_tax_catch_up_contrib = 0

        # Step 4: Calculate Roth catch-up contributions
        if roth_effective <= period:
            roth_catch_up_contrib = 0
            if age >= 50 and remaining_catch_up_limit > 0 and remaining_contribution_limit > 0:
                roth_catch_up_contrib_desired = max(0, roth_contrib_desired - roth_contrib)
                roth_catch_up_contrib = min(roth_catch_up_contrib_desired, remaining_catch_up_limit, remaining_contribution_limit)
                total_roth_catch_up += roth_catch_up_contrib
                remaining_contribution_limit -= roth_catch_up_contrib
                remaining_catch_up_limit -= roth_catch_up_contrib
        else:
            roth_catch_up_contrib = 0

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
        if after_tax_effective <= period:
            after_tax_contrib = 0
            if total_contributions >= contribution_limit - catch_up_limit and remaining_catch_up_limit > 0:
                after_tax_contrib = 0
            elif total_contributions < contribution_limit - catch_up_limit and total_contributions + after_tax_contrib_desired > contribution_limit - catch_up_limit and remaining_catch_up_limit > 0:
                after_tax_contrib = (contribution_limit - catch_up_limit) - total_contributions
                total_after_tax += after_tax_contrib
                remaining_contribution_limit -= after_tax_contrib
            else:
                after_tax_contrib = min(after_tax_contrib_desired, remaining_contribution_limit)
                total_after_tax += after_tax_contrib
                remaining_contribution_limit -= after_tax_contrib
        else:
            after_tax_contrib = 0

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
        if period_total_contributions >= 0:
            breakdown.append({
                'Period': period,
                'Wages for Period': salary_per_period,
                'CONTRIBUTIONS FOR PERIOD': '',
                'Pre-Tax': pre_tax_contrib,
                'Roth': roth_contrib,
                'Pre-Tax Catch-Up': pre_tax_catch_up_contrib,
                'Roth Catch-Up': roth_catch_up_contrib,
                'Match': company_match_contrib,
                'After-Tax': after_tax_contrib,
                'CONTRIBUTIONS TO DATE': '',
                'Pre-tax/Roth': total_pre_tax + total_roth,
                'Catch-Up': total_pre_tax_catch_up + total_roth_catch_up,
                'Match ': total_company_match,
                'After-Tax ': total_after_tax,
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
    expected_match_percent = min(employer_match, eligible_contributions_for_match / (base_salary + aip_october + aip_april))

    expected_company_match = expected_match_percent * (base_salary + aip_april + aip_october)

    if total_company_match != expected_company_match:
        estimated_true_up = max(expected_company_match - total_company_match, 0)
    else:
        estimated_true_up = 0

    total_annual_contribs = estimated_true_up + total_contributions

    return (
        breakdown, total_pre_tax, total_roth, total_pre_tax_catch_up, total_roth_catch_up,
        total_company_match, total_after_tax, total_contributions, estimated_true_up,
        annual_pre_tax_roth_limit, catch_up_limit, add_catch_up_limit, contribution_limit, match_limit, total_annual_contribs
    )


# Streamlit App
def main():

    st.header('401(k) Contribution Calculator')
    st.markdown("To determine what to set your contribution percentages to for 2025 enter your Wage Information & Test Contributions below. The YTD Contributions information is not required. Note these are estimates and the output may not be exact.")
    st.markdown(" ")

    errors = []

    col1, col3, col2 = st.columns([3.0, 0.5, 3.0])

    with col1:

        #st.write("**Wage Info**")
        st.subheader("Wage Info", help="Enter your wage/age information.")

        # Base salary input box
        base_salary_input = st.text_input('Base salary', placeholder='e.g. 100000')
        if base_salary_input != '':
            try:
                base_salary = float(base_salary_input)
            except ValueError:  
                st.markdown(f"**:red[{base_salary_input}]** Please input a number.")
                return
        else:
            base_salary = 0
            
        # Age input box
        age_input = st.text_input('Age as of Dec 31st', placeholder='e.g. 37')
        if age_input != '':
            try:
                age = int(age_input)
            except ValueError:  
                st.markdown(f"**:red[{age_input}]** Please input an integer.")
                return
        else:
            age = 0

        # 1st bonus input box
        aip_april_input = st.text_input('1st half of the year bonus', placeholder='e.g. 5000')
        if aip_april_input != '':
            try:
                aip_april = float(aip_april_input)
            except ValueError:
                st.markdown(f"**:red[{aip_april_input}]** Please input a number.")
                return
        else:
            aip_april = 0

        # 2nd bonus input box
        aip_october_input = st.text_input('2nd half of the year bonus', placeholder='e.g. 2000')
        if aip_october_input != '':
            try:
                aip_october = float(aip_october_input)
            except ValueError:  
                st.markdown(f"**:red[{aip_october_input}]** Please input a number.")
                return
        else:
            aip_october = 0

        # Merit increase input box
        merit_increase_input = st.text_input('If applicable, merit increase %', placeholder='e.g. 7')
        if merit_increase_input != '':
            try:
                merit_increase = int(merit_increase_input)
            except ValueError:  
                st.markdown(f"**:red[{merit_increase_input}]** Please input an integer.")
                return
        else:
            merit_increase = 0

        # Merit increase input box
        merit_time_input = st.text_input('If applicable, pay period your merit starts', placeholder='e.g. 7')
        if merit_time_input != '':
            try:
                merit_time = int(merit_time_input)
            except ValueError:  
                st.markdown(f"**:red[{merit_time_input}]** Please input an integer.")
                return
        else:
            merit_time = 0

        st.write("\n")
        #st.write("**Current Contributions**")
        st.subheader("Test Contributions", help="Enter your current or test contribution rates & the pay period your contributions to start. If your contributions start in pay period 1, then you can leave the input box empty.")

        #pre-tax input box
        pre_tax_percentage_input = st.text_input('Pre-Tax contribution %', placeholder='e.g. 5')
        if pre_tax_percentage_input != '':
            try:
               pre_tax_percentage = int(pre_tax_percentage_input)
            except ValueError:  
                st.markdown(f"**:red[{pre_tax_percentage_input}]** Please input an integer.")
                return
        else:
            pre_tax_percentage = 0

        #roth input box
        roth_percentage_input = st.text_input('Roth contribution %', placeholder='e.g. 10')
        if roth_percentage_input != '':
            try:
                roth_percentage = int(roth_percentage_input)
            except ValueError:  
                st.markdown(f"**:red[{roth_percentage_input}]** Please input an integer.")
                return
        else:
            roth_percentage = 0
        
        #after-tax input box
        after_tax_percentage_input = st.text_input('After-Tax contribution %', placeholder='e.g. 15')
        if after_tax_percentage_input != '':
            try:
                after_tax_percentage = int(after_tax_percentage_input)
            except ValueError:  
                st.markdown(f"**:red[{after_tax_percentage_input}]** Please input an integer.")
                return
        else:
            after_tax_percentage = 0


        # Calculate button
        calculate_button = st.button("Calculate")

    with col2:

        #st.write("**YTD Contributions**")
        st.subheader("YTD Contributions", help="Enter your Year to Date (YTD) contributions that may have already occurred. If you don't have YTD contributions, then leave the input box empty.")
        
        #PT YTD input box
        pt_ytd_input = st.text_input('Year to Date Pre-Tax Contributions', placeholder='e.g. 1000')
        if pt_ytd_input != '':
            try:
                pt_ytd = float(pt_ytd_input)
            except ValueError:  
                st.markdown(f"**:red[{pt_ytd_input}]** Please input a number.")
                return
        else:
            pt_ytd = 0

        #Pre-Tax Catch-Up YTD input box
        if age > 49:
            pt_cu_ytd_input = st.text_input('Year to Date Pre-Tax Catch-Up Contributions', placeholder='e.g. 1500')
            if pt_cu_ytd_input != '':
                try:
                    pt_cu_ytd = float(pt_cu_ytd_input)
                except ValueError:  
                    st.markdown(f"**:red[{pt_cu_ytd_input}]** Please input a number.")
                    return
            else:
                pt_cu_ytd = 0
        else: pt_cu_ytd = 0

        #Roth YTD input box
        r_ytd_input = st.text_input('Year to Date Roth Contributions', placeholder='e.g. 500')
        if r_ytd_input != '':
            try:
                r_ytd = float(r_ytd_input)
            except ValueError:  
                st.markdown(f"**:red[{r_ytd_input}]** Please input a number.")
                return
        else:
            r_ytd = 0

        #Roth Catch-Up YTD input box
        if age > 49:
            r_cu_ytd_input = st.text_input('Year to Date Roth Catch-Up Contributions', placeholder='e.g. 0')
            if r_cu_ytd_input != '':
                try:
                    r_cu_ytd = float(r_cu_ytd_input)
                except ValueError:  
                    st.markdown(f"**:red[{r_cu_ytd_input}]** Please input a number.")
                    return
            else:
                r_cu_ytd = 0
        else: r_cu_ytd = 0

        #NXP Match YTD input box
        m_ytd_input = st.text_input('Year to Date NXP Match Contributions', placeholder='e.g. 500')
        if m_ytd_input != '':
            try:
                m_ytd = float(m_ytd_input)
            except ValueError:  
                st.markdown(f"**:red[{m_ytd_input}]** Please input a number.")
                return
        else:
            m_ytd = 0

        #NXP After-Tax YTD input box
        at_ytd_input = st.text_input('Year to Date After-Tax Contributions', placeholder='e.g. 1000')
        if at_ytd_input != '':
            try:
                at_ytd = float(at_ytd_input)
            except ValueError:  
                st.markdown(f"**:red[{at_ytd_input}]** Please input a number.")
                return
        else:
            at_ytd = 0

        st.write("\n")
        st.write("\n")
        st.write("\n")

        if age < 50:
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write("\n")

        if age > 49:
            st.write("\n")
            st.write("\n")
        
        pt_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]

        pre_tax_effective_input = st.selectbox('The pay period your Pre-Tax contributions start', pt_list, index=0)
        pre_tax_effective = int(pre_tax_effective_input)

        # #pre-tax effective input box
        # pre_tax_effective_input = st.text_input('The pay period your Pre-Tax contributions start', placeholder='e.g. 1')
        # if pre_tax_effective_input != '':
        #     try:
        #         pre_tax_effective = int(pre_tax_effective_input)
        #     except ValueError:  
        #         st.markdown(f"**:red[{pre_tax_effective_input}]** Please input an integer.")
        #         return
        # else:
        #     pre_tax_effective = 1

        roth_effective_input = st.selectbox('The pay period your Roth contributions start', pt_list, index=0)
        roth_effective = int(roth_effective_input)

        # #roth effective input box
        # roth_effective_input = st.text_input('The pay period your Roth contributions start', placeholder='e.g. 5')
        # if roth_effective_input != '':
        #     try:
        #         roth_effective = int(roth_effective_input)
        #     except ValueError:  
        #         st.markdown(f"**:red[{roth_effective_input}]** Please input an integer.")
        #         return
        # else:
        #     roth_effective = 1

        after_tax_effective_input = st.selectbox('The pay period your After-Tax contributions start', pt_list, index=0)
        after_tax_effective = int(after_tax_effective_input)

        # #after-tax effective input box
        # after_tax_effective_input = st.text_input('The pay period your After-Tax contributions start', placeholder='e.g. 26')
        # if after_tax_effective_input != '':
        #     try:
        #         after_tax_effective = int(after_tax_effective_input)
        #     except ValueError:  
        #         st.markdown(f"**:red[{after_tax_effective_input}]** Please input an integer.")
        #         return
        # else:
        #     after_tax_effective = 1

        # Check total contribution percentage input does not exceed 75%
        total_percentage = pre_tax_percentage + roth_percentage + after_tax_percentage
        if total_percentage > 75:
            st.error("Error: Please adjust your contribution percentages to not exceed 75%.")
            return
        

    if calculate_button:
        with col1:
            try:
                (
                    breakdown, total_pre_tax, total_roth, total_pre_tax_catch_up, total_roth_catch_up,
                    total_company_match, total_after_tax, total_contributions, estimated_true_up,
                    annual_pre_tax_roth_limit, catch_up_limit, add_catch_up_limit, contribution_limit, match_limit, total_annual_contribs
                ) = calculate_401k_contributions(
                    base_salary, aip_april, aip_october, age,
                    pre_tax_percentage, roth_percentage, after_tax_percentage, merit_increase, merit_time, pre_tax_effective, roth_effective, after_tax_effective, pt_ytd, r_ytd, pt_cu_ytd, r_cu_ytd,
                    m_ytd, at_ytd
                )

                if not breakdown:
                    st.warning("No contributions were made based on the input percentages.")
                    return
                
                st.subheader("Annual Contributions")
                #st.write("**Annual Contributions**")
                st.markdown(f"  Pre-tax: :blue[${total_pre_tax:,.2f}]")
                st.markdown(f"  Roth: :blue[${total_roth:,.2f}]")
                if age >= 50:
                    st.markdown(f"  Pre-tax catch-up: :blue[${total_pre_tax_catch_up:,.2f}]")
                    st.markdown(f"  Roth catch-up: :blue[${total_roth_catch_up:,.2f}]")
                else:
                    st.markdown("  Catch-Up: :blue[N/A]")
                st.markdown(f"  NXP Match: :blue[${total_company_match:,.2f}]")
                st.markdown(f"  After-tax: :blue[${total_after_tax:,.2f}]")
                st.markdown(f"  Total (excluding True-Up): :blue[${total_contributions:,.2f}]")
                st.markdown(f"  True-Up: :blue[${estimated_true_up:,.2f}]")
                if estimated_true_up + total_contributions > contribution_limit:
                    st.markdown(f"  Total (including True-Up): :red[${total_annual_contribs:,.2f}]")
                    #st.markdown(f"  :red[By our estimates your true-up will push you over the annual contribution limit, which results in Fidelity processing a refund of that excess contribuion amount potentially with a penalty. If you want to avoid exceeding the limit, you should consider reducing your after-tax contribution %.]")
                else:
                    st.markdown(f"  Total (including True-Up): :blue[${total_annual_contribs:,.2f}]")
            
            except Exception as e:
                st.error(f"An error occurred: {e}")

        with col2:
            try:
                (
                    breakdown, total_pre_tax, total_roth, total_pre_tax_catch_up, total_roth_catch_up,
                    total_company_match, total_after_tax, total_contributions, estimated_true_up,
                    annual_pre_tax_roth_limit, catch_up_limit, add_catch_up_limit, contribution_limit, match_limit, total_annual_contribs
                ) = calculate_401k_contributions(
                    base_salary, aip_april, aip_october, age,
                    pre_tax_percentage, roth_percentage, after_tax_percentage, merit_increase, merit_time, pre_tax_effective, roth_effective, after_tax_effective, pt_ytd, r_ytd, pt_cu_ytd, r_cu_ytd,
                    m_ytd, at_ytd
                )

                if not breakdown:
                    st.warning("No contributions were made based on the input percentages.")
                    return

                #st.markdown("**Annual Contribution Limits**")
                st.markdown("\n")
                st.markdown("\n")
                st.markdown("\n")

                st.subheader("Annual Limits")
                #st.write("**Annual Limits**")

                st.markdown(f"  Pre-tax/Roth: :blue[${annual_pre_tax_roth_limit:,.0f}]")
                st.markdown(f"  Catch-Up: :blue[${catch_up_limit:,.0f}]")
                st.markdown(f"  NXP Match: :blue[${match_limit:,.0f}]")
                st.markdown(f"  Total (including Catch-Up): :blue[${contribution_limit:,.0f}]")
                
                #st.write("---")

            except Exception as e:
                st.error(f"An error occurred: {e}")
                

        if estimated_true_up + total_contributions > contribution_limit:
            st.markdown(f"  :red[By our estimates your true-up will push you over the annual contribution limit, which results in Fidelity processing a refund of that excess contribuion amount. If you want to avoid exceeding the limit, you should consider reducing your after-tax contribution percentage.]")


        # Create a DataFrame from the breakdown list of dictionaries
        df_breakdown = pd.DataFrame(breakdown)

        # Set 'Period' as the index
        df_breakdown.set_index('Period', inplace=True)

        # Transpose the DataFrame to swap rows and columns
        df_transposed = df_breakdown.transpose()

        # Format numeric values
        numeric_rows = ['Wages for Period', 'Pre-Tax', 'Roth', 'Pre-Tax Catch-Up',
                        'Roth Catch-Up', 'After-Tax', 'Match', 'Pre-tax/Roth', 'Catch-Up',
                        'Match ', 'After-Tax ', 'Total']

        # Apply formatting to numeric rows
        for row in numeric_rows:
            df_transposed.loc[row] = df_transposed.loc[row].apply(lambda x: '    -  ' if x==0 else f"${x:,.2f}")

        # Define a function to highlight specific cells when limits are hit
        def highlight_limits(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            for col in df.columns:
                # Highlight 'Total Pre-tax/Roth Contributions' if limit hit
                if df_transposed.loc['pre_tax_roth_limit_hit', col]:
                    styles.loc['Pre-tax/Roth', col] = 'background-color: #1E88E5'
                if catch_up_limit != 0:
                    # Highlight 'Total Catch-Up Contributions' if limit hit
                    if df_transposed.loc['catch_up_limit_hit', col]:
                        styles.loc['Catch-Up', col] = 'background-color: #1E88E5'
                # Highlight 'Total Match Contributions' if limit hit
                if df_transposed.loc['match_limit_hit', col]:
                    styles.loc['Match', col] = 'background-color: #1E88E5'
                # Highlight 'Total Contributions to Date' if total limit hit
                if df_transposed.loc['total_contribution_limit_hit', col]:
                    styles.loc['Total', col] = 'background-color: #1E88E5'
            return styles

        # Remove limit hit flags before displaying
        df_transposed_display = df_transposed.drop(['pre_tax_roth_limit_hit','catch_up_limit_hit', 'match_limit_hit', 'total_contribution_limit_hit'])

        # Apply the highlighting
        styled_df = df_transposed_display.style.apply(highlight_limits, axis=None)

        # Display the styled DataFrame
        st.write("\n")
        st.subheader("Breakdown of Your Contributions", help="See your contributions broken down over each pay period in the chart below. The top section shows your wages, the section below that shows your Contributions for Each Pay Period, and the section below that shows your Contribution Totals as of the end of each pay period.")
        st.markdown(f" :blue[Blue] cells indicate a limit has been hit and contributions of that type have stopped")
        st.write(styled_df)
        st.subheader("Definitions")
        st.write(f'Wages for Pay Period - your eligible earnings each pay period including Annual Incentive Payments, Sales Incentive Payments, shift differentials, overtime and lump-sum pay')
        st.write(f'Pre-Tax - contributions to the Plan made on a before-tax basis (before federal and most state income taxes, but not before FICA social secutiry and medicare taxes)')
        st.write(f'Roth - contributions to the Plan made on a after-tax basis, and under certain tax law, if certain requirements are met, Roth contributions and their investment earnings are not taxable when you take them as a qualified distribution')
        st.write(f'After-tax - contributions to the Plan made on a after-tax basis and are not eligible for NXP matching contributions')
        st.write(f'Catch-up - additional pre-tax and/or Roth contributions are allowed if you are: ages 50-59 or 64+, or ages 60-63)')
        st.write(f'True-up - if at the end of the year, you have not received your maximum match you were eligibe for, then NXP will make a true-up contribution in the following January to bring you up to the maximum NXP match')
        st.write(f'')
        st.write(f'')
        st.write(f' :blue[**Disclaimer** this calculator provides estimates and may not be exact]')

if __name__ == "__main__":
    main()
