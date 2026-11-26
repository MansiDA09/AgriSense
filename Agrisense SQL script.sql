CREATE DATABASE IF NOT EXISTS agrisense;

-- AGRISENSE: MYSQL DATA PIPELINE

USE agrisense;

-- 1. Check table structure
DESCRIBE agridata;

-- 2. Check total records
SELECT COUNT(*) AS total_records
FROM agridata;

-- 3. Preview agriculture data
SELECT * FROM agridata
LIMIT 10;

-- 4. Check Haryana records
SELECT COUNT(*) AS haryana_records
FROM agridata
WHERE State = 'Haryana';

-- 5. Filter Bhiwani records
SELECT * FROM agridata
WHERE State = 'Haryana' AND District = 'Bhiwani'
LIMIT 20;

-- 6. Check available crops in Bhiwani
SELECT DISTINCT Crop
FROM agridata
WHERE State = 'Haryana' AND District = 'Bhiwani';

-- 7. Check year-wise crop production
SELECT `Year`, Crop, SUM(Production) AS total_production
FROM agridata
WHERE State = 'Haryana' AND District = 'Bhiwani'
GROUP BY `Year`, Crop
ORDER BY `Year`;


