import os
import sys
import streamlit as st

# Add the current directory to the path so we can import our component
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import our component directly from the local __init__.py file
from __init__ import filter

# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run filter/example.py`

st.title("Filter Component Demo")

# Sample data
categories = ["Electronics", "Books", "Clothing", "Home & Kitchen", "Sports", "Toys"]
brands = ["Apple", "Samsung", "Sony", "LG", "Dell", "Lenovo", "HP", "Asus"]
price_ranges = ["Under $50", "$50-$100", "$100-$200", "$200-$500", "Over $500"]

st.subheader("Filter Example")

# Create our filter components - avoid using keys for now to debug the issue
selected_categories = filter("Categories", categories)
selected_brands = filter("Brands", brands)
selected_prices = filter("Price Range", price_ranges)

# Display the selected filters
st.markdown("### Selected Filters")

if selected_categories:
    st.write("**Categories:**", ", ".join(selected_categories))
else:
    st.write("**Categories:** None selected")

if selected_brands:
    st.write("**Brands:**", ", ".join(selected_brands))
else:
    st.write("**Brands:** None selected")

if selected_prices:
    st.write("**Price Range:**", ", ".join(selected_prices))
else:
    st.write("**Price Range:** None selected")

# Show how this could be used in a real application
st.markdown("---")
st.subheader("How to use filter values")

# Mock search results based on filters
if selected_categories or selected_brands or selected_prices:
    st.write("Showing products matching your filters...")
    
    # Create a sample DataFrame based on selected filters
    import pandas as pd
    
    # Simple mockup of how you might use the filter values
    if len(selected_categories) == 0:
        selected_categories = categories  # If none selected, include all
    
    if len(selected_brands) == 0:
        selected_brands = brands[:3]  # If none selected, include some defaults
    
    # Create a sample dataframe (in a real app, this would query your database)
    data = []
    for category in selected_categories[:2]:  # Limit to first 2 for demo
        for brand in selected_brands[:2]:  # Limit to first 2 for demo
            data.append({
                "Product": f"{brand} {category} Item",
                "Category": category,
                "Brand": brand,
                "Price": "$" + str(50 + hash(category + brand) % 500)
            })
    
    if data:
        st.table(pd.DataFrame(data))
    else:
        st.write("No products match your criteria.")
else:
    st.write("Select filters to see results.")