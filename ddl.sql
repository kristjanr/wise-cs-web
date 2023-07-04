CREATE TABLE article
(
    id                   bigserial PRIMARY KEY    NOT NULL,
    title                text                     NOT NULL UNIQUE,
    url                  text                     NOT NULL UNIQUE,
    html                 text                     NOT NULL,
    markdown             text                     NOT NULL,
    md_hash              text                     NOT NULL DEFAULT '',
    metadata             jsonb                    NOT NULL,
    section_title        text                     NULL,
    section_subtitle     text                     NULL,
    section_url          text                     NULL,
    subsection_title     text                     NULL,
    created_at           timestamp with time zone NOT NULL DEFAULT current_timestamp,
    updated_at           timestamp with time zone NOT NULL DEFAULT current_timestamp,
    deleted_at           timestamp with time zone NULL,
    md_ada_002_embedding double precision[]       NULL,
    questions_answers    jsonb                    NULL

);

CREATE OR REPLACE FUNCTION update_timestamp()
    RETURNS TRIGGER AS
$$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_article_modtime
    BEFORE UPDATE
    ON article
    FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();

CREATE OR REPLACE FUNCTION update_md_hash()
    RETURNS TRIGGER AS
$$
BEGIN
    NEW.md_hash = md5(NEW.markdown);
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_md_hash_trigger
    BEFORE INSERT OR UPDATE OF markdown
    ON article
    FOR EACH ROW
EXECUTE FUNCTION update_md_hash();

CREATE TABLE test_question_answer
(
    id                            bigserial,
    question                      text UNIQUE        NOT NULL,
    answer                        text               NOT NULL,
    article_url                   text               NOT NULL,
    md_ada_002_question_embedding double precision[] NOT NULL
);