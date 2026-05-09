/*
 Navicat Premium Dump SQL

 Source Server         : 本地
 Source Server Type    : MySQL
 Source Server Version : 80045 (8.0.45)
 Source Host           : localhost:3306
 Source Schema         : hypertension

 Target Server Type    : MySQL
 Target Server Version : 80045 (8.0.45)
 File Encoding         : 65001

 Date: 24/04/2026 22:22:46
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for alembic_version
-- ----------------------------
DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE `alembic_version`  (
  `version_num` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`version_num`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for admin_users
-- ----------------------------
DROP TABLE IF EXISTS `admin_users`;
CREATE TABLE `admin_users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_admin_users_email`(`email` ASC) USING BTREE,
  UNIQUE INDEX `ix_admin_users_username`(`username` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for bp_records
-- ----------------------------
DROP TABLE IF EXISTS `bp_records`;
CREATE TABLE `bp_records`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `systolic_bp` float NOT NULL,
  `diastolic_bp` float NOT NULL,
  `heart_rate` float NULL DEFAULT NULL,
  `recorded_at` datetime NOT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_bp_records_user_id`(`user_id` ASC) USING BTREE,
  INDEX `ix_bp_records_user_recorded_at`(`user_id` ASC, `recorded_at` ASC) USING BTREE,
  CONSTRAINT `fk_bp_records_user_id_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 212 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for prediction_records
-- ----------------------------
DROP TABLE IF EXISTS `prediction_records`;
CREATE TABLE `prediction_records`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `risk_probability` float NOT NULL,
  `risk_level` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `data_days_used` int NULL DEFAULT NULL,
  `confidence_level` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `cache_mode` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'fresh_train',
  `has_anomaly` tinyint(1) NOT NULL DEFAULT 0,
  `input_snapshot` json NULL,
  `fusion_meta` json NULL,
  `bp_forecast` json NULL,
  `training_meta` json NULL,
  `recommendations` json NULL,
  `anomaly_flags` json NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_prediction_records_user_id`(`user_id` ASC) USING BTREE,
  INDEX `ix_prediction_records_user_created_at`(`user_id` ASC, `created_at` ASC) USING BTREE,
  INDEX `ix_prediction_records_risk_created_at`(`risk_level` ASC, `created_at` ASC) USING BTREE,
  INDEX `ix_prediction_records_confidence_created_at`(`confidence_level` ASC, `created_at` ASC) USING BTREE,
  INDEX `ix_prediction_records_anomaly_created_at`(`has_anomaly` ASC, `created_at` ASC) USING BTREE,
  CONSTRAINT `fk_prediction_records_user_id_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_profiles
-- ----------------------------
DROP TABLE IF EXISTS `user_profiles`;
CREATE TABLE `user_profiles`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `avatar` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `diagnosis` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_user_profiles_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `fk_user_profiles_user_id_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 42 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_risk_factor_profiles
-- ----------------------------
DROP TABLE IF EXISTS `user_risk_factor_profiles`;
CREATE TABLE `user_risk_factor_profiles`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `age` float NULL DEFAULT NULL,
  `male` int NULL DEFAULT NULL,
  `height` float NULL DEFAULT NULL,
  `weight` float NULL DEFAULT NULL,
  `current_smoker` int NULL DEFAULT NULL,
  `cigs_per_day` float NULL DEFAULT NULL,
  `bp_meds` int NULL DEFAULT NULL,
  `diabetes` int NULL DEFAULT NULL,
  `tot_chol` float NULL DEFAULT NULL,
  `glucose` float NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_user_risk_factor_profiles_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `fk_user_risk_factor_profiles_user_id_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_prophet_models
-- ----------------------------
DROP TABLE IF EXISTS `user_prophet_models`;
CREATE TABLE `user_prophet_models`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `forecast_days` int NOT NULL,
  `model_version` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `data_signature` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `aggregation_mode` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `trained_at` datetime NOT NULL,
  `trained_until` date NOT NULL,
  `data_days_used` int NOT NULL,
  `total_history_days` int NOT NULL,
  `history_window_capped` tinyint(1) NOT NULL,
  `parameter_profile` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `weekly_enabled` tinyint(1) NOT NULL,
  `monthly_enabled` tinyint(1) NOT NULL,
  `storage_key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_user_prophet_models_data_signature`(`data_signature` ASC) USING BTREE,
  INDEX `ix_user_prophet_models_is_active`(`is_active` ASC) USING BTREE,
  INDEX `ix_user_prophet_models_model_version`(`model_version` ASC) USING BTREE,
  INDEX `ix_user_prophet_models_user_id`(`user_id` ASC) USING BTREE,
  INDEX `ix_user_prophet_models_active_slot_trained`(`user_id` ASC, `forecast_days` ASC, `is_active` ASC, `trained_at` ASC, `id` ASC) USING BTREE,
  CONSTRAINT `fk_user_prophet_models_user_id_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `ck_user_prophet_models_forecast_days_7` CHECK ((`forecast_days` = 7))
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_users_email`(`email` ASC) USING BTREE,
  UNIQUE INDEX `ix_users_username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 43 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
