import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import json
import os
import shutil
from generate_data import generate_retail_data

BG_COLOR = '#F0EEF6'
CARD_BG = '#FFFFFF'
PRIMARY = '#6366F1'
PRIMARY_DARK = '#4F46E5'
SECONDARY = '#818CF8'
ACCENT_ORANGE = '#F59E0B'
ACCENT_GREEN = '#10B981'
ACCENT_RED = '#EF4444'
TEXT_DARK = '#1E1B4B'
TEXT_MID = '#64748B'
GRID_COLOR = '#E2E0ED'

CATEGORY_COLORS = ['#6366F1', '#F59E0B', '#10B981', '#EF4444', '#EC4899', '#8B5CF6']

BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
CHARTS_DIR = os.path.join(OUTPUT_DIR, 'charts')

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Segoe UI', 'Arial', 'Helvetica'],
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'figure.facecolor': BG_COLOR,
    'axes.facecolor': CARD_BG,
    'axes.edgecolor': GRID_COLOR,
    'axes.grid': True,
    'grid.color': GRID_COLOR,
    'grid.alpha': 0.5,
    'xtick.color': TEXT_MID,
    'ytick.color': TEXT_MID,
})


def prepare_data(df):
    df['revenue'] = df['unit_price'] * df['quantity'] * (1 - df['discount_percent'] / 100)
    df['total_cost'] = df['cost_price'] * df['quantity']
    df['profit'] = df['revenue'] - df['total_cost']
    df['profit_margin'] = np.where(df['revenue'] > 0, (df['profit'] / df['revenue']) * 100, 0)
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.strftime('%b')
    return df


def analyze_kpis(df):
    total_revenue = round(float(df['revenue'].sum()), 2)
    total_profit = round(float(df['profit'].sum()), 2)
    total_transactions = int(len(df))
    avg_order_value = round(total_revenue / total_transactions, 2)
    overall_margin = round((total_profit / total_revenue) * 100, 1)
    total_products = int(df['product_name'].nunique())

    return {
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'total_transactions': total_transactions,
        'avg_order_value': avg_order_value,
        'overall_margin': overall_margin,
        'total_products': total_products
    }


def analyze_category_performance(df):
    cat_stats = df.groupby('category').agg(
        revenue=('revenue', 'sum'),
        profit=('profit', 'sum'),
        transactions=('transaction_id', 'count'),
        avg_price=('unit_price', 'mean')
    ).round(2)

    cat_stats['margin'] = ((cat_stats['profit'] / cat_stats['revenue']) * 100).round(1)
    cat_stats = cat_stats.sort_values('revenue', ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(cat_stats.index, cat_stats['revenue'], color=CATEGORY_COLORS[:len(cat_stats)],
                   height=0.6, edgecolor='white', linewidth=1.5, zorder=3)

    for bar, val in zip(bars, cat_stats['revenue']):
        ax.text(val + cat_stats['revenue'].max() * 0.01, bar.get_y() + bar.get_height() / 2,
                f'₹{val:,.0f}', va='center', fontsize=10, color=TEXT_DARK, fontweight='600')

    ax.set_title('Revenue by Category', color=TEXT_DARK, pad=15)
    ax.set_xlabel('Revenue (₹)', color=TEXT_MID)
    ax.invert_yaxis()
    ax.set_xlim(0, cat_stats['revenue'].max() * 1.15)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'₹{x/1000:.0f}K'))
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'category_revenue.png'), dpi=200, bbox_inches='tight')
    plt.close(fig)

    return cat_stats.reset_index().to_dict('records')


