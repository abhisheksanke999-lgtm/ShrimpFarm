-- ============================================================================
-- Run this ONCE in phpMyAdmin if your aquacontrol database already exists.
-- It adds user_id so each farmer only sees their own data.
-- Existing rows (if any) are assigned to the first user in the users table.
-- ============================================================================

USE `if0_42477062_aquacontrol`;

-- Add user_id columns (ignore errors if a column already exists)
ALTER TABLE `ponds`
  ADD COLUMN `user_id` INT NULL AFTER `pond_id`;

ALTER TABLE `daily_observations`
  ADD COLUMN `user_id` INT NULL AFTER `log_id`;

ALTER TABLE `feed_records`
  ADD COLUMN `user_id` INT NULL AFTER `feed_id`;

ALTER TABLE `expense_records`
  ADD COLUMN `user_id` INT NULL AFTER `expense_id`;

ALTER TABLE `harvest_records`
  ADD COLUMN `user_id` INT NULL AFTER `harvest_id`;

-- Assign any old shared rows to the first registered user
SET @owner_id = (SELECT `id` FROM `users` ORDER BY `id` ASC LIMIT 1);

UPDATE `ponds` SET `user_id` = @owner_id WHERE `user_id` IS NULL;
UPDATE `daily_observations` SET `user_id` = @owner_id WHERE `user_id` IS NULL;
UPDATE `feed_records` SET `user_id` = @owner_id WHERE `user_id` IS NULL;
UPDATE `expense_records` SET `user_id` = @owner_id WHERE `user_id` IS NULL;
UPDATE `harvest_records` SET `user_id` = @owner_id WHERE `user_id` IS NULL;

-- Make user_id required going forward
ALTER TABLE `ponds` MODIFY `user_id` INT NOT NULL;
ALTER TABLE `daily_observations` MODIFY `user_id` INT NOT NULL;
ALTER TABLE `feed_records` MODIFY `user_id` INT NOT NULL;
ALTER TABLE `expense_records` MODIFY `user_id` INT NOT NULL;
ALTER TABLE `harvest_records` MODIFY `user_id` INT NOT NULL;

-- Indexes for faster per-user lookups
ALTER TABLE `ponds` ADD INDEX `idx_ponds_user` (`user_id`);
ALTER TABLE `daily_observations` ADD INDEX `idx_daily_user` (`user_id`);
ALTER TABLE `feed_records` ADD INDEX `idx_feed_user` (`user_id`);
ALTER TABLE `expense_records` ADD INDEX `idx_expense_user` (`user_id`);
ALTER TABLE `harvest_records` ADD INDEX `idx_harvest_user` (`user_id`);
