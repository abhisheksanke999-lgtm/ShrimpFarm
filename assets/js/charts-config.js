/* ==========================================================================
   Shrimp Farm Record Management System - Chart.js Configurations & Analytics
   ========================================================================== */

let chartInstances = {};

window.renderAllCharts = function () {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const textColor = isDark ? '#94A3B8' : '#64748B';
  const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)';

  Chart.defaults.color = textColor;
  Chart.defaults.font.family = 'Poppins';

  // 1. Monthly Expenses Chart (Bar Chart)
  const expCtx = document.getElementById('expenseChart');
  if (expCtx) {
    if (chartInstances.expChart) chartInstances.expChart.destroy();
    chartInstances.expChart = new Chart(expCtx, {
      type: 'bar',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
        datasets: [{
          label: 'Feed ($)',
          data: [4200, 3900, 4500, 5100, 4800, 5600, 5200],
          backgroundColor: '#0B4F6C',
          borderRadius: 6
        }, {
          label: 'Medicine & Utilities ($)',
          data: [1200, 1100, 1500, 1800, 1600, 2100, 1950],
          backgroundColor: '#FF8C42',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'top' } },
        scales: {
          x: { grid: { color: gridColor } },
          y: { grid: { color: gridColor }, beginAtZero: true }
        }
      }
    });
  }

  // 2. Feed Consumption Trend (Line Chart)
  const feedCtx = document.getElementById('feedConsumptionChart');
  if (feedCtx) {
    if (chartInstances.feedChart) chartInstances.feedChart.destroy();
    chartInstances.feedChart = new Chart(feedCtx, {
      type: 'line',
      data: {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
        datasets: [{
          label: 'Pond Alpha Feed (kg)',
          data: [350, 420, 580, 750, 920, 1100],
          borderColor: '#2E8B57',
          backgroundColor: 'rgba(46, 139, 87, 0.15)',
          fill: true,
          tension: 0.4,
          pointRadius: 4
        }, {
          label: 'Pond Beta Feed (kg)',
          data: [300, 390, 510, 680, 840, 980],
          borderColor: '#00A8E8',
          backgroundColor: 'transparent',
          borderDash: [5, 5],
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'top' } },
        scales: {
          x: { grid: { color: gridColor } },
          y: { grid: { color: gridColor } }
        }
      }
    });
  }

  // 3. Growth Rate (ABW in Grams) Chart
  const growthCtx = document.getElementById('growthChart');
  if (growthCtx) {
    if (chartInstances.growthChart) chartInstances.growthChart.destroy();
    chartInstances.growthChart = new Chart(growthCtx, {
      type: 'line',
      data: {
        labels: ['DOC 10', 'DOC 20', 'DOC 30', 'DOC 40', 'DOC 50', 'DOC 60'],
        datasets: [{
          label: 'Actual ABW (g)',
          data: [2.5, 6.2, 10.8, 14.5, 18.2, 22.4],
          borderColor: '#FF8C42',
          backgroundColor: 'rgba(255, 140, 66, 0.2)',
          fill: true,
          tension: 0.3
        }, {
          label: 'Target ABW (g)',
          data: [2.2, 5.8, 10.0, 14.0, 17.5, 21.0],
          borderColor: '#0B4F6C',
          borderDash: [4, 4],
          fill: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: gridColor } },
          y: { grid: { color: gridColor } }
        }
      }
    });
  }

  // 4. Profit & Revenue Trend Chart
  const profitCtx = document.getElementById('profitTrendChart');
  if (profitCtx) {
    if (chartInstances.profitChart) chartInstances.profitChart.destroy();
    chartInstances.profitChart = new Chart(profitCtx, {
      type: 'line',
      data: {
        labels: ['Cycle 1', 'Cycle 2', 'Cycle 3', 'Cycle 4', 'Current Forecast'],
        datasets: [{
          label: 'Revenue ($)',
          data: [24000, 28500, 31000, 36000, 42000],
          borderColor: '#2E8B57',
          backgroundColor: 'rgba(46, 139, 87, 0.1)',
          fill: true
        }, {
          label: 'Net Profit ($)',
          data: [9500, 11800, 13200, 15400, 18900],
          borderColor: '#0B4F6C',
          backgroundColor: 'rgba(11, 79, 108, 0.2)',
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: gridColor } },
          y: { grid: { color: gridColor } }
        }
      }
    });
  }

  // 5. Expense Breakdown Pie Chart
  const expPieCtx = document.getElementById('expensePieChart');
  if (expPieCtx) {
    if (chartInstances.expPieChart) chartInstances.expPieChart.destroy();
    chartInstances.expPieChart = new Chart(expPieCtx, {
      type: 'doughnut',
      data: {
        labels: ['Feed (62%)', 'Electricity (18%)', 'Medicine (8%)', 'Labor (7%)', 'Others (5%)'],
        datasets: [{
          data: [62, 18, 8, 7, 5],
          backgroundColor: ['#0B4F6C', '#2E8B57', '#FF8C42', '#00A8E8', '#94A3B8']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } }
      }
    });
  }
};

document.addEventListener('DOMContentLoaded', () => {
  if (typeof Chart !== 'undefined') {
    window.renderAllCharts();
  }
});
