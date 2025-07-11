-- Database initialization script
-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS oozo_db;

-- Connect to the database
\c oozo_db;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create regulations table
CREATE TABLE IF NOT EXISTS regulations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    search_vector TSVECTOR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    author VARCHAR(100),
    source VARCHAR(200),
    effective_date TIMESTAMP WITH TIME ZONE
);

-- Create services table
CREATE TABLE IF NOT EXISTS services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    contact_info TEXT,
    approval_type VARCHAR(50) DEFAULT 'required',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create analysis_results table
CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    original_text TEXT NOT NULL,
    modified_text TEXT NOT NULL,
    llm_comment TEXT NOT NULL,
    change_type VARCHAR(50) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    analysis_id UUID NOT NULL,
    document_pair_reference VARCHAR(500),
    document_pair_client VARCHAR(500)
);

-- Create regulation_services junction table
CREATE TABLE IF NOT EXISTS regulation_services (
    regulation_id UUID REFERENCES regulations(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id) ON DELETE CASCADE,
    PRIMARY KEY (regulation_id, service_id)
);

-- Create analysis_services junction table
CREATE TABLE IF NOT EXISTS analysis_services (
    analysis_result_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id) ON DELETE CASCADE,
    PRIMARY KEY (analysis_result_id, service_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_regulations_title ON regulations(title);
CREATE INDEX IF NOT EXISTS idx_regulations_category ON regulations(category);
CREATE INDEX IF NOT EXISTS idx_regulations_active ON regulations(active);
CREATE INDEX IF NOT EXISTS idx_regulations_created_at ON regulations(created_at);
CREATE INDEX IF NOT EXISTS idx_regulations_category_active ON regulations(category, active);

-- Create full-text search index
CREATE INDEX IF NOT EXISTS idx_regulations_search ON regulations USING GIN(search_vector);

-- Create trigram index for fuzzy search
CREATE INDEX IF NOT EXISTS idx_regulations_title_trgm ON regulations USING GIN(title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_regulations_content_trgm ON regulations USING GIN(content gin_trgm_ops);

-- Create indexes for services
CREATE INDEX IF NOT EXISTS idx_services_name ON services(name);
CREATE INDEX IF NOT EXISTS idx_services_active ON services(active);
CREATE INDEX IF NOT EXISTS idx_services_approval_type ON services(approval_type);

-- Create indexes for analysis results
CREATE INDEX IF NOT EXISTS idx_analysis_results_analysis_id ON analysis_results(analysis_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at ON analysis_results(created_at);
CREATE INDEX IF NOT EXISTS idx_analysis_results_severity ON analysis_results(severity);
CREATE INDEX IF NOT EXISTS idx_analysis_results_change_type ON analysis_results(change_type);

-- Create function to update search vector
CREATE OR REPLACE FUNCTION update_regulations_search_vector() RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('russian', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('russian', coalesce(NEW.content, '')), 'B') ||
        setweight(to_tsvector('russian', coalesce(NEW.category, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update search vector
DROP TRIGGER IF EXISTS regulations_search_vector_trigger ON regulations;
CREATE TRIGGER regulations_search_vector_trigger
    BEFORE INSERT OR UPDATE ON regulations
    FOR EACH ROW
    EXECUTE FUNCTION update_regulations_search_vector();

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS regulations_updated_at_trigger ON regulations;
CREATE TRIGGER regulations_updated_at_trigger
    BEFORE UPDATE ON regulations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS services_updated_at_trigger ON services;
CREATE TRIGGER services_updated_at_trigger
    BEFORE UPDATE ON services
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function for fuzzy search
CREATE OR REPLACE FUNCTION search_regulations(
    query_text TEXT,
    limit_count INTEGER DEFAULT 10,
    similarity_threshold REAL DEFAULT 0.3
) RETURNS TABLE(
    id UUID,
    title VARCHAR(500),
    content TEXT,
    category VARCHAR(100),
    relevance REAL,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.id,
        r.title,
        r.content,
        r.category,
        ts_rank(r.search_vector, plainto_tsquery('russian', query_text)) AS relevance,
        r.created_at
    FROM regulations r
    WHERE r.active = true
    AND (
        r.search_vector @@ plainto_tsquery('russian', query_text)
        OR similarity(r.title, query_text) > similarity_threshold
        OR similarity(r.content, query_text) > similarity_threshold
    )
    ORDER BY relevance DESC, r.created_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to get related services for a regulation
CREATE OR REPLACE FUNCTION get_regulation_services(regulation_uuid UUID)
RETURNS TABLE(
    service_id UUID,
    service_name VARCHAR(200),
    service_description TEXT,
    approval_type VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        s.name,
        s.description,
        s.approval_type
    FROM services s
    JOIN regulation_services rs ON s.id = rs.service_id
    WHERE rs.regulation_id = regulation_uuid
    AND s.active = true;
END;
$$ LANGUAGE plpgsql;

-- Create view for analysis statistics
CREATE OR REPLACE VIEW analysis_statistics AS
SELECT 
    DATE_TRUNC('day', created_at) as analysis_date,
    COUNT(*) as total_analyses,
    COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_count,
    COUNT(CASE WHEN severity = 'high' THEN 1 END) as high_count,
    COUNT(CASE WHEN severity = 'medium' THEN 1 END) as medium_count,
    COUNT(CASE WHEN severity = 'low' THEN 1 END) as low_count,
    AVG(confidence) as avg_confidence
FROM analysis_results
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY analysis_date DESC;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO oozo_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO oozo_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO oozo_user;

-- Create user if not exists (for development)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'oozo_user') THEN
        CREATE USER oozo_user WITH PASSWORD 'oozo_password';
    END IF;
END
$$;

-- Grant permissions to user
GRANT ALL PRIVILEGES ON DATABASE oozo_db TO oozo_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO oozo_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO oozo_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO oozo_user; 