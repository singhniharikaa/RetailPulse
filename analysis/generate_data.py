import numpy as np
import pandas as pd
import os

def generate_retail_data():
    np.random.seed(42)

    categories = {
        'Electronics': {
            'products': ['Wireless Earbuds', 'Bluetooth Speaker', 'Smart Watch', 'Power Bank 20000mAh',
                         'USB-C Hub', 'Webcam HD', 'Mechanical Keyboard', 'Gaming Mouse',
                         'Portable Monitor', 'Phone Stand'],
            'price_range': (799, 15999),
            'margin_range': (0.08, 0.35)
        },
        'Clothing': {
            'products': ['Cotton T-Shirt', 'Denim Jeans', 'Formal Shirt', 'Hoodie',
                         'Track Pants', 'Kurta Set', 'Winter Jacket', 'Polo T-Shirt',
                         'Cargo Pants', 'Linen Shirt'],
            'price_range': (399, 3499),
            'margin_range': (0.25, 0.55)
        },
        'Home & Kitchen': {
            'products': ['Non-Stick Pan', 'Bedsheet Set', 'LED Desk Lamp', 'Water Bottle 1L',
                         'Storage Container Set', 'Cushion Covers', 'Wall Clock', 'Chopping Board'],
            'price_range': (249, 2999),
            'margin_range': (0.20, 0.50)
        },
        'Sports & Fitness': {
            'products': ['Yoga Mat', 'Resistance Bands', 'Dumbbells 5kg', 'Skipping Rope',
                         'Sports Shoes', 'Gym Gloves', 'Cricket Bat', 'Football'],
            'price_range': (199, 4999),
            'margin_range': (0.15, 0.45)
        },
        'Beauty & Personal Care': {
            'products': ['Face Wash', 'Sunscreen SPF50', 'Hair Serum', 'Moisturizer',
                         'Lip Balm Set', 'Beard Oil', 'Shampoo 500ml', 'Face Mask Pack'],
            'price_range': (149, 1499),
            'margin_range': (0.30, 0.65)
        },
        'Books & Stationery': {
            'products': ['Notebook Set', 'Pen Set Premium', 'Self-Help Book', 'Planner 2024',
                         'Sketch Pad', 'Highlighter Set'],
            'price_range': (99, 899),
            'margin_range': (-0.10, 0.40)
        }
    }

    regions = ['North', 'South', 'East', 'West']
    payment_methods = ['UPI', 'Credit Card', 'Debit Card', 'Cash', 'Net Banking']

    transactions = []
    txn_id = 1

    for month in range(1, 13):
        if month in [10, 11, 12]:
            monthly_txns = np.random.randint(250, 350)
        elif month in [1, 6, 7]:
            monthly_txns = np.random.randint(180, 250)
        else:
            monthly_txns = np.random.randint(150, 220)

        for _ in range(monthly_txns):
            category = np.random.choice(list(categories.keys()),
                                         p=[0.25, 0.22, 0.18, 0.13, 0.12, 0.10])
            cat_data = categories[category]
            product = np.random.choice(cat_data['products'])

            unit_price = round(np.random.uniform(*cat_data['price_range']), 2)
            margin = np.random.uniform(*cat_data['margin_range'])
            cost_price = round(unit_price * (1 - margin), 2)

            quantity = np.random.choice([1, 1, 1, 2, 2, 3, 4, 5],
                                         p=[0.35, 0.15, 0.10, 0.15, 0.10, 0.07, 0.05, 0.03])

            discount = np.random.choice([0, 0, 0, 5, 10, 15, 20, 25],
                                         p=[0.30, 0.15, 0.10, 0.15, 0.12, 0.08, 0.06, 0.04])

            day = np.random.randint(1, 29)
            date = f'2026-{month:02d}-{day:02d}'

            region = np.random.choice(regions, p=[0.30, 0.28, 0.20, 0.22])
            payment = np.random.choice(payment_methods, p=[0.35, 0.25, 0.15, 0.15, 0.10])

            transactions.append({
                'transaction_id': f'TXN-{txn_id:04d}',
                'date': date,
                'product_name': product,
                'category': category,
                'quantity': quantity,
                'unit_price': unit_price,
                'cost_price': cost_price,
                'discount_percent': discount,
                'region': region,
                'payment_method': payment
            })
            txn_id += 1

    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, 'retail_sales_data.csv'), index=False)

    print(f"Generated {len(df)} transactions")
    print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"Categories: {df['category'].nunique()}")
    print(f"Products: {df['product_name'].nunique()}")

    return df

if __name__ == '__main__':
    generate_retail_data()
