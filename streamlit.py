
import streamlit as st

# Function to calculate 401(k) contributions
def calculate_401k_contributions(
    base_salary, aip_april, aip_october, age,
    pre_tax_percentage, roth_percentage, after_tax_percentage
):
    salary_cap = 350000  # IRS salary cap for 401(k) contributions
    annual_pre_tax_roth_limit = 23500  # IRS limit for combined pre-tax and Roth contributions
    catch_up_limit = 7500  # Catch-up contribution limit for age 50+
    contribution_limit = 70000  # Total contribution limit, including employee and employer contributions
    company_match_limit_percentage = 5 / 100  # Company match percentage
    pay_periods = 26  # Number of pay periods

    # Cap the base salary at the IRS salary cap
    base_salary = min(base_salary, salary_cap)

    # Adjust limits if employee is age 50 or older
    if age >= 50:
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
        'total_contribution_limit': False
    }

    breakdown = []

    # Loop through each pay period
    for period in range(1, pay_periods + 1):

        # Initialize limit messages for this period
        period_limit_messages = []
        
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
        if remaining_pre_tax_roth_limit <= 0 and not limits_reached['pre_tax_roth_limit']:
            limits_reached['pre_tax_roth_limit'] = True
            period_limit_messages.append(f"Reached pre-tax/Roth limit of ${annual_pre_tax_roth_limit:,} in this period.")

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
        if remaining_catch_up_limit <= 0 and not limits_reached['catch_up_limit']:
            limits_reached['catch_up_limit'] = True
            period_limit_messages.append(f"Reached catch-up limit of ${catch_up_limit:,} in this period.")

        # Step 5: Calculate company match (simultaneously with pre-tax, Roth, and catch-up contributions)
        max_company_match = salary_per_period * company_match_limit_percentage
        eligible_for_match = pre_tax_contrib + roth_contrib + pre_tax_catch_up_contrib + roth_catch_up_contrib
        company_match_contrib = min(eligible_for_match, max_company_match, remaining_contribution_limit)
        total_company_match += company_match_contrib
        remaining_contribution_limit -= company_match_contrib

        # Update total contributions prior to adding after-tax
        total_contributions = (
            total_pre_tax + total_roth + total_pre_tax_catch_up + total_roth_catch_up +
            total_company_match + total_after_tax
        )

        # Step 6: Calculate after-tax contributions
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

        # Update total contributions post after-tax
        total_contributions = (
            total_pre_tax + total_roth + total_pre_tax_catch_up + total_roth_catch_up +
            total_company_match + total_after_tax
        )

        # Check if total contribution limit reached
        if remaining_contribution_limit <= 0 and not limits_reached['total_contribution_limit']:
            limits_reached['total_contribution_limit'] = True
            period_limit_messages.append(f"Reached total contribution limit of ${contribution_limit:,} in this period.")

        # Calculate total contributions for this period
        period_total_contributions = (
            pre_tax_contrib + roth_contrib + pre_tax_catch_up_contrib +
            roth_catch_up_contrib + company_match_contrib + after_tax_contrib
        )

        # Store the breakdown for this period
        if period_total_contributions > 0:
            breakdown.append({
                'period': period,
                'salary_per_period': salary_per_period,
                'pre_tax': pre_tax_contrib,
                'roth': roth_contrib,
                'pre_tax_catch_up': pre_tax_catch_up_contrib,
                'roth_catch_up': roth_catch_up_contrib,
                'company_match': company_match_contrib,
                'after_tax': after_tax_contrib,
                'total_contributions': total_contributions,
                'limit_messages': period_limit_messages
            })

        # Stop contributions once the overall contribution limit is reached
        if remaining_contribution_limit <= 0:
            break

    # Estimate the true-up contribution based on company match eligibility
    eligible_contributions_for_match = (total_pre_tax + total_roth + total_pre_tax_catch_up + total_roth_catch_up) / base_salary
    expected_company_match = min(eligible_contributions_for_match * base_salary, company_match_limit_percentage * base_salary)
    estimated_true_up = max(0, expected_company_match - total_company_match)

    return (
        breakdown, total_pre_tax, total_roth, total_pre_tax_catch_up, total_roth_catch_up,
        total_company_match, total_after_tax, total_contributions, estimated_true_up,
        annual_pre_tax_roth_limit, catch_up_limit, contribution_limit
    )


