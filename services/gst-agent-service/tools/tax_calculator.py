def calculate_tax(base_amount: float, rate_percentage: float) -> dict:
    """
    Calculates the GST amount and total based on a base amount and percentage rate.
    """
    tax_amount = base_amount * (rate_percentage / 100)
    total_amount = base_amount + tax_amount
    return {
        "base_amount": base_amount,
        "rate": f"{rate_percentage}%",
        "tax_amount": round(tax_amount, 2),
        "total_amount": round(total_amount, 2)
    }
