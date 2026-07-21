-- ============================================================================
-- Shrimp Farm Record Management System - Complete Database Schema (XAMPP / MySQL)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS `shrimp_farm_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `shrimp_farm_db`;

-- ----------------------------------------------------------------------------
-- Table 1: Users
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `full_name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(120) NOT NULL UNIQUE,
  `password` VARCHAR(255) NOT NULL,
  `role` ENUM('Owner', 'Manager', 'Technician') DEFAULT 'Owner',
  `avatar` VARCHAR(255) DEFAULT 'default_avatar.jpg',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `users` (`full_name`, `email`, `password`, `role`) VALUES
('John Sterling', 'admin@shrimpfarm.com', '$2y$10$e0MYzXyjpJS7Pd0RVvHwHe1V.x15WwLdJ.kX9O5lQv3oW7l', 'Owner');

-- ----------------------------------------------------------------------------
-- Table 2: Ponds
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `ponds`;
CREATE TABLE `ponds` (
  `pond_id` VARCHAR(20) PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `area_sqm` DECIMAL(10,2) NOT NULL,
  `depth_m` DECIMAL(4,2) NOT NULL,
  `water_source` VARCHAR(100) NOT NULL,
  `status` ENUM('Preparation', 'Active', 'Harvested', 'Maintenance') DEFAULT 'Preparation',
  `disinfected` TINYINT(1) DEFAULT 0,
  `lime_kg` DECIMAL(8,2) DEFAULT 0,
  `fertilizer_details` TEXT,
  `prep_date` DATE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `ponds` (`pond_id`, `name`, `area_sqm`, `depth_m`, `water_source`, `status`, `disinfected`, `lime_kg`, `fertilizer_details`, `prep_date`) VALUES
('POND-01', 'Pond Alpha (01)', 5000.00, 1.80, 'Borewell / Tidal', 'Active', 1, 250.00, 'Organic Probiotics 50kg', '2026-06-01'),
('POND-02', 'Pond Beta (02)', 4500.00, 1.70, 'Sea Water Filtered', 'Active', 1, 220.00, 'Urea + DAP 30kg', '2026-06-05'),
('POND-03', 'Pond Gamma (03)', 6000.00, 2.00, 'Estuary Reservoir', 'Active', 1, 300.00, 'Fermented Bio-juice 80L', '2026-06-10'),
('POND-04', 'Pond Delta (04)', 4000.00, 1.60, 'Borewell', 'Preparation', 0, 200.00, 'Dolomite 150kg', '2026-07-15');

-- ----------------------------------------------------------------------------
-- Table 3: Seed Stocking Records
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `stocking_records`;
CREATE TABLE `stocking_records` (
  `stocking_id` VARCHAR(20) PRIMARY KEY,
  `pond_id` VARCHAR(20) NOT NULL,
  `stocking_date` DATE NOT NULL,
  `supplier` VARCHAR(150) NOT NULL,
  `species` VARCHAR(100) NOT NULL,
  `pl_size` VARCHAR(20) NOT NULL,
  `quantity` INT NOT NULL,
  `survival_rate` DECIMAL(5,2) DEFAULT 100.00,
  `cost` DECIMAL(10,2) NOT NULL,
  `remarks` TEXT,
  FOREIGN KEY (`pond_id`) REFERENCES `ponds`(`pond_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `stocking_records` (`stocking_id`, `pond_id`, `stocking_date`, `supplier`, `species`, `pl_size`, `quantity`, `survival_rate`, `cost`, `remarks`) VALUES
('STK-101', 'POND-01', '2026-06-05', 'CP Aquaculture Hatchery', 'Litopenaeus vannamei', 'PL-12', 250000, 88.00, 3500.00, 'PCR negative for WSSV/EHP'),
('STK-102', 'POND-02', '2026-06-10', 'Sheng Long Hatchery', 'Litopenaeus vannamei', 'PL-15', 200000, 92.00, 2900.00, 'Active swimming, uniform size');

-- ----------------------------------------------------------------------------
-- Table 4: Daily Observations
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `daily_observations`;
CREATE TABLE `daily_observations` (
  `log_id` VARCHAR(20) PRIMARY KEY,
  `pond_id` VARCHAR(20) NOT NULL,
  `log_date` DATE NOT NULL,
  `temperature` DECIMAL(4,2),
  `ph` DECIMAL(4,2),
  `salinity` DECIMAL(4,2),
  `dissolved_oxygen` DECIMAL(4,2),
  `water_color` VARCHAR(50),
  `activity` VARCHAR(100),
  `mortality_count` INT DEFAULT 0,
  `avg_weight_g` DECIMAL(6,2),
  `disease_symptoms` VARCHAR(255),
  `notes` TEXT,
  FOREIGN KEY (`pond_id`) REFERENCES `ponds`(`pond_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `daily_observations` (`log_id`, `pond_id`, `log_date`, `temperature`, `ph`, `salinity`, `dissolved_oxygen`, `water_color`, `activity`, `mortality_count`, `avg_weight_g`, `disease_symptoms`, `notes`) VALUES
('LOG-501', 'POND-01', '2026-07-21', 29.50, 7.90, 22.00, 6.40, 'Light Green', 'Active Feeding', 0, 14.50, 'None', 'Checktray clean after 2 hours'),
('LOG-502', 'POND-02', '2026-07-21', 28.80, 8.10, 24.00, 5.80, 'Brownish Green', 'Normal', 2, 12.80, 'None', 'Aerators running continuously');

-- ----------------------------------------------------------------------------
-- Table 5: Feed Records
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `feed_records`;
CREATE TABLE `feed_records` (
  `feed_id` VARCHAR(20) PRIMARY KEY,
  `pond_id` VARCHAR(20) NOT NULL,
  `feed_brand` VARCHAR(100) NOT NULL,
  `feed_type` VARCHAR(50) NOT NULL,
  `feed_size` VARCHAR(20) NOT NULL,
  `quantity_kg` DECIMAL(8,2) NOT NULL,
  `feeding_time` VARCHAR(100),
  `remaining_stock_kg` DECIMAL(10,2),
  `entry_date` DATE NOT NULL,
  FOREIGN KEY (`pond_id`) REFERENCES `ponds`(`pond_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `feed_records` (`feed_id`, `pond_id`, `feed_brand`, `feed_type`, `feed_size`, `quantity_kg`, `feeding_time`, `remaining_stock_kg`, `entry_date`) VALUES
('FD-901', 'POND-01', 'CP Nova Feed', 'Pellet No. 3', '1.8 mm', 180.00, '06:00, 11:00, 16:00, 21:00', 1420.00, '2026-07-21'),
('FD-902', 'POND-02', 'GroBest Premium', 'Pellet No. 2', '1.4 mm', 140.00, '06:30, 11:30, 16:30, 21:30', 850.00, '2026-07-21');

-- ----------------------------------------------------------------------------
-- Table 6: Expense Records
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `expense_records`;
CREATE TABLE `expense_records` (
  `expense_id` VARCHAR(20) PRIMARY KEY,
  `expense_date` DATE NOT NULL,
  `category` ENUM('Feed', 'Medicine', 'Electricity', 'Labor', 'Transportation', 'Equipment', 'Maintenance', 'Other') NOT NULL,
  `description` VARCHAR(255) NOT NULL,
  `amount` DECIMAL(10,2) NOT NULL,
  `invoice_no` VARCHAR(50),
  `status` ENUM('Paid', 'Pending') DEFAULT 'Paid'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `expense_records` (`expense_id`, `expense_date`, `category`, `description`, `amount`, `invoice_no`, `status`) VALUES
('EXP-801', '2026-07-15', 'Feed', '2 Tons CP Pellet Feed', 3200.00, 'INV-9921', 'Paid'),
('EXP-802', '2026-07-12', 'Electricity', 'Monthly Aerator & Pump Power Bill', 1450.00, 'INV-4410', 'Paid');
