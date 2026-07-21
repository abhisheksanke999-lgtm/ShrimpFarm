/* ==========================================================================
   Shrimp Farm Record Management System - Interactive Modules & Calculators
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initTableSearchAndFilters();
  initPondViewSwitcher();
  initFeedCalculator();
  initProfitCalculator();
});

/* 1. Global Table Search & Filter Logic */
function initTableSearchAndFilters() {
  const searchInputs = document.querySelectorAll('.table-search-input');
  searchInputs.forEach(input => {
    input.addEventListener('input', (e) => {
      const term = e.target.value.toLowerCase();
      const targetTableId = input.getAttribute('data-table-target');
      const table = document.getElementById(targetTableId);
      if (!table) return;

      const rows = table.querySelectorAll('tbody tr');
      rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
      });
    });
  });
}

/* 2. Pond Module View Switcher (Table vs Card View) */
function initPondViewSwitcher() {
  const btnTable = document.getElementById('btnViewTable');
  const btnCard = document.getElementById('btnViewCard');
  const tableView = document.getElementById('pondTableView');
  const cardView = document.getElementById('pondCardView');

  if (btnTable && btnCard && tableView && cardView) {
    btnTable.addEventListener('click', () => {
      btnTable.classList.add('active', 'btn-primary-saas');
      btnTable.classList.remove('btn-outline-saas');
      btnCard.classList.remove('active', 'btn-primary-saas');
      btnCard.classList.add('btn-outline-saas');

      tableView.classList.remove('d-none');
      cardView.classList.add('d-none');
    });

    btnCard.addEventListener('click', () => {
      btnCard.classList.add('active', 'btn-primary-saas');
      btnCard.classList.remove('btn-outline-saas');
      btnTable.classList.remove('active', 'btn-primary-saas');
      btnTable.classList.add('btn-outline-saas');

      cardView.classList.remove('d-none');
      tableView.classList.add('d-none');
    });
  }
}

/* 3. Automatic Feed Calculator */
function initFeedCalculator() {
  const calcForm = document.getElementById('feedCalcForm');
  if (!calcForm) return;

  const abwInput = document.getElementById('calcAbw');
  const qtyInput = document.getElementById('calcShrimpCount');
  const rateSelect = document.getElementById('calcFeedRate');
  const resultDisplay = document.getElementById('calcDailyFeedResult');

  function calculateFeed() {
    const abw = parseFloat(abwInput.value) || 0; // grams
    const count = parseFloat(qtyInput.value) || 0; // count
    const ratePct = parseFloat(rateSelect.value) || 3.0; // % body weight

    if (abw > 0 && count > 0) {
      const totalBiomassKg = (abw * count) / 1000;
      const dailyFeedKg = (totalBiomassKg * (ratePct / 100)).toFixed(2);
      const perFeedKg = (dailyFeedKg / 4).toFixed(2); // 4 feedings

      resultDisplay.innerHTML = `
        <div class="p-3 glass-card rounded-md">
          <div class="text-muted small">Estimated Total Biomass</div>
          <div class="fs-4 fw-bold text-primary">${totalBiomassKg.toLocaleString(undefined, {maximumFractionDigits: 1})} kg</div>
          <hr class="my-2">
          <div class="d-flex justify-content-between align-items-center">
            <span>Recommended Daily Feed:</span>
            <span class="fs-4 fw-bold text-success">${dailyFeedKg} kg / day</span>
          </div>
          <div class="small text-muted mt-1">Split into 4 feedings: <strong>${perFeedKg} kg</strong> per meal.</div>
        </div>
      `;
    }
  }

  [abwInput, qtyInput, rateSelect].forEach(el => {
    if (el) el.addEventListener('input', calculateFeed);
  });
}

/* 4. Interactive Profit & ROI Calculator */
function initProfitCalculator() {
  const form = document.getElementById('profitCalcForm');
  if (!form) return;

  const inputs = ['calcHarvestQty', 'calcPricePerKg', 'calcFeedExpense', 'calcMedicineExpense', 'calcUtilityExpense', 'calcLaborExpense', 'calcOtherExpense'];
  
  function updateProfitResults() {
    const qty = parseFloat(document.getElementById('calcHarvestQty')?.value) || 0;
    const price = parseFloat(document.getElementById('calcPricePerKg')?.value) || 0;
    const feed = parseFloat(document.getElementById('calcFeedExpense')?.value) || 0;
    const med = parseFloat(document.getElementById('calcMedicineExpense')?.value) || 0;
    const util = parseFloat(document.getElementById('calcUtilityExpense')?.value) || 0;
    const labor = parseFloat(document.getElementById('calcLaborExpense')?.value) || 0;
    const other = parseFloat(document.getElementById('calcOtherExpense')?.value) || 0;

    const totalRev = qty * price;
    const totalExp = feed + med + util + labor + other;
    const netProfit = totalRev - totalExp;
    const roi = totalExp > 0 ? ((netProfit / totalExp) * 100).toFixed(1) : 0;
    const costPerKg = qty > 0 ? (totalExp / qty).toFixed(2) : 0;

    const resRev = document.getElementById('resTotalRevenue');
    const resExp = document.getElementById('resTotalExpenses');
    const resProfit = document.getElementById('resNetProfit');
    const resRoi = document.getElementById('resRoi');
    const resCostKg = document.getElementById('resCostPerKg');

    if (resRev) resRev.innerText = `$${totalRev.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    if (resExp) resExp.innerText = `$${totalExp.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    if (resProfit) {
      resProfit.innerText = `$${netProfit.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
      resProfit.className = netProfit >= 0 ? 'profit-result-val text-success' : 'profit-result-val text-danger';
    }
    if (resRoi) resRoi.innerText = `${roi}%`;
    if (resCostKg) resCostKg.innerText = `$${costPerKg} / kg`;
  }

  inputs.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', updateProfitResults);
  });

  updateProfitResults();
}

/* 5. Print & Report Generator Simulation */
window.printReport = function () {
  window.print();
};

window.exportExcel = function () {
  showToast('Exporting Excel report file...', 'info');
  setTimeout(() => {
    showToast('Excel report generated successfully!', 'success');
  }, 1500);
};

window.exportPDF = function () {
  showToast('Generating PDF summary report...', 'info');
  setTimeout(() => {
    showToast('PDF report downloaded!', 'success');
  }, 1500);
};
