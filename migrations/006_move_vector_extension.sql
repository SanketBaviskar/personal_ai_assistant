-- Create the extensions schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS extensions;

-- Move the vector extension to the new schema
ALTER EXTENSION vector SET SCHEMA extensions;

-- Update the database search path so unqualified "vector" type references still work
-- AND "extensions" is included for future lookups.
-- Note: This affects the database level config.
ALTER DATABASE postgres SET search_path TO "$user", public, extensions;

-- Alternatively, for the current role if we can't alter database:
-- ALTER ROLE current_user SET search_path TO "$user", public, extensions;

-- For redundancy, let's try setting it for the current role too, as ALTER DATABASE might require superuser if not owner
ALTER ROLE authenticated SET search_path TO "$user", public, extensions;
ALTER ROLE service_role SET search_path TO "$user", public, extensions;
-- Also for the 'postgres' user often used in dev
ALTER ROLE postgres SET search_path TO "$user", public, extensions;
