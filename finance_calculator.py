simulation_years = 60
retirement_age = 34

pay_periods_per_year = 26

# savings
free_savings = 102000
locked_savings = 44700
roth_ira = 24332

# incomes
salary = 105000

# outcomes
annual_living_expenses = 40000

# rates
managed_interest_rate = 0.1
tax_free_interest_rate = 0.1
contribution_401k_percent = 0.15
annual_inflation_rate = 0.032
annual_pay_raise = 0.02

# other
pre_tax_check = salary / pay_periods_per_year
age = 24
savings_contribution = 1000
roth_ira_contribution = 250
savings_contribution_percentage = savings_contribution / pre_tax_check
roth_ira_contribution_percentage = roth_ira_contribution / pre_tax_check


# matching function specific per person/company
def get_company_match(pre_tax_check, contribution_401k_percent, age):
    amount = 0
    
    # company match
    if contribution_401k_percent <= 0.03:
        amount += pre_tax_check * contribution_401k_percent
    else:
        amount += pre_tax_check * 0.03

        if contribution_401k_percent <= 0.06:
            amount += 0.333 * pre_tax_check * (contribution_401k_percent - 0.03)
        else:
            amount += 0.333 * pre_tax_check * 0.03

    # company retirement fund
    retirement_match_rates = {
        30   : 0.03,
        35   : 0.035,
        40   : 0.04,
        45   : 0.045,
        50   : 0.05,
        55   : 0.06,
        1000 : 0.07
    }

    for age_limit in retirement_match_rates.keys():
        if age < age_limit:
            amount += pre_tax_check * retirement_match_rates[age_limit]
            break
    
    return amount


def simulate_pay_period(savings, locked_savings, roth_ira, pre_tax_check, contribution_amount, contribution_401k_percent, roth_ira_contribution_percentage, age):
    savings += contribution_amount
    locked_savings += pre_tax_check * contribution_401k_percent + get_company_match(pre_tax_check, contribution_401k_percent, age)
    roth_ira += pre_tax_check * roth_ira_contribution_percentage

    return savings, locked_savings, roth_ira


def withdraw(savings, locked_savings, roth_ira, age, needed_withdraw):
    #if age < 73:
    if age >= 60:
        if locked_savings > 0:
            print("taking from 401k")
            locked_savings -= needed_withdraw
            needed_withdraw = 0
            if locked_savings < 0:
                needed_withdraw = abs(locked_savings)
        if needed_withdraw > 0 and roth_ira > 0:
            print("taking from roth ira")
            roth_ira -= needed_withdraw
            needed_withdraw = 0
            if roth_ira < 0:
                needed_withdraw = abs(roth_ira)
    if needed_withdraw > 0:
        print("taking from savings")
        savings -= needed_withdraw

    #else:
    #    pass # do something about 401k RMD amounts
    
    return savings, locked_savings, roth_ira


def scale_amount_with_inflation(amount, years_elapsed, annual_inflation_rate):
    return amount / (1 + annual_inflation_rate)**years_elapsed


def scale_amount_to_future(amount, years_elapsed, annual_inflation_rate):
    return amount * (1 + annual_inflation_rate)**years_elapsed


def compound_amount(amount, interest_rate):
    return amount * (1 + interest_rate)


print("free matching money:", get_company_match(pre_tax_check, contribution_401k_percent, age))
print("paycheck sim:", simulate_pay_period(free_savings, locked_savings, pre_tax_check, savings_contribution, contribution_401k_percent, age, managed_interest_rate / pay_periods_per_year, True))

print("\n\nraw money:", free_savings, locked_savings, roth_ira)
for year in range(1,simulation_years + 1):
    age += 1

    if retirement_age <= age:
        pre_tax_check = 0
        salary = 0
        contribution_401k_percent = 0
        roth_ira_contribution_percentage = 0
        savings_contribution = 0

    for _ in range(pay_periods_per_year):
        free_savings, locked_savings, roth_ira = simulate_pay_period(free_savings, locked_savings, roth_ira, pre_tax_check, savings_contribution, contribution_401k_percent, roth_ira_contribution_percentage, age)

    free_savings = compound_amount(free_savings, managed_interest_rate)
    locked_savings = compound_amount(locked_savings, tax_free_interest_rate)
    roth_ira = compound_amount(roth_ira, tax_free_interest_rate)

    if retirement_age <= age:
        needed_withdraw = scale_amount_to_future(annual_living_expenses, year, annual_inflation_rate)
        print(f"Withdrawing {str(round(needed_withdraw, 2))} for the year: savings: {str(round(free_savings, 2))}")
        free_savings, locked_savings, roth_ira = withdraw(free_savings, locked_savings, roth_ira, age, needed_withdraw)
        print("savings after withdrawing:", str(round(free_savings, 2)))

    print(f"=== Year {year} stats ===")
    print("age:", age)
    contribution_401k = pre_tax_check * contribution_401k_percent + get_company_match(pre_tax_check, contribution_401k_percent, age)
    print(f"contributions per check: savings {savings_contribution}, 401k {contribution_401k}, roth ira {roth_ira_contribution}")
    print("raw money:", str(round(free_savings,2)), str(round(locked_savings, 2)), str(round(roth_ira, 2)))
    free_savings_with_inflation = str(round(scale_amount_with_inflation(free_savings, year, annual_inflation_rate), 2))
    locked_savings_with_inflation = str(round(scale_amount_with_inflation(locked_savings, year, annual_inflation_rate), 2))
    roth_ira_with_inflation = str(round(scale_amount_with_inflation(roth_ira, year, annual_inflation_rate), 2))
    total_money = free_savings + locked_savings + roth_ira
    total_money_with_inflation = str(round(scale_amount_with_inflation(total_money, year, annual_inflation_rate), 2))
    print("with inflation:", free_savings_with_inflation, locked_savings_with_inflation, roth_ira_with_inflation)
    print("total money accounting for inflation:", total_money_with_inflation)
    salary *= 1 + annual_pay_raise
    pre_tax_check = salary / pay_periods_per_year
    print("New salary:", salary)
    savings_contribution = savings_contribution_percentage * pre_tax_check
    roth_ira_contribution = roth_ira_contribution_percentage * pre_tax_check