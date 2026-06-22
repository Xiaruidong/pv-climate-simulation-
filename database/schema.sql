-- 光伏气候效应模拟系统数据库
-- MySQL数据库结构

-- 创建数据库
CREATE DATABASE IF NOT EXISTS pv_climate_simulation
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE pv_climate_simulation;

-- ============== 用户表 ==============
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============== 模拟记录表 ==============
CREATE TABLE IF NOT EXISTS simulations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    record_id VARCHAR(100) UNIQUE NOT NULL COMMENT '唯一记录ID',

    -- 场景信息
    scenario_name VARCHAR(200) NOT NULL,
    description TEXT NULL,

    -- 时间信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- 状态信息
    status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'completed',
    error_message TEXT NULL,

    -- 计算时间信息
    calculation_time_ms INT NULL COMMENT '计算耗时(毫秒)',

    INDEX idx_user_id (user_id),
    INDEX idx_record_id (record_id),
    INDEX idx_created_at (created_at),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============== 输入参数表 ==============
CREATE TABLE IF NOT EXISTS simulation_parameters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    simulation_id INT NOT NULL,

    -- 光伏系统参数
    albedo_pv DECIMAL(10,6) NOT NULL COMMENT '光伏面板反照率',
    coverage_ratio DECIMAL(15,10) NOT NULL COMMENT '覆盖率',
    pv_efficiency DECIMAL(6,4) NOT NULL COMMENT '光伏效率',

    -- 地表反照率参数
    albedo_land DECIMAL(10,6) NOT NULL COMMENT '陆地反照率',
    albedo_ocean DECIMAL(10,6) NOT NULL COMMENT '海洋反照率',

    -- 气候参数
    co2_current DECIMAL(10,2) NOT NULL COMMENT 'CO2浓度(ppm)',
    initial_temp DECIMAL(6,2) NOT NULL COMMENT '初始温度(°C)',

    -- 模拟控制参数
    simulation_years INT NOT NULL COMMENT '模拟年数',
    calculation_method VARCHAR(50) DEFAULT 'euler',

    -- 附加参数（JSON格式）
    extra_params JSON NULL COMMENT '其他参数',

    UNIQUE KEY uk_sim_id (simulation_id),
    INDEX idx_coverage_ratio (coverage_ratio),
    INDEX idx_albedo_pv (albedo_pv),
    FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============== 计算结果表 ==============
CREATE TABLE IF NOT EXISTS simulation_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    simulation_id INT NOT NULL,

    -- 基准情景结果
    baseline_equilibrium_temp DECIMAL(10,6) NOT NULL,
    baseline_planetary_albedo DECIMAL(10,6) NOT NULL,
    baseline_equilibrium_time INT NOT NULL,
    baseline_temperature_series JSON NULL COMMENT '温度时间序列',
    baseline_convergence JSON NULL COMMENT '收敛性分析',

    -- 光伏情景结果
    pv_equilibrium_temp DECIMAL(10,6) NOT NULL,
    pv_planetary_albedo DECIMAL(10,6) NOT NULL,
    pv_equilibrium_time INT NOT NULL,
    pv_co2_reduction DECIMAL(15,6) NOT NULL,
    pv_final_co2_concentration DECIMAL(10,2) NOT NULL,
    pv_temperature_series JSON NULL COMMENT '温度时间序列',
    pv_convergence JSON NULL COMMENT '收敛性分析',

    -- 对比结果
    temperature_change DECIMAL(12,8) NOT NULL,
    albedo_change DECIMAL(12,8) NOT NULL,
    cooling_effect BOOLEAN NOT NULL,
    heat_island_effect DECIMAL(12,8) NOT NULL,
    cooling_efficiency DECIMAL(10,4) NOT NULL,

    -- 元数据
    calculation_metadata JSON NULL COMMENT '计算元数据',

    UNIQUE KEY uk_sim_id (simulation_id),
    INDEX idx_temperature_change (temperature_change),
    INDEX idx_cooling_efficiency (cooling_efficiency),
    INDEX idx_pv_co2_reduction (pv_co2_reduction),
    FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============== 标签表 ==============