# Streamlit App
def main():
    
    st.title(":green[2025 401(k) Contribution Calculator]")
    st.subheader("Estimate your annual contribtions and your contributions per pay period to help determine your contribution percentages.")

    errors = []

    col1, col3, col2 = st.columns([2.5, 0.5, 3])

    with col1:
        #Base salary input box
        base_salary = st.text_input('Enter your base salary', placeholder='e.g. 100000')
        if base_salary != '':
            try:
                base_salary = int(base_salary)
            except ValueError:  
                st.markdown(f"**:red[{base_salary}]** Please input an integer.")
        else:
            base_salary = 0

        #Age input box
        age = st.text_input('Enter your age', placeholder='e.g. 37')
        if age != '':
            try:
                age = int(age)
            except ValueError:  
                st.markdown(f"**:red[{age}]** Please input an integer.")
    
        #1st bonus input box
        aip_april = st.text_input('Enter your 1st half of the year bonus', placeholder='e.g. 5000')
        if aip_april != '':
            try:
                aip_april = int(aip_april)
            except ValueError:
                st.markdown(f"**:red[{aip_april}]** Please input an integer.")

        #2nd bonus input box
        aip_october = st.text_input('Enter your 2nd half of the year bonus', placeholder='e.g. 2000')
        if aip_october != '':
            try:
                aip_october = int(aip_october)
            except ValueError:  
                st.markdown(f"**:red[{aip_october}]** Please input an integer.")
            
        #PT input box
        pre_tax_percentage = st.text_input('Enter your pre-tax contribution percentage', placeholder='e.g. 5')
        if pre_tax_percentage != '':
            try:
                pre_tax_percentage = int(pre_tax_percentage)
            except ValueError:  
                st.markdown(f"**:red[{pre_tax_percentage}]** Please input an integer.")
            
        #Roth input box
        roth_percentage = st.text_input('Enter your Roth contribution percentage', placeholder='e.g. 10')
        if roth_percentage != '':
            try:
                roth_percentage = int(roth_percentage)
            except ValueError:  
                st.markdown(f"**:red[{roth_percentage}]** Please input an integer.")
            
        #AT input box
        after_tax_percentage = st.text_input('Enter your after-tax contribution percentage', placeholder='e.g. 15')
        if after_tax_percentage != '':
            try:
                after_tax_percentage = int(after_tax_percentage)
            except ValueError:  
                st.markdown(f"**:red[{after_tax_percentage}]** Please input an integer.")
            
    # Check total contribution percentage input does not exceed 75%
    try:
        total_percentage = pre_tax_percentage + roth_percentage + after_tax_percentage
    except TypeError:
        print("Type Error")
    
    try:
        if total_percentage > 75:
            st.error("Error: Please adjust your contribution percentages to not exceed 75%.")
            return
    except TypeError:
        print("Type Error 2")
    except UnboundLocalError:
        print("Unbound Local Error")

    with col3:
        print("")
        
    # Calculate and display results when the button is clicked
    if st.button("Calculate"):
        with col2:
            try:
                (
                    breakdown, total_pre_tax, total_roth, total_pre_tax_catch_up, total_roth_catch_up,
                    total_company_match, total_after_tax, total_contributions, estimated_true_up,
                    annual_pre_tax_roth_limit, catch_up_limit, contribution_limit
                ) = calculate_401k_contributions(
                    base_salary, aip_april, aip_october, age,
                    pre_tax_percentage, roth_percentage, after_tax_percentage
                )

                if not breakdown:
                    st.warning("No contributions were made based on the input percentages.")
                    return

                st.markdown("**Your Annual Contribution Limits**")
                st.markdown(f"  Pre-tax/Roth Limit: :green[${annual_pre_tax_roth_limit:,.0f}]")
                st.markdown(f"  Catch-Up: :green[${catch_up_limit:,.0f}]")
                st.markdown(f"  Total: :green[${contribution_limit:,.0f}]")
                
                st.write("---")
                
                st.markdown("**Your Total Annual Contributions**")
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

            except Exception as e:
                st.error(f"An error occurred: {e}")

        st.markdown("""
            <style>
                [data-testid="column"]:nth-child(2){
                    background-color: lightgrey;
                }
            </style>
            """, unsafe_allow_html=True
        )

        try:
                st.subheader("Breakdown of Your Contributions per Pay Period")
                for row in breakdown:
                    st.markdown(f"**Pay Period :green[{row['period']}]**")
                    if row['period'] == 8:
                        st.markdown("  :red[*1st half of the year bonus added to your wages this pay period*]")
                    elif row['period'] == 21:
                        st.markdown("  :red[*2nd half of the year bonus added to your wages this pay period*]")
                    st.markdown(f"  Wages this pay period: :green[${row['salary_per_period']:,.2f}]")
                    st.markdown(f"  Pre-tax: :green[${row['pre_tax']:,.2f}]")
                    st.markdown(f"  Roth: :green[${row['roth']:,.2f}]")
                    if age >= 50:
                        st.markdown(f"  Pre-tax catch-up: :green[${row['pre_tax_catch_up']:,.2f}]")
                        st.markdown(f"  Roth catch-up: :green[${row['roth_catch_up']:,.2f}]")
                    st.markdown(f"  Company match: :green[${row['company_match']:,.2f}]")
                    st.markdown(f"  After-tax: :green[${row['after_tax']:,.2f}]")
                    st.markdown(f"  Total contributions as of this period: :green[${row['total_contributions']:,.2f}]")

                    # Display any limit messages for this period
                    for message in row['limit_messages']:
                        st.warning(f"  **{message}**")

                    st.write("---")

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
