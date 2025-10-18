-- SafetyMind Supabase Database Schema
-- Run this SQL in your Supabase SQL Editor

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    consequence VARCHAR(50),
    severity VARCHAR(50),
    location VARCHAR(255),
    activity VARCHAR(255),
    status VARCHAR(50) DEFAULT 'Submitted',
    occurred_at TIMESTAMP DEFAULT NOW(),
    reported_by VARCHAR(255),
    witnesses JSONB,
    equipment_involved JSONB,
    weather_conditions VARCHAR(255),
    time_of_day VARCHAR(50),
    injury_details JSONB,
    environmental_impact JSONB,
    cost_estimate DECIMAL(10,2),
    images JSONB,
    voice_recording_url VARCHAR(500),
    similar_incidents JSONB,
    mem0_context JSONB,
    ai_analysis JSONB,
    immediate_causes JSONB,
    underlying_causes JSONB,
    risk_level VARCHAR(50),
    extra JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_reports_event_type ON reports(event_type);
CREATE INDEX IF NOT EXISTS idx_reports_consequence ON reports(consequence);
CREATE INDEX IF NOT EXISTS idx_reports_severity ON reports(severity);
CREATE INDEX IF NOT EXISTS idx_reports_location ON reports(location);
CREATE INDEX IF NOT EXISTS idx_reports_activity ON reports(activity);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_occurred_at ON reports(occurred_at);
CREATE INDEX IF NOT EXISTS idx_reports_risk_level ON reports(risk_level);
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at);

-- Enable Row Level Security (RLS)
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- Create policy for public access (adjust as needed for your security requirements)
CREATE POLICY "Allow public access to reports" ON reports 
    FOR ALL USING (true);

-- Create policy for authenticated users (if you want to add auth later)
-- CREATE POLICY "Allow authenticated users to manage reports" ON reports 
--     FOR ALL USING (auth.role() = 'authenticated');

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_reports_updated_at 
    BEFORE UPDATE ON reports 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data (optional)
INSERT INTO reports (title, description, event_type, consequence, severity, location, activity, risk_level) VALUES
('Sample Near Miss', 'Worker noticed loose bolt on safety railing', 'NearMiss', 'Injury', 'Insignificant', 'Drilling Platform Alpha', 'Maintenance', 'Low'),
('Equipment Malfunction', 'Pump pressure gauge reading incorrectly', 'Incident', 'ProcessSafety', 'Moderate', 'Processing Facility', 'Operations', 'Medium'),
('Weather Delay', 'High winds caused work stoppage', 'NearMiss', 'Environmental', 'Insignificant', 'Offshore Platform', 'Drilling', 'Low')
ON CONFLICT DO NOTHING;