CREATE TABLE IF NOT EXISTS tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(7) DEFAULT '#4a9eff',
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============== 模拟标签关联表 ==============
CREATE TABLE IF NOT EXISTS simulation_tags (
    simulation_id INT NOT NULL,
    tag_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (simulation_id, tag_id),
    FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============== 收藏表 ==============
CREATE TABLE IF NOT EXISTS favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    simulation_id INT NOT NULL,
    note TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_sim (user_id, simulation_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============== 对比组表 ==============
CREATE TABLE IF NOT EXISTS comparison_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============== 对比组项目表 ==============
CREATE TABLE IF NOT EXISTS comparison_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comparison_group_id INT NOT NULL,
    simulation_id INT NOT NULL,
    display_order INT DEFAULT 0,
    FOREIGN KEY (comparison_group_id) REFERENCES comparison_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============== 导出记录表 ==============
CREATE TABLE IF NOT EXISTS export_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    simulation_id INT NULL,
    export_type ENUM('single', 'batch', 'comparison') NOT NULL,
    file_format ENUM('json', 'csv', 'excel') NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    export_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_export_date (export_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============== 插入默认标签 ==============
INSERT INTO tags (name, color, description) VALUES
('高覆盖率', '#ff5747', '覆盖率 ≥ 1e-7'),
('中等覆盖率', '#ffa947', '1e-8 ≤ 覆盖率 < 1e-7'),
('低覆盖率', '#4ad97f', '覆盖率 < 1e-8'),
('镜面面板', '#4a9eff', '反照率 ≥ 0.9'),
('新型面板', '#00d9ff', '0.4 ≤ 反照率 < 0.9'),
('普通面板', '#a86855', '反照率 < 0.4'),
('高CO2', '#ff4757', 'CO2浓度 ≥ 800ppm'),
('低CO2', '#4ad97f', 'CO2浓度 ≤ 350ppm'),
('高效率', '#00ff9d', '冷却效率 > 10%'),
('低效率', '#ffa947', '冷却效率 < 5%');

-- ============== 创建视图 ==============

-- 模拟记录汇总视图
CREATE OR REPLACE VIEW simulation_summary AS
SELECT
    s.id,
    s.record_id,
    s.scenario_name,
    s.created_at,
    s.status,
    sp.albedo_pv,
    sp.coverage_ratio,
    sp.pv_efficiency,
    sp.co2_current,
    sr.temperature_change,
    sr.pv_co2_reduction,
    sr.cooling_efficiency,
    (SELECT GROUP_CONCAT(t.name) FROM simulation_tags st JOIN tags t ON st.tag_id = t.id WHERE st.simulation_id = s.id) as tags
FROM simulations s
LEFT JOIN simulation_parameters sp ON s.id = sp.simulation_id
LEFT JOIN simulation_results sr ON s.id = sr.simulation_id
WHERE s.status = 'completed';

-- ============== 创建存储过程 ==============

-- 自动标签生成存储过程
DELIMITER //
CREATE PROCEDURE generate_auto_tags(IN simulation_id INT)
BEGIN
    DECLARE v_coverage_ratio DECIMAL(15,10);
    DECLARE v_albedo_pv DECIMAL(10,6);
    DECLARE v_co2_current DECIMAL(10,2);
    DECLARE v_cooling_efficiency DECIMAL(10,4);

    -- 获取参数
    SELECT coverage_ratio, albedo_pv, co2_current INTO v_coverage_ratio, v_albedo_pv, v_co2_current
    FROM simulation_parameters WHERE simulation_id = simulation_id;

    -- 获取结果
    SELECT cooling_efficiency INTO v_cooling_efficiency
    FROM simulation_results WHERE simulation_id = simulation_id;

    -- 覆盖率标签
    IF v_coverage_ratio >= 1e-7 THEN
        INSERT IGNORE INTO simulation_tags (simulation_id, tag_id)
        SELECT simulation_id, id FROM tags WHERE name = '高覆盖率';
    ELSEIF v_coverage_ratio >= 1e-8 THEN
        INSERT IGNORE INTO simulation_tags (simulation_id, tag_id)
        SELECT simulation_id, id FROM tags WHERE name = '中等覆盖率';
    ELSE
        INSERT IGNORE INTO simulation_tags (simulation_id, tag_id)
        SELECT simulation_id, id FROM tags WHERE name = '低覆盖率';
    END IF;

    -- 面板类型标签
    IF v_albedo_pv >= 0.9 THEN
        INSERT IGNORE INTO simulation_tags (simulation_id, tag_id)
        SELECT simulation_id, id FROM tags WHERE name = '镜面面板';
    ELSEIF v_albedo_pv >= 0.4 THEN
        INSERT IGNORE INTO simulation_tags (simulation_id, tag_id)
        SELECT simulation_id, id FROM tags WHERE name = '新型面板';
    ELSE
        INSERT IGNORE INTO simulation_tags (simulation_id, tag_id)
        SELECT simulation_id, id FROM tags WHERE name = '普通面板';
    END IF;

    -- CO2浓度标签
    IF v_co2_current >= 800 THEN
        INSERT IGNORE INTO simulation_tags (simulation_id, tag_id)
        SELECT simulation_id, id FROM tags WHERE name = '高CO2';
    ELSEIF v_co2_current <= 350 THEN
        INSERT IGNORE INTO simulation_tags (simulation_id, tag_id)
        SELECT simulation_id, id FROM tags WHERE name = '低CO2';
    END IF;

    -- 效率标签
    IF v_cooling_efficiency > 10 THEN
        INSERT IGNORE INTO simulation_tags (simulation_id, tag_id)
        SELECT simulation_id, id FROM tags WHERE name = '高效率';
    ELSEIF v_cooling_efficiency < 5 THEN
        INSERT IGNORE INTO simulation_tags (simulation_id, tag_id)
        SELECT simulation_id, id FROM tags WHERE name = '低效率';
    END IF;
END //
DELIMITER ;

-- ============== 创建触发器 ==============

-- 在插入模拟结果后自动生成标签
DELIMITER //
CREATE TRIGGER after_simulation_result_insert
AFTER INSERT ON simulation_results
FOR EACH ROW
BEGIN
    CALL generate_auto_tags(NEW.simulation_id);
END //
DELIMITER ;

-- ============== 创建索引优化 ==============

-- 复合索引优化查询
CREATE INDEX idx_sim_composite ON simulations(created_at, status);
CREATE INDEX idx_params_composite ON simulation_parameters(coverage_ratio, albedo_pv);
CREATE INDEX idx_results_composite ON simulation_results(temperature_change, cooling_efficiency);

-- ============== 显示数据库结构 ==============
SHOW TABLES;
SHOW CREATE TABLE simulations;
SHOW CREATE TABLE simulation_parameters;
SHOW CREATE TABLE simulation_results;