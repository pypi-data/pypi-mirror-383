-- 修复主键缺少 AUTOINCREMENT 的表
-- 创建日期: 2025-09-14
-- 目的: 确保所有表的主键都使用 AUTOINCREMENT 避免 ID 复用

BEGIN TRANSACTION;

-- 1. 修复 project_pin 表
DROP INDEX IF EXISTS ix_project_pin_id;
DROP TABLE IF EXISTS project_pin_backup;
ALTER TABLE project_pin RENAME TO project_pin_backup;

CREATE TABLE project_pin (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects (id),
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX IF NOT EXISTS ix_project_pin_id ON project_pin (id);

INSERT INTO project_pin (project_id, user_id, created_at)
SELECT project_id, user_id, created_at FROM project_pin_backup;

DROP TABLE project_pin_backup;

-- 2. 修复 relate_eval_dataset 表  
DROP INDEX IF EXISTS ix_relate_eval_dataset_id;
DROP TABLE IF EXISTS relate_eval_dataset_backup;
ALTER TABLE relate_eval_dataset RENAME TO relate_eval_dataset_backup;

CREATE TABLE relate_eval_dataset (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    eval_id INTEGER,
    datasets_id INTEGER,
    FOREIGN KEY(eval_id) REFERENCES evaluate (id),
    FOREIGN KEY(datasets_id) REFERENCES datasets (id)
);

CREATE INDEX IF NOT EXISTS ix_relate_eval_dataset_id ON relate_eval_dataset (id);

INSERT INTO relate_eval_dataset (eval_id, datasets_id)
SELECT eval_id, datasets_id FROM relate_eval_dataset_backup;

DROP TABLE relate_eval_dataset_backup;

-- 3. 修复 relate_model_dataset 表
DROP INDEX IF EXISTS ix_relate_model_dataset_id;
DROP TABLE IF EXISTS relate_model_dataset_backup;
ALTER TABLE relate_model_dataset RENAME TO relate_model_dataset_backup;

CREATE TABLE relate_model_dataset (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    models_id INTEGER,
    datasets_id INTEGER,
    FOREIGN KEY(models_id) REFERENCES models (id),
    FOREIGN KEY(datasets_id) REFERENCES datasets (id)
);

CREATE INDEX IF NOT EXISTS ix_relate_model_dataset_id ON relate_model_dataset (id);

INSERT INTO relate_model_dataset (models_id, datasets_id)
SELECT models_id, datasets_id FROM relate_model_dataset_backup;

DROP TABLE relate_model_dataset_backup;

-- 4. 修复 tag 表
DROP TABLE IF EXISTS tag_backup;
ALTER TABLE tag RENAME TO tag_backup;

CREATE TABLE tag (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects (id),
    FOREIGN KEY(user_id) REFERENCES users (id)
);

INSERT INTO tag (name, project_id, user_id, created_at, updated_at)
SELECT name, project_id, user_id, created_at, updated_at FROM tag_backup;

DROP TABLE tag_backup;

-- 5. 修复 tag_sample 表
DROP TABLE IF EXISTS tag_sample_backup;
ALTER TABLE tag_sample RENAME TO tag_sample_backup;

CREATE TABLE tag_sample (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    sample_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY(sample_id) REFERENCES samples (id),
    FOREIGN KEY(tag_id) REFERENCES tag (id)
);

INSERT INTO tag_sample (sample_id, tag_id, created_at)
SELECT sample_id, tag_id, created_at FROM tag_sample_backup;

DROP TABLE tag_sample_backup;

COMMIT;

-- 验证修复结果
.schema project_pin
.schema relate_eval_dataset
.schema relate_model_dataset
.schema tag
.schema tag_sample