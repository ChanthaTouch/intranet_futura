
-- v029a: Project file revisions and folder drag/move support

CREATE TABLE IF NOT EXISTS project_file_versions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id INT NOT NULL,
    revision_no INT NOT NULL DEFAULT 1,
    stored_path VARCHAR(500) NOT NULL,
    content_type VARCHAR(100),
    size_bytes BIGINT DEFAULT 0,
    uploaded_by INT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pfver_file FOREIGN KEY (file_id) REFERENCES project_files(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_pfver_file ON project_file_versions(file_id);
