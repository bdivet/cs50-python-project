# Pricing model of a bond to generate credit and interest rate sensitivities
### Video demo: [https://youtu.be/8u9Igzj5fHM?si=YwgfUB3O46o_zpgX]
### Description
#### Bond Definition
As per [Wikipedia](https://en.wikipedia.org/wiki/Bond_(finance)),

> a bond is a type of security under which the issuer (debtor) owes the holder (creditor) a debt, and is obliged – depending on the terms – to provide cash flow to the creditor (e.g. repay the principal (i.e. amount borrowed) of the bond at the maturity date as well as interest (called the coupon) over a specified amount of time)

The main characteristics of a bond are its maturity date and its coupon. We can ignore coupon frequency and day count convention which only have second order effects.
#### Bond valuation
As often in finance the valuation of bond comes down to discounting future cash flows. The actual discounting requires an interest rate that we'll assume to be constant for simplicity. The cash flows depend on two credit parameters: the default probability and the recovery rate. In the absence of default, the issuer will pay coupons on a regular basis and pay back the notional on maturity date. In case of the default, the holder will receive recovery rate times the face value of the bond only. The default probability at time t depends on t and the default intensity spread divided by (1 - recovery)
#### Python implementation
A bond is a good candidate to develop a **class Bond** with its own
- attributes: maturity date, coupon, recovery and pricing date
- methods: __init__ and __str__, value_bond_from_price and value_bond_from_spread
I also used property decorator to create getter and setter for the attribute recovery.

**extract_date_from_string** is a utility function that ensure that a given string can indeed be interpreted as a proper date. It uses the regex techniques learnt during the course. The user is prompted twice for a date: the maturity date of the bond and the trade date. And this function is called in both instances.

**get_settlement_date_from_trade_date** is a utility function to get the settlement date from the trade date. The settlement date is 2 business days after the trade date, so it needs to figure out whether the settlement will cross over a week end (for sake of simplicity the function does not check for bank holidays).

**bond_price** is the core analytical function. It is vectorized using numpy library, which does not add significant value in this special case but can be of interest when performing calculations on a large number of bonds. This function takes spread and interst rate as inputs and returns a bond price. By bumping either credit spread or interest by a small amount (in this case 1 basis point) it is possible to estimate the first derivative of the price with respect to credit and with respect to interest rate. The sensitivity of the bond price with respect to credit spread is called CR01. The sensitivity of the bond price with respect to interest rate is called IR01.
By iteration and using a method similar to Newton-Raphson, bond_price can be used to imply the spread that matches a given price. In this case we are somehow inverting the function. And once we have the implied spread, we can proceed as in the first case described.

Last **create_bond_object_from_prompt** and **price_bond_from_prompt** are used to interact with the user, prompting him to enter the characterics of the bond and then to specify the pricing parameters, making sure they can be passed on the different functions. In particular the string must respect a certain format and the number must have the right scale, absolute, in percent or in basis point, each successive scale being in a 1:100 ratio to the previous one.