"""
Simplified Sales Forecasting for BHOKYOL COCOLUMBER SYSTEM
Uses only basic Python libraries + mysql-connector-python
Author: AI Assistant
Date: 2025-09-24
"""

import sys
import json
import mysql.connector
from datetime import datetime, timedelta
from statistics import mean
import logging
from fractions import Fraction
from parse_quantity import parse_fractional_quantity

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

class SimpleForecastController:
    def __init__(self):
        """Initialize with minimal dependencies"""
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'bhokyol_cocolumber_db',
            'charset': 'utf8mb4'
        }
        
    def connect_db(self):
        """Connect to database"""
        try:
            return mysql.connector.connect(**self.config)
        except mysql.connector.Error as err:
            return None
    
    def get_sales_data(self, conn, product_id=None):
        """Get sales data for forecasting"""
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get sales data with product information
            # Use total_amount_due since total_sales column doesn't exist
            query = """
            SELECT 
                s.product_name,
                p.id as product_id,
                p.category,
                p.description,
                s.quantity_sold,
                COALESCE(s.total_amount_due, 0) as total_sales,
                p.price,
                p.unit,
                s.transaction_date,
                MONTH(s.transaction_date) as month,
                YEAR(s.transaction_date) as year
            FROM sales s
            LEFT JOIN products p ON s.product_name = p.product_name AND s.description = p.description
            WHERE s.transaction_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            """
            
            params = []
            if product_id:
                query += " AND p.id = %s"
                params.append(product_id)
            
            query += " ORDER BY s.transaction_date DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            
            return results
            
        except Exception as e:
            return []
    
    def simple_forecast_algorithm(self, sales_data, product_name=None, months=3, product_id=None):
        """Simple moving average forecasting algorithm"""
        forecasts = []
        
        # Group data by product (now using product_id for unique identification)
        product_data = {}
        for sale in sales_data:
            # Use product_id if available, otherwise create a composite key
            product_key = sale.get('product_id')
            if not product_key:
                # Create composite key from name and description for unique identification
                product_key = f"{sale['product_name']}|{sale.get('description', '')}"
            
            name = sale['product_name']
            
            if product_name and name != product_name:
                continue
            if product_id and str(sale.get('product_id', '')) != str(product_id):
                continue
                
            if product_key not in product_data:
                product_data[product_key] = {
                    'quantities': [],
                    'revenues': [],
                    'category': sale.get('category', 'Unknown'),
                    'price': float(sale['price']) if sale['price'] is not None else 0.0,
                    'unit': sale.get('unit', 'pcs'),
                    'description': sale.get('description', ''),
                    'product_id': sale.get('product_id'),
                    'product_name': name
                }
            
            # Parse fractional quantities like "2 1/2"
            qty_numeric = parse_fractional_quantity(sale.get('quantity_sold'))
            product_data[product_key]['quantities'].append(qty_numeric)
            product_data[product_key]['revenues'].append(float(sale['total_sales']) if sale['total_sales'] is not None else 0.0)
        
        # Generate forecasts for each product
        for product, data in product_data.items():
            if len(data['quantities']) < 1:  # Need at least 1 data point
                continue
                
            # Calculate moving averages
            avg_quantity = mean(data['quantities'])
            avg_revenue = mean(data['revenues'])
            
            # Simple trend calculation
            if len(data['quantities']) == 1:
                trend_factor = 1.0  # No trend for single data point
            else:
                recent_qty = mean(data['quantities'][:3]) if len(data['quantities']) >= 3 else avg_quantity
                trend_factor = max(0.5, min(1.5, recent_qty / avg_quantity)) if avg_quantity > 0 else 1.0
            
            # Calculate confidence based on data consistency
            if len(data['quantities']) >= 5:
                variance = sum((x - avg_quantity) ** 2 for x in data['quantities']) / len(data['quantities'])
                std_dev = variance ** 0.5
                confidence = max(0.3, min(0.9, 1.0 - (std_dev / avg_quantity) if avg_quantity > 0 else 0.3))
            elif len(data['quantities']) == 1:
                confidence = 0.3  # Low confidence for single data point
            else:
                confidence = 0.5  # Medium confidence for limited data
            
            # Generate monthly forecasts
            for month_offset in range(1, months + 1):
                forecast_date = datetime.now() + timedelta(days=30 * month_offset)
                forecast_month = forecast_date.strftime('%Y-%m')
                
                # Apply trend and seasonal adjustments to quantity only
                seasonal_factor = 1.0 + (month_offset * 0.02)  # Slight growth assumption
                predicted_quantity_decimal = max(0.5, avg_quantity * trend_factor * seasonal_factor)
                predicted_quantity = format_quantity_as_fraction(predicted_quantity_decimal)
                # Revenue should be simple: Price × Quantity (exact calculation)
                predicted_revenue = round(predicted_quantity_decimal * data['price'], 2)
                
                forecasts.append({
                    'product_name': data['product_name'],
                    'product_id': data['product_id'],
                    'description': data['description'],
                    'category': data['category'],
                    'forecast_month': forecast_month,
                    'forecast_date': forecast_date.strftime('%Y-%m-%d'),
                    'forecast_quantity': predicted_quantity,
                    'forecast_quantity_decimal': round(predicted_quantity_decimal, 2),
                    'forecast_revenue': round(predicted_revenue, 2),
                    'confidence': round(confidence, 2),
                    'price': data['price'],
                    'unit': data['unit']
                })
        
        return forecasts
    
    def save_forecasts_to_db(self, conn, forecasts):
        """Save forecasts to database"""
        try:
            cursor = conn.cursor()
            
            # Clear existing future forecasts
            cursor.execute("DELETE FROM sales_forecasting WHERE forecast_month >= CURDATE()")
            
            # Insert new forecasts
            insert_query = """
            INSERT INTO sales_forecasting 
            (product_id, forecast_month, forecast_quantity, forecast_revenue, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            """
            
            for forecast in forecasts:
                # Use product_id from forecast data if available, otherwise look it up
                product_id = forecast.get('product_id')
                if not product_id:
                    cursor.execute("SELECT id FROM products WHERE product_name = %s", (forecast['product_name'],))
                    result = cursor.fetchone()
                    if result:
                        product_id = result[0]
                
                if product_id:
                    cursor.execute(insert_query, (
                        product_id,
                        forecast['forecast_month'],
                        forecast['forecast_quantity_decimal'],
                        forecast['forecast_revenue']
                    ))
            
            conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            return False
    
    def generate_forecast(self, product_name=None, months=3, product_id=None):
        """Main forecast generation function"""
        try:
            # Connect to database
            conn = self.connect_db()
            if not conn:
                return {
                    'success': False,
                    'error': 'Database connection failed'
                }
            
            # Get sales data
            sales_data = self.get_sales_data(conn, product_id)
            if not sales_data:
                return {
                    'success': False,
                    'error': 'No sales data available for forecasting'
                }
            
            # Generate forecasts
            forecasts = self.simple_forecast_algorithm(sales_data, product_name, months, product_id)
            if not forecasts:
                return {
                    'success': False,
                    'error': 'Could not generate forecasts with available data'
                }
            
            # Save to database
            self.save_forecasts_to_db(conn, forecasts)
            
            conn.close()
            
            return {
                'success': True,
                'message': f'Generated {len(forecasts)} forecasts successfully',
                'forecast_count': len(forecasts),
                'forecasts': forecasts,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Forecast generation failed: {str(e)}'
            }

def main():
    """Command line interface"""
    try:
        # Parse command line arguments
        import argparse
        parser = argparse.ArgumentParser(description='Simple Sales Forecasting')
        parser.add_argument('--product', type=str, default=None, help='Product name to forecast')
        parser.add_argument('--product_id', type=str, default=None, help='Product ID to forecast')
        parser.add_argument('--months', type=int, default=3, help='Number of months to forecast')
        
        args = parser.parse_args()
        
        # Generate forecast
        controller = SimpleForecastController()
        result = controller.generate_forecast(args.product, args.months, args.product_id)
        
        # Output JSON result
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Return exit code
        sys.exit(0 if result.get('success', False) else 1)
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': f'Script execution failed: {str(e)}'
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

if __name__ == '__main__':
    main()