def analyze_top_products(df):
    top = df.groupby('product_name').agg(
        revenue=('revenue', 'sum'),
        quantity=('quantity', 'sum'),
        profit=('profit', 'sum')
    ).round(2).nlargest(10, 'revenue')

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [PRIMARY if i < 3 else SECONDARY for i in range(len(top))]
    bars = ax.barh(top.index, top['revenue'], color=colors, height=0.6,
                   edgecolor='white', linewidth=1.5, zorder=3)

    for bar, val in zip(bars, top['revenue']):
        ax.text(val + top['revenue'].max() * 0.01, bar.get_y() + bar.get_height() / 2,
                f'₹{val:,.0f}', va='center', fontsize=9, color=TEXT_DARK, fontweight='500')

    ax.set_title('Top 10 Products by Revenue', color=TEXT_DARK, pad=15)
    ax.set_xlabel('Revenue (₹)', color=TEXT_MID)
    ax.invert_yaxis()
    ax.set_xlim(0, top['revenue'].max() * 1.15)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'₹{x/1000:.0f}K'))
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'top10_products.png'), dpi=200, bbox_inches='tight')
    plt.close(fig)

    return top.reset_index().to_dict('records')


def analyze_monthly_trend(df):
    monthly = df.groupby('month').agg(
        revenue=('revenue', 'sum'),
        transactions=('transaction_id', 'count'),
        profit=('profit', 'sum')
    ).round(2)

    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.fill_between(monthly.index, monthly['revenue'], alpha=0.15, color=PRIMARY, zorder=2)
    ax.plot(monthly.index, monthly['revenue'], color=PRIMARY, linewidth=2.5,
            marker='o', markersize=7, markerfacecolor='white', markeredgecolor=PRIMARY,
            markeredgewidth=2, zorder=3)

    peak_month = monthly['revenue'].idxmax()
    ax.annotate(f'Peak: ₹{monthly.loc[peak_month, "revenue"]:,.0f}',
                xy=(peak_month, monthly.loc[peak_month, 'revenue']),
                xytext=(peak_month - 1.5, monthly.loc[peak_month, 'revenue'] * 1.08),
                fontsize=9, fontweight='bold', color=PRIMARY_DARK,
                arrowprops=dict(arrowstyle='->', color=PRIMARY_DARK, lw=1.5))

    ax.set_title('Monthly Sales Trend (2026)', color=TEXT_DARK, pad=15)
    ax.set_xlabel('Month', color=TEXT_MID)
    ax.set_ylabel('Revenue (₹)', color=TEXT_MID)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_labels)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'₹{x/1000:.0f}K'))
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'monthly_sales_trend.png'), dpi=200, bbox_inches='tight')
    plt.close(fig)

    return monthly.reset_index().to_dict('records')


def analyze_profit_margins(df):
    cat_margin = df.groupby('category').agg(
        revenue=('revenue', 'sum'),
        profit=('profit', 'sum')
    )
    cat_margin['margin'] = ((cat_margin['profit'] / cat_margin['revenue']) * 100).round(1)
    cat_margin = cat_margin.sort_values('margin', ascending=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    wedges, texts, autotexts = ax1.pie(
        cat_margin['revenue'], labels=cat_margin.index, autopct='%1.1f%%',
        colors=CATEGORY_COLORS[:len(cat_margin)], startangle=90,
        wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2),
        textprops=dict(fontsize=9, color=TEXT_DARK)
    )
    for t in autotexts:
        t.set_fontsize(8)
        t.set_fontweight('bold')
    ax1.set_title('Revenue Share', color=TEXT_DARK, pad=15)

    bars = ax2.bar(cat_margin.index, cat_margin['margin'],
                   color=[ACCENT_GREEN if m > 0 else ACCENT_RED for m in cat_margin['margin']],
                   width=0.6, edgecolor='white', linewidth=1.5, zorder=3)

    for bar, val in zip(bars, cat_margin['margin']):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                 f'{val:.1f}%', ha='center', fontsize=9, fontweight='600', color=TEXT_DARK)

    ax2.set_title('Profit Margin by Category', color=TEXT_DARK, pad=15)
    ax2.set_ylabel('Margin (%)', color=TEXT_MID)
    ax2.tick_params(axis='x', rotation=25)
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'profit_margins.png'), dpi=200, bbox_inches='tight')
    plt.close(fig)

    return cat_margin.reset_index().to_dict('records')


