-- Migration: Add experts field to cards table
-- Description: Stores identified expert agents for each card (JSON format)
-- Example: {"database": {"reason": "...", "confidence": "high", "identified_at": "..."}}

ALTER TABLE cards ADD COLUMN experts TEXT;
