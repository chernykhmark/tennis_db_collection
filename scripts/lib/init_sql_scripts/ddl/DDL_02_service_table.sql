CREATE TABLE IF NOT EXISTS stg.srv_wf_settings (
    id serial NOT NULL PRIMARY KEY,
    workflow_key varchar NOT NULL UNIQUE,
    workflow_settings JSON NOT NULL
);