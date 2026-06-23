document.addEventListener('DOMContentLoaded', () => {
    fetch('data/analysis_results.json')
        .then(res => res.json())
        .then(data => {
            renderKPIs(data.kpis);
            renderCategoryTable(data.category_performance);
            renderProductsTable(data.top_products);
            renderLossSection(data.loss_making_products);
            renderInsights(data.insights);
            initScrollAnimations();
            initNavPills();
        })
        .catch(() => {
            document.getElementById('kpi-container').innerHTML =
                '<p style="grid-column:1/-1;text-align:center;color:var(--text-muted);padding:40px;">Run the Python analysis first: <code>python analysis/analyze_sales.py</code></p>';
        });
});

function formatCurrency(num) {
    if (num >= 10000000) return '\u20B9' + (num / 10000000).toFixed(2) + ' Cr';
    if (num >= 100000) return '\u20B9' + (num / 100000).toFixed(2) + ' L';
    if (num >= 1000) return '\u20B9' + (num / 1000).toFixed(1) + 'K';
    return '\u20B9' + num.toFixed(0);
}

function formatNumber(num) {
    return num.toLocaleString('en-IN');
}

function animateCounter(element, target, prefix, suffix, duration) {
    let start = 0;
    let startTime = null;

    function step(timestamp) {
        if (!startTime) startTime = timestamp;
        let progress = Math.min((timestamp - startTime) / duration, 1);
        let eased = 1 - Math.pow(1 - progress, 3);
        let current = start + (target - start) * eased;

        if (target >= 10000000) {
            element.textContent = prefix + (current / 10000000).toFixed(2) + ' Cr' + suffix;
        } else if (target >= 100000) {
            element.textContent = prefix + (current / 100000).toFixed(2) + ' L' + suffix;
        } else if (target >= 1000) {
            element.textContent = prefix + (current / 1000).toFixed(1) + 'K' + suffix;
        } else if (Number.isInteger(target)) {
            element.textContent = prefix + Math.floor(current).toLocaleString('en-IN') + suffix;
        } else {
            element.textContent = prefix + current.toFixed(1) + suffix;
        }

        if (progress < 1) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
}

function renderKPIs(kpis) {
    const container = document.getElementById('kpi-container');
    const cards = [
        { label: 'Total Revenue', value: kpis.total_revenue, prefix: '\u20B9', suffix: '', icon: '💵' },
        { label: 'Total Profit', value: kpis.total_profit, prefix: '\u20B9', suffix: '', icon: '📊' },
        { label: 'Transactions', value: kpis.total_transactions, prefix: '', suffix: '', icon: '🛍️' },
        { label: 'Avg Order Value', value: kpis.avg_order_value, prefix: '\u20B9', suffix: '', icon: '🧾' },
        { label: 'Profit Margin', value: kpis.overall_margin, prefix: '', suffix: '%', icon: '📈' },
        { label: 'Products', value: kpis.total_products, prefix: '', suffix: '', icon: '📦' },
    ];

    container.innerHTML = cards.map((card, i) => `
        <div class="kpi-card" style="animation-delay: ${i * 0.1}s">
            <div class="kpi-label">${card.label}</div>
            <div class="kpi-value" id="kpi-${i}">-</div>
            <div class="kpi-sub">2026 Annual Data</div>
        </div>
    `).join('');

    setTimeout(() => {
        cards.forEach((card, i) => {
            const el = document.getElementById(`kpi-${i}`);
            animateCounter(el, card.value, card.prefix, card.suffix, 1200 + i * 200);
        });
    }, 300);
}

function renderCategoryTable(categories) {
    const tbody = document.querySelector('#category-table tbody');
    tbody.innerHTML = categories.map(cat => `
        <tr>
            <td style="font-weight: 600; color: var(--text-primary)">${cat.category}</td>
            <td>${formatCurrency(cat.revenue)}</td>
            <td class="${cat.profit >= 0 ? 'profit-positive' : 'profit-negative'}">${formatCurrency(Math.abs(cat.profit))}</td>
            <td>${cat.margin}%</td>
            <td>${formatNumber(cat.transactions)}</td>
        </tr>
    `).join('');
}

function renderProductsTable(products) {
    const tbody = document.querySelector('#products-table tbody');
    tbody.innerHTML = products.map((p, i) => {
        let rankClass = i === 0 ? 'rank-1' : i === 1 ? 'rank-2' : i === 2 ? 'rank-3' : 'rank-default';
        return `
        <tr>
            <td><span class="rank-badge ${rankClass}">${i + 1}</span></td>
            <td style="font-weight: 600; color: var(--text-primary)">${p.product_name}</td>
            <td>${formatCurrency(p.revenue)}</td>
            <td>${formatNumber(p.quantity)}</td>
            <td class="${p.profit >= 0 ? 'profit-positive' : 'profit-negative'}">${formatCurrency(Math.abs(p.profit))}</td>
        </tr>
        `;
    }).join('');
}

function renderLossSection(lossProducts) {
    if (!lossProducts || lossProducts.length === 0) return;

    document.getElementById('loss-section').style.display = 'flex';
    document.getElementById('loss-container').style.display = 'block';
    document.getElementById('loss-count').textContent = lossProducts.length + ' Products';

    const tbody = document.querySelector('#loss-table tbody');
    tbody.innerHTML = lossProducts.map(p => `
        <tr>
            <td style="font-weight: 600; color: var(--text-primary)">${p.product_name}</td>
            <td>${formatCurrency(p.revenue)}</td>
            <td class="profit-negative">-${formatCurrency(Math.abs(p.profit))}</td>
            <td>${formatNumber(p.quantity)}</td>
        </tr>
    `).join('');
}

function renderInsights(insights) {
    const container = document.getElementById('insights-container');
    container.innerHTML = insights.map((insight, i) => {
        let isLoss = insight.title.toLowerCase().includes('loss');
        return `
        <div class="insight-card ${isLoss ? 'loss-alert' : ''}" style="animation-delay: ${i * 0.1}s">
            <div class="insight-icon">${insight.icon}</div>
            <div>
                <div class="insight-title">${insight.title}</div>
                <div class="insight-text">${insight.text}</div>
            </div>
        </div>
        `;
    }).join('');
}

function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
}

function initNavPills() {
    const pills = document.querySelectorAll('.nav-pill');
    const sections = document.querySelectorAll('section[id]');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                pills.forEach(p => p.classList.remove('active'));
                const target = document.querySelector(`.nav-pill[href="#${entry.target.id}"]`);
                if (target) target.classList.add('active');
            }
        });
    }, { threshold: 0.3 });

    sections.forEach(sec => observer.observe(sec));
}