def analyze_monthly_growth(df):
    monthly_rev = df.groupby('month')['revenue'].sum()
    growth = monthly_rev.pct_change().fillna(0) * 100

    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [ACCENT_GREEN if g >= 0 else ACCENT_RED for g in growth]
    bars = ax.bar(growth.index, growth.values, color=colors, width=0.6,
                  edgecolor='white', linewidth=1.5, zorder=3)

    for bar, val in zip(bars, growth.values):
        y_pos = bar.get_height() + 0.3 if val >= 0 else bar.get_height() - 1.5
        ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                f'{val:+.1f}%', ha='center', fontsize=9, fontweight='600',
                color=ACCENT_GREEN if val >= 0 else ACCENT_RED)

    ax.axhline(y=0, color=TEXT_MID, linewidth=0.8, linestyle='-', zorder=2)
    ax.set_title('Month-over-Month Growth Rate', color=TEXT_DARK, pad=15)
    ax.set_xlabel('Month', color=TEXT_MID)
    ax.set_ylabel('Growth (%)', color=TEXT_MID)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_labels)
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'monthly_growth_rate.png'), dpi=200, bbox_inches='tight')
    plt.close(fig)

    return [{'month': m, 'growth_rate': round(g, 1)} for m, g in zip(range(1, 13), growth)]


def analyze_loss_making(df):
    product_profit = df.groupby('product_name').agg(
        revenue=('revenue', 'sum'),
        profit=('profit', 'sum'),
        quantity=('quantity', 'sum')
    ).round(2)

    loss_products = product_profit[product_profit['profit'] < 0].sort_values('profit')

    if len(loss_products) > 0:
        fig, ax = plt.subplots(figsize=(10, max(4, len(loss_products) * 0.6)))
        bars = ax.barh(loss_products.index, loss_products['profit'],
                       color=ACCENT_RED, height=0.6, alpha=0.85,
                       edgecolor='white', linewidth=1.5, zorder=3)

        for bar, val in zip(bars, loss_products['profit']):
            ax.text(val - abs(loss_products['profit'].min()) * 0.03,
                    bar.get_y() + bar.get_height() / 2,
                    f'₹{val:,.0f}', va='center', fontsize=9, color='white', fontweight='600')

        ax.set_title('Loss-Making Products', color=TEXT_DARK, pad=15)
        ax.set_xlabel('Profit/Loss (₹)', color=TEXT_MID)
        ax.invert_yaxis()
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'₹{x:,.0f}'))
        plt.tight_layout()
        fig.savefig(os.path.join(CHARTS_DIR, 'loss_making_products.png'), dpi=200, bbox_inches='tight')
        plt.close(fig)

    return loss_products.reset_index().to_dict('records')


def analyze_region_performance(df):
    region_stats = df.groupby('region').agg(
        revenue=('revenue', 'sum'),
        transactions=('transaction_id', 'count'),
        profit=('profit', 'sum')
    ).round(2).sort_values('revenue', ascending=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = [PRIMARY, SECONDARY, '#A5B4FC', '#C7D2FE']
    bars = ax.bar(region_stats.index, region_stats['revenue'], color=colors[:len(region_stats)],
                  width=0.5, edgecolor='white', linewidth=1.5, zorder=3)

    for bar, val in zip(bars, region_stats['revenue']):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + region_stats['revenue'].max() * 0.01,
                f'₹{val/1000:.0f}K', ha='center', fontsize=10, fontweight='600', color=TEXT_DARK)

    ax.set_title('Revenue by Region', color=TEXT_DARK, pad=15)
    ax.set_ylabel('Revenue (₹)', color=TEXT_MID)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'₹{x/1000:.0f}K'))
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'region_performance.png'), dpi=200, bbox_inches='tight')
    plt.close(fig)

    return region_stats.reset_index().to_dict('records')


