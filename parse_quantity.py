"""
Parse fractional quantities for Python forecasting scripts
Converts between decimal and fraction formats
"""

from fractions import Fraction

def parse_fractional_quantity(quantity):
    """
    Parse quantity that might be in fractional format (e.g., "2 1/2", "1/2", "2.5")
    Returns decimal value for calculations
    
    Args:
        quantity: Can be string ("2 1/2", "1/2", "2.5") or numeric (2.5)
    
    Returns:
        float: Decimal value for calculations
    """
    if quantity is None:
        return 0.0
    
    # If it's already a number, return as float
    if isinstance(quantity, (int, float)):
        return float(quantity)
    
    # Convert to string for parsing
    quantity_str = str(quantity).strip()
    
    if not quantity_str or quantity_str == '0':
        return 0.0
    
    # Handle mixed fractions like "2 1/2"
    if ' ' in quantity_str and '/' in quantity_str:
        parts = quantity_str.split(' ')
        if len(parts) == 2:
            try:
                whole_part = float(parts[0])
                fraction_part = parts[1]
                
                if '/' in fraction_part:
                    num, den = fraction_part.split('/')
                    fraction_value = float(num) / float(den)
                    return whole_part + fraction_value
            except (ValueError, ZeroDivisionError):
                pass
    
    # Handle simple fractions like "1/2"
    if '/' in quantity_str and ' ' not in quantity_str:
        try:
            num, den = quantity_str.split('/')
            return float(num) / float(den)
        except (ValueError, ZeroDivisionError):
            pass
    
    # Handle decimal numbers
    try:
        return float(quantity_str)
    except ValueError:
        return 0.0

def format_quantity_as_fraction(quantity):
    """
    Convert decimal quantity to fractional format for display
    Examples: 1.5 -> "1 1/2", 0.75 -> "3/4", 2.0 -> "2", 1.06 -> "1.06"
    """
    if quantity == 0:
        return "0"
    
    # Handle whole numbers
    if abs(quantity - int(quantity)) < 0.01:  # Very close to whole number
        return str(int(round(quantity)))
    
    # Convert to fraction for common fractions
    try:
        frac = Fraction(quantity).limit_denominator(4)  # Limit to common fractions like 1/2, 1/4, 3/4
        
        # Only use fraction if it's a close match
        if abs(quantity - float(frac)) < 0.01:
            # Handle mixed fractions
            if frac.numerator >= frac.denominator:
                whole_part = frac.numerator // frac.denominator
                remainder = frac.numerator % frac.denominator
                if remainder == 0:
                    return str(whole_part)
                else:
                    return f"{whole_part} {remainder}/{frac.denominator}"
            else:
                return f"{frac.numerator}/{frac.denominator}"
    except:
        pass
    
    # Fallback to decimal for non-standard fractions
    return str(round(quantity, 2))
