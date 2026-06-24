let state = {
    category: {
        data: [],
        filtered: [],
        sortCol: null,
        sortAsc: true,
        searchQuery: ''
    },
    products: {
        data: [],
        filtered: [],
        sortCol: null,
        sortAsc: true,
        searchQuery: ''
    },
    loss: {
        data: [],
        filtered: [],
        sortCol: null,
        sortAsc: true,
        searchQuery: ''
    }
};

document.addEventListener('DOMContentLoaded', () => {
    fetch('data/analysis_results.json')
        .then(res => res.json())
        .then(data => {
            state.category.data = data.category_performance || [];
            state.category.filtered = [...state.category.data];

            state.products.data = data.top_products || [];
            state.products.filtered = [...state.products.data];

            state.loss.data = data.loss_making_products || [];
            state.loss.filtered = [...state.loss.data];

            renderKPIs(data.kpis);
            renderCategoryTable();
            renderProductsTable();
            renderLossSection();
            renderInsights(data.insights);
            initScrollAnimations();
            initNavPills();
            initSearchAndSort();
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

function renderCategoryTable() {
    const tbody = document.querySelector('#category-table tbody');
    const categories = state.category.filtered;
    if (categories.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 20px;">No categories match search criteria</td></tr>';
        return;
    }
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

function renderProductsTable() {
    const tbody = document.querySelector('#products-table tbody');
    const products = state.products.filtered;
    if (products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 20px;">No products match search criteria</td></tr>';
        return;
    }
    tbody.innerHTML = products.map(p => {
        let originalRank = state.products.data.findIndex(orig => orig.product_name === p.product_name) + 1;
        let rankClass = originalRank === 1 ? 'rank-1' : originalRank === 2 ? 'rank-2' : originalRank === 3 ? 'rank-3' : 'rank-default';
        return `
        <tr>
            <td><span class="rank-badge ${rankClass}">${originalRank}</span></td>
            <td style="font-weight: 600; color: var(--text-primary)">${p.product_name}</td>
            <td>${formatCurrency(p.revenue)}</td>
            <td>${formatNumber(p.quantity)}</td>
            <td class="${p.profit >= 0 ? 'profit-positive' : 'profit-negative'}">${formatCurrency(Math.abs(p.profit))}</td>
        </tr>
        `;
    }).join('');
}

function renderLossSection() {
    const lossProducts = state.loss.filtered;
    if (!state.loss.data || state.loss.data.length === 0) return;

    document.getElementById('loss-section').style.display = 'flex';
    document.getElementById('loss-container').style.display = 'block';
    document.getElementById('loss-count').textContent = lossProducts.length + ' Products';

    const tbody = document.querySelector('#loss-table tbody');
    if (lossProducts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 20px;">No products match search criteria</td></tr>';
        return;
    }
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

function initSearchAndSort() {
    setupSearch('category-search', 'category', renderCategoryTable);
    setupSearch('products-search', 'products', renderProductsTable);
    setupSearch('loss-search', 'loss', renderLossSection);

    document.querySelectorAll('th.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const tableName = th.dataset.table;
            const columnName = th.dataset.sort;
            handleSort(tableName, columnName, th);
        });
    });
}

function setupSearch(inputId, tableKey, renderFunc) {
    const input = document.getElementById(inputId);
    if (!input) return;
    input.addEventListener('input', (e) => {
        state[tableKey].searchQuery = e.target.value.toLowerCase().trim();
        applyFilterAndSort(tableKey);
        renderFunc();
    });
}

function handleSort(tableName, columnName, thElement) {
    const tableState = state[tableName];
    if (tableState.sortCol === columnName) {
        tableState.sortAsc = !tableState.sortAsc;
    } else {
        tableState.sortCol = columnName;
        tableState.sortAsc = true;
    }

    const headerRow = thElement.parentElement;
    headerRow.querySelectorAll('th.sortable').forEach(th => {
        if (th !== thElement) {
            th.classList.remove('asc', 'desc');
        }
    });

    thElement.classList.remove('asc', 'desc');
    thElement.classList.add(tableState.sortAsc ? 'asc' : 'desc');

    applyFilterAndSort(tableName);

    if (tableName === 'category') renderCategoryTable();
    else if (tableName === 'products') renderProductsTable();
    else if (tableName === 'loss') renderLossSection();
}

function applyFilterAndSort(tableKey) {
    const tableState = state[tableKey];
    let result = [...tableState.data];

    if (tableState.searchQuery) {
        const query = tableState.searchQuery;
        if (tableKey === 'category') {
            result = result.filter(item => item.category.toLowerCase().includes(query));
        } else if (tableKey === 'products' || tableKey === 'loss') {
            result = result.filter(item => item.product_name.toLowerCase().includes(query));
        }
    }

    if (tableState.sortCol) {
        const col = tableState.sortCol;
        const asc = tableState.sortAsc;
        result.sort((a, b) => {
            let valA = a[col];
            let valB = b[col];
            if (typeof valA === 'string') {
                return asc ? valA.localeCompare(valB) : valB.localeCompare(valA);
            } else {
                return asc ? valA - valB : valB - valA;
            }
        });
    }

    tableState.filtered = result;
}

