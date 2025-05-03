import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

def generate_badge(df, category=None):
    """
    Generates a visual badge for the most sold product in a given category.
    
    Parameters:
    df (DataFrame): The enhanced dataset
    category (str): The specific category to generate badge for
    
    Returns:
    dict: Dictionary containing badge image path and product details
    """
    if all(col in df.columns for col in ['category', 'item_purchased', 'quantity']):
        # If category is specified, filter data for that category
        if category:
            df = df[df['category'] == category]
        
        # Group by category and item to get total quantity sold
        sales_data = df.groupby(['category', 'item_purchased'])['quantity'].sum().reset_index()
        
        # Get the top selling product for the category
        if not sales_data.empty:
            # Find the product with maximum quantity sold
            idx = sales_data.groupby('category')['quantity'].idxmax()
            top_products = sales_data.loc[idx]
            
            def create_badge_image(category, product, quantity):
                """Helper function to create a badge image"""
                # Load the badge template
                badge_template_path = os.path.join('assets', 'badge.png')
                badge = Image.open(badge_template_path)
                
                # Create a drawing object
                draw = ImageDraw.Draw(badge)
                
                # Try to load a nice font, fall back to default if not available
                try:
                    # Adjust font size based on text length
                    font_size = 40
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                # Prepare the text
                badge_text = f"{int(quantity)} units sold for {product}"
                
                # Wrap text if it's too long
                max_width = 20  # Adjust based on your badge width
                wrapped_text = textwrap.fill(badge_text, width=max_width)
                
                # Calculate text position to center it
                bbox = draw.textbbox((0, 0), wrapped_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Position text in the center of the badge
                x = (badge.width - text_width) // 2
                y = (badge.height - text_height) // 2
                
                # Add the main text
                draw.text((x, y), wrapped_text, fill='white', font=font)
                
                # Add verification text at the bottom
                verification_text = "Verified by TrendScape"
                verification_font_size = 37
                try:
                    verification_font = ImageFont.truetype("arial.ttf", verification_font_size)
                except:
                    verification_font = ImageFont.load_default()
                
                # Calculate position for verification text
                v_bbox = draw.textbbox((0, 0), verification_text, font=verification_font)
                v_text_width = v_bbox[2] - v_bbox[0]
                v_x = (badge.width - v_text_width) // 2
                v_y = badge.height - 120  # Adjust this value to position the text appropriately
                
                draw.text((v_x, v_y), verification_text, fill='black', font=verification_font)
                
                # Save the badge
                output_path = os.path.join('assets', f'generated_badge_{category.lower().replace(" ", "_")}.png')
                badge.save(output_path)
                
                return output_path
            
            if category:
                # Return single category result
                if not top_products.empty:
                    product = top_products.iloc[0]
                    badge_path = create_badge_image(
                        product['category'],
                        product['item_purchased'],
                        product['quantity']
                    )
                    return {
                        'category': product['category'],
                        'product': product['item_purchased'],
                        'quantity': int(product['quantity']),
                        'badge_path': badge_path,
                        'badge_text': f"{int(product['quantity'])} units sold for {product['item_purchased']} - Verified by TrendScape"
                    }
            else:
                # Return all categories
                badges = {}
                for _, row in top_products.iterrows():
                    badge_path = create_badge_image(
                        row['category'],
                        row['item_purchased'],
                        row['quantity']
                    )
                    badges[row['category']] = {
                        'category': row['category'],
                        'product': row['item_purchased'],
                        'quantity': int(row['quantity']),
                        'badge_path': badge_path,
                        'badge_text': f"{int(row['quantity'])} units sold for {row['item_purchased']} - Verified by TrendScape"
                    }
                return badges
    
    return None
