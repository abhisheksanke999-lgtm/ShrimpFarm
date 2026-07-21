/* ==========================================================================
   Shrimp Farm Record Management System - Dummy Data Store
   ========================================================================== */

const ShrimpDataStore = {
  // Ponds Data
  ponds: [
    { id: 'POND-01', name: 'Pond Alpha (01)', area: 5000, depth: 1.8, source: 'Borewell / Tidal', status: 'Active', disinfected: true, limeKg: 250, fertilizer: 'Organic Probiotics 50kg', prepDate: '2026-06-01' },
    { id: 'POND-02', name: 'Pond Beta (02)', area: 4500, depth: 1.7, source: 'Sea Water Filtered', status: 'Active', disinfected: true, limeKg: 220, fertilizer: 'Urea + DAP 30kg', prepDate: '2026-06-05' },
    { id: 'POND-03', name: 'Pond Gamma (03)', area: 6000, depth: 2.0, source: 'Estuary Reservoir', status: 'Active', disinfected: true, limeKg: 300, fertilizer: 'Fermented Bio-juice 80L', prepDate: '2026-06-10' },
    { id: 'POND-04', name: 'Pond Delta (04)', area: 4000, depth: 1.6, source: 'Borewell', status: 'Preparation', disinfected: false, limeKg: 200, fertilizer: 'Dolomite 150kg', prepDate: '2026-07-15' },
    { id: 'POND-05', name: 'Pond Epsilon (05)', area: 5500, depth: 1.9, source: 'Sea Water Filtered', status: 'Harvested', disinfected: true, limeKg: 280, fertilizer: 'Organic Compost', prepDate: '2026-04-10' }
  ],

  // Seed Stocking Records
  stocking: [
    { id: 'STK-101', pondId: 'POND-01', date: '2026-06-05', supplier: 'CP Aquaculture Hatchery', species: 'Litopenaeus vannamei', plSize: 'PL-12', quantity: 250000, survivalRate: 88, cost: 3500, qualityGrade: 'A+', remarks: 'PCR negative for WSSV/EHP' },
    { id: 'STK-102', pondId: 'POND-02', date: '2026-06-10', supplier: 'Sheng Long Hatchery', species: 'Litopenaeus vannamei', plSize: 'PL-15', quantity: 200000, survivalRate: 92, cost: 2900, qualityGrade: 'A+', remarks: 'Active swimming, uniform size' },
    { id: 'STK-103', pondId: 'POND-03', date: '2026-06-15', supplier: 'Apex Aqua Hatchery', species: 'Penaeus monodon', plSize: 'PL-20', quantity: 180000, survivalRate: 84, cost: 3200, qualityGrade: 'A', remarks: 'Good stress test endurance' }
  ],

  // Daily Observations
  dailyLogs: [
    { id: 'LOG-501', pondId: 'POND-01', date: '2026-07-21', temp: 29.5, ph: 7.9, salinity: 22, do: 6.4, waterColor: 'Light Green', activity: 'Active Feeding', mortality: 0, avgWeight: 14.5, disease: 'None', notes: 'Checktray clean after 2 hours' },
    { id: 'LOG-502', pondId: 'POND-02', date: '2026-07-21', temp: 28.8, ph: 8.1, salinity: 24, do: 5.8, waterColor: 'Brownish Green', activity: 'Normal', mortality: 2, avgWeight: 12.8, disease: 'None', notes: 'Aerators running continuously' },
    { id: 'LOG-503', pondId: 'POND-03', date: '2026-07-20', temp: 30.1, ph: 8.4, salinity: 25, do: 5.2, waterColor: 'Dark Green', activity: 'Sluggish', mortality: 5, avgWeight: 16.2, disease: 'Mild Gill Fouling', notes: 'Applied mineral supplement' }
  ],

  // Feed Management
  feedLogs: [
    { id: 'FD-901', pondId: 'POND-01', brand: 'CP Nova Feed', type: 'Pellet No. 3', size: '1.8 mm', quantityKg: 180, feedingTime: '06:00, 11:00, 16:00, 21:00', stockLeftKg: 1420 },
    { id: 'FD-902', pondId: 'POND-02', brand: 'GroBest Premium', type: 'Pellet No. 2', size: '1.4 mm', quantityKg: 140, feedingTime: '06:30, 11:30, 16:30, 21:30', stockLeftKg: 850 },
    { id: 'FD-903', pondId: 'POND-03', brand: 'Uni-President Aqua', type: 'Pellet No. 4', size: '2.2 mm', quantityKg: 210, feedingTime: '06:00, 11:00, 16:00, 21:00', stockLeftKg: 2150 }
  ],

  // Water Quality Parameters
  waterQuality: [
    { pondId: 'POND-01', temp: 29.5, ph: 7.9, salinity: 22, do: 6.4, ammonia: 0.02, nitrite: 0.05, nitrate: 1.2, transparency: 35, status: 'Optimal' },
    { pondId: 'POND-02', temp: 28.8, ph: 8.1, salinity: 24, do: 5.8, ammonia: 0.15, nitrite: 0.12, nitrate: 2.0, transparency: 30, status: 'Optimal' },
    { pondId: 'POND-03', temp: 30.1, ph: 8.4, salinity: 25, do: 5.2, ammonia: 0.45, nitrite: 0.35, nitrate: 4.5, transparency: 22, status: 'Warning' }
  ],

  // Medicine & Treatments
  medicine: [
    { id: 'MED-301', pondId: 'POND-01', name: 'Aqua-Probiotic Plus', supplier: 'BioAqua Solutions', purpose: 'Water & Soil Remediation', dosage: '500 g / Ha', appliedDate: '2026-07-18', nextDate: '2026-07-25', cost: 120, qty: '2 kg' },
    { id: 'MED-302', pondId: 'POND-03', name: 'BKC 80% Disinfectant', supplier: 'Apex Chemical', purpose: 'Bacterial Control', dosage: '1.2 L / Ha', appliedDate: '2026-07-19', nextDate: '2026-07-26', cost: 85, qty: '5 L' }
  ],

  // Growth Monitoring
  growth: [
    { pondId: 'POND-01', doc: 45, abw: 14.5, adg: 0.32, fcr: 1.22, expHarvest: '2026-09-10', targetWeight: 22.0 },
    { pondId: 'POND-02', doc: 40, abw: 12.8, adg: 0.30, fcr: 1.28, expHarvest: '2026-09-18', targetWeight: 20.0 },
    { pondId: 'POND-03', doc: 35, abw: 16.2, adg: 0.41, fcr: 1.35, expHarvest: '2026-09-05', targetWeight: 25.0 }
  ],

  // Expense Records
  expenses: [
    { id: 'EXP-801', date: '2026-07-15', category: 'Feed', description: '2 Tons CP Pellet Feed', amount: 3200, invoiceNo: 'INV-9921', status: 'Paid' },
    { id: 'EXP-802', date: '2026-07-12', category: 'Electricity', description: 'Monthly Aerator & Pump Power Bill', amount: 1450, invoiceNo: 'INV-4410', status: 'Paid' },
    { id: 'EXP-803', date: '2026-07-10', category: 'Labor', description: 'Weekly Technician & Helper Wages', amount: 950, invoiceNo: 'INV-7701', status: 'Paid' },
    { id: 'EXP-804', date: '2026-07-08', category: 'Medicine', description: 'Probiotics & Vitamin C Fortifier', amount: 480, invoiceNo: 'INV-1092', status: 'Paid' }
  ],

  // Harvest Records
  harvest: [
    { id: 'HRV-401', pondId: 'POND-05', harvestDate: '2026-07-02', qtyKg: 4200, avgWeight: 21.5, buyer: 'Pacific Seafood Exports', pricePerKg: 7.20, totalRevenue: 30240, transportCost: 650, remarks: 'Export grade quality' },
    { id: 'HRV-402', pondId: 'POND-06', harvestDate: '2026-06-18', qtyKg: 3800, avgWeight: 19.8, buyer: 'Ocean Prime Traders', pricePerKg: 6.80, totalRevenue: 25840, transportCost: 500, remarks: 'Partial harvest completed' }
  ],

  // Quick Notifications
  notifications: [
    { id: 1, type: 'warning', title: 'Low Feed Alert', text: 'GroBest Pellet No.2 is below threshold (850kg remaining).', time: '10 mins ago' },
    { id: 2, type: 'danger', title: 'Water Quality Warning', text: 'Pond 03 Ammonia high (0.45 ppm). Action recommended.', time: '1 hour ago' },
    { id: 3, type: 'info', title: 'Treatment Scheduled', text: 'Pond 01 Probiotics application due in 4 days.', time: '3 hours ago' }
  ]
};
