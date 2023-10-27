import numpy as np
import datetime as dt
import re

class Bond():
    def __init__(self, coupon:float, maturity_date: dt.date):
        if coupon >=0 and coupon < 1:
            self.coupon = coupon
        else:
            raise ErrorValue("incorrect coupon")
        if isinstance(maturity_date, dt.date):
            self.maturity_date = maturity_date
        self._recovery = 0.4
        self.trade_date = dt.datetime.now().date()
    def __str__(self):
        return f"Bond {self.coupon*100}% due {self.maturity_date}, recovery: {self._recovery*100}%"

    @property
    def recovery(self):
        return self._recovery

    @recovery.setter
    def recovery(self, recovery_rate):
        if recovery_rate < 0:
            raise ValueError("Recovery rate must be positive")
        elif recovery_rate >= 1:
            raise ValueError("Recovery rate must be less than 1 or 100%")
        else:
            self._recovery = recovery_rate

    def value_bond_from_price(self, trade_date: dt.datetime, price: float, interest_rate: float):
        settlement_date = get_settlement_date_from_trade_date(trade_date)
        tenor_in_years = (self.maturity_date - settlement_date).days / 365.25
        if tenor_in_years > 0:
            spread = bond_spread(tenor_in_years, self.coupon, interest_rate, price, self.recovery)
            if not np.isnan(spread):
                cr01 = bond_cr01(tenor_in_years, self.coupon, interest_rate, spread, self.recovery)
                ir01 = bond_ir01(tenor_in_years, self.coupon, interest_rate, spread, self.recovery)
                return spread, cr01, ir01
            else:
                print(f"Cannot imply bond price of: {price:,.3f}")
        else:
            print(f"Bond has matured as of {trade_date.date()}")

    def value_bond_from_spread(self, trade_date: dt.datetime, spread: float, interest_rate: float):
        settlement_date = get_settlement_date_from_trade_date(trade_date)
        tenor_in_years = (self.maturity_date - settlement_date).days / 365.25
        if tenor_in_years > 0:
            price = bond_price(tenor_in_years, self.coupon, interest_rate, spread, self.recovery)
            cr01 = bond_cr01(tenor_in_years, self.coupon, interest_rate, spread, self.recovery)
            ir01 = bond_ir01(tenor_in_years, self.coupon, interest_rate, spread, self.recovery)
            return price, cr01, ir01


def extract_date_from_string(s: str) -> dt.date:
    try:
        if matched := re.search(r"([0-9]+)-([0-9]+)-([0-9]{4})", s):
            day = int(matched[1])
            month =int(matched[2])
            year = int(matched[3])
        elif matched := re.search(r"([0-9]+)/([0-9]+)/([0-9]{4})", s):
            day = int(matched[1])
            month =int(matched[2])
            year = int(matched[3])
        return dt.date(year, month, day)
    except:
        print("Wrong date format")



def get_settlement_date_from_trade_date(trade_date: dt.date) -> dt.date:
    weekday = trade_date.weekday()
    if weekday in [3, 4, 5]:
        return (trade_date + dt.timedelta(4))
    elif weekday == 6:
        return (trade_date + dt.timedelta(3))
    else:
        return (trade_date + dt.timedelta(2))



def bond_price(maturity: np.array,
               coupon:np.array,
               interest_rate:np.array,
               spread: np.array,
               recovery_rate:np.array) -> np.array:
    """
    vectorized function to compute the price of a bond from spread and recovery rate
    returns an array of price in absolute value (i.e. for a notional of 1)
    returns nan if default_intensity_plus_interest_rate is null
    """
    one_minus_recovery = np.add(1,-recovery_rate)
    default_intensity = np.divide(spread, one_minus_recovery) # aka hazard rate
    default_intensity_plus_interest_rate = np.add(default_intensity, interest_rate)
    ir_plus_lambda_times_t = np.multiply(default_intensity_plus_interest_rate, maturity)
    discount_to_maturity = np.exp(-ir_plus_lambda_times_t)
    integral = np.divide(np.add(1,-discount_to_maturity), default_intensity_plus_interest_rate)
    sum_discounted_coupon = np.multiply(coupon, integral)
    recovery_discounted = np.multiply(recovery_rate,np.multiply(default_intensity, integral))
    return np.add(np.add(discount_to_maturity, sum_discounted_coupon),recovery_discounted)

def bond_cr01(maturity: np.array,
               coupon:np.array,
               interest_rate:np.array,
               spread: np.array,
               recovery_rate:np.array) -> np.array:
    """
    vectorized function to compute the price sensitivity of a bond for a bump of 1 basis point of the credit spread
    returns an array of CR01 in absolute term
    returns nan if sum of interest rate and default intensity is null
    """
    spread_bump = 1e-4
    spread_plus_1_basis_point = np.add(spread, spread_bump)
    spread_minus_1_basis_point = np.add(spread, -spread_bump)

    price_plus_1_basis_point = bond_price(maturity, coupon, interest_rate, spread_plus_1_basis_point, recovery_rate)
    price_minus_1_basis_point = bond_price(maturity, coupon, interest_rate, spread_minus_1_basis_point, recovery_rate)
    return (price_plus_1_basis_point - price_minus_1_basis_point) / 2 / spread_bump / 1e2