def generate_insights(kpis, category_data, top_products, monthly_data, loss_products):
    insights = []

    best_cat = max(category_data, key=lambda x: x['revenue'])
    insights.append({
        'icon': '👑',
        'title': 'Top Revenue Category',
        'text': f"{best_cat['category']} leads with ₹{best_cat['revenue']:,.0f} in revenue"
    })

    best_product = top_products[0]
    insights.append({
        'icon': '🏆',
        'title': 'Best Selling Product',
        'text': f"{best_product['product_name']} generated ₹{best_product['revenue']:,.0f} revenue"
    })

    peak = max(monthly_data, key=lambda x: x['revenue'])
    month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    insights.append({
        'icon': '📈',
        'title': 'Peak Sales Month',
        'text': f"{month_names[peak['month']]} recorded highest sales of ₹{peak['revenue']:,.0f}"
    })

    if loss_products:
        total_loss = sum(p['profit'] for p in loss_products)
        insights.append({
            'icon': '⚠️',
            'title': 'Loss Alert',
            'text': f"{len(loss_products)} products are running at a loss totaling ₹{abs(total_loss):,.0f}"
        })

    insights.append({
        'icon': '💰',
        'title': 'Profit Margin',
        'text': f"Overall profit margin stands at {kpis['overall_margin']}%"
    })

    insights.append({
        'icon': '🛒',
        'title': 'Average Order Value',
        'text': f"Customers spend an average of ₹{kpis['avg_order_value']:,.0f} per transaction"
    })

    return insights


def main():
    os.makedirs(CHARTS_DIR, exist_ok=True)

    print("Generating synthetic data...")
    df = generate_retail_data()

    print("Cleaning & preparing data...")
    df = prepare_data(df)

    print("Running analysis...")
    kpis = analyze_kpis(df)
    print(f"  Total Revenue: Rs.{kpis['total_revenue']:,.2f}")
    print(f"  Total Profit: Rs.{kpis['total_profit']:,.2f}")
    print(f"  Margin: {kpis['overall_margin']}%")

    print("  > Category performance...")
    category_data = analyze_category_performance(df)

    print("  > Top 10 products...")
    top_products = analyze_top_products(df)

    print("  > Monthly trend...")
    monthly_data = analyze_monthly_trend(df)

    print("  > Profit margins...")
    margin_data = analyze_profit_margins(df)

    print("  > Monthly growth...")
    growth_data = analyze_monthly_growth(df)

    print("  > Loss-making products...")
    loss_products = analyze_loss_making(df)

    print("  > Region performance...")
    region_data = analyze_region_performance(df)

    print("  > Generating insights...")
    insights = generate_insights(kpis, category_data, top_products, monthly_data, loss_products)

    results = {
        'kpis': kpis,
        'category_performance': category_data,
        'top_products': top_products,
        'monthly_trend': monthly_data,
        'profit_margins': margin_data,
        'monthly_growth': growth_data,
        'loss_making_products': loss_products,
        'region_performance': region_data,
        'insights': insights
    }

    json_path = os.path.join(OUTPUT_DIR, 'analysis_results.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    dashboard_json_path = os.path.join(BASE_DIR, '..', 'dashboard', 'data', 'analysis_results.json')
    os.makedirs(os.path.dirname(dashboard_json_path), exist_ok=True)
    with open(dashboard_json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nAnalysis complete!")
    print(f"  Charts saved to: {CHARTS_DIR}")
    print(f"  Results JSON: {json_path}")
    print(f"  Dashboard JSON: {dashboard_json_path}")

    dashboard_data_dir = os.path.dirname(dashboard_json_path)
    for chart_file in os.listdir(CHARTS_DIR):
        if chart_file.endswith('.png'):
            shutil.copy2(os.path.join(CHARTS_DIR, chart_file), dashboard_data_dir)
    print(f"  Charts copied to dashboard")


if __name__ == '__main__':
    main()