def bond_ir01(maturity: np.array,
               coupon:np.array,
               interest_rate:np.array,
               spread: np.array,
               recovery_rate:np.array) -> np.array:
    """
    vectorized function to compute the price sensitivity of a bond for a bump of 1 basis point of the interest rate
    returns an array or IR01 in absolute term
    returns nan if sum of spread and default intensity is null
    """
    ir_bump = 1e-4
    ir_plus_1_basis_point = np.add(interest_rate, ir_bump)
    ir_minus_1_basis_point = np.add(interest_rate, -ir_bump)

    price = bond_price(maturity, coupon, interest_rate, spread, recovery_rate)
    price_plus_1_basis_point = bond_price(maturity, coupon, ir_plus_1_basis_point, spread, recovery_rate)
    price_minus_1_basis_point = bond_price(maturity, coupon, ir_minus_1_basis_point, spread, recovery_rate)
    return (price_plus_1_basis_point - price_minus_1_basis_point) / 2 / ir_bump / 1e2

def bond_spread(maturity: np.array,
               coupon:np.array,
               interest_rate:np.array,
               price: np.array,
               recovery_rate:np.array,
               max_number_of_loop:int = 15) -> np.array:
    """
    vectorized function to compute the credit spread that matches a bond price given in percent for a given recovery rate
    returns an array of spread in absolute value

    """
    # first ensure recovery ate is positive and at least 10% below the bond market price to ensure the spread can be implied
    recovery_rate = np.clip(recovery_rate, 0, np.subtract(np.divide(price,100), 0.1))
    # makes a first estimate of the yield of the bond using bond price, years to maturity and coupon, then substract interest rate to get spread
    spread_guess = np.subtract(np.divide(np.add(coupon, np.divide(np.subtract(100,price), maturity)/100), np.add(price, 100)/2)*100, interest_rate)
    price_theoretical = 100 * bond_price(maturity,coupon, interest_rate, spread_guess, recovery_rate)
    counter = 0
    # from starting spread, iterate the calculatio of the spread using a Newton-Raphson method on the bond price
    while counter < max_number_of_loop and np.max(np.abs(np.subtract(price_theoretical, price))) > 1e-6:
        cr01 = bond_cr01(maturity, coupon, interest_rate, spread_guess, recovery_rate)
        spread_guess = spread_guess + np.divide(np.subtract(price, price_theoretical), cr01) / 10_000
        price_theoretical = 100 * bond_price(maturity,coupon, interest_rate, spread_guess, recovery_rate)
        counter += 1
    return spread_guess

def create_bond_object_from_prompt():
    bond_maturity_str = input("What is the maturity date of the bond (format dd-mm-yyyy): ")
    bond_coupon_str = input("What is the coupon of the bond in percent (5 for a 5% coupon): ")
    bond_maturity = extract_date_from_string(bond_maturity_str)
    bond_coupon = float(bond_coupon_str) / 100
    if isinstance(bond_maturity, dt.date) and bond_coupon > 0 and bond_coupon < 1:
        return Bond(bond_coupon, bond_maturity)
    else:
        return None

def price_bond_from_prompt(bond: Bond):
    counter = 0
    while counter < 3:
        try:
            type_pricing = input("Do you want to get the CR01 and IR01 from credit spread (type s) or from bond price (type p)? Type e to exit: ")
            if type_pricing.lower() in ['e','exit']:
                break
            else:
                counter += 1
                trade_date_str = input(f"What is the trading date using format: dd-mm-yyyy (leave empty to use current {bond.trade_date.strftime('%d-%m-%y')}): ")
                if trade_date_str in ["","\n"," \n","  \n"]:
                    trade_date = bond.trade_date
                else:
                    trade_date = extract_date_from_string(trade_date_str)
                    if isinstance(trade_date, dt.date):
                        bond.trade_date = trade_date
                interest_rate_str = input("What is the interest rate in percent (4 for a 4% interest rate): ")
                interest_rate = float(interest_rate_str) / 100
                if type_pricing.lower() in ['p','price']:
                    bond_price_str = input("What is the (clean) price of the bond in percent (100 for a bond trading at par value): ")
                    bond_valuation_from_price = bond.value_bond_from_price(trade_date, float(bond_price_str), interest_rate)
                    print(f"*** The spread of the bond as of {trade_date} is {bond_valuation_from_price[0]*10_000:,.0f} basis points. Its cr01 is: {bond_valuation_from_price[1]*100:,.2f} and its ir01 is: {bond_valuation_from_price[2]*100:,.2f}\n")
                elif type_pricing.lower() in ['s','spread']:
                    credit_spread_str = input("What is the credit spread of the bond in basis point (100 for a credit spread of 100 bps, ie 1% or 0.01 in absolute term): ")
                    credit_spread = float(credit_spread_str) / 10_000
                    bond_valuation_from_spread = bond.value_bond_from_spread(trade_date, credit_spread, interest_rate)
                    print(f"*** The price of the bond as of {trade_date} is {bond_valuation_from_spread[0]*100:,.3f}%. Its cr01 is: {bond_valuation_from_spread[1]*100:,.2f} and its ir01 is: {bond_valuation_from_spread[2]*100:,.2f}\n")
                else:
                    print("Not a valid choice")
        except EOFError:
            break
        except:
            counter += 1
            print("Invalid entry")


def main():
    bond = create_bond_object_from_prompt()
    if bond:
        price_bond_from_prompt(bond)
    else:
        print("Invalid bond description")

if __name__ == "__main__":
   main()
