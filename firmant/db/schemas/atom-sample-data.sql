SET search_path = atom;

DELETE FROM entry_revisions CASCADE;
DELETE FROM entries CASCADE;
DELETE FROM people CASCADE;
DELETE FROM categories CASCADE;
DELETE FROM content CASCADE;

-- Insert some sample post content.  These represent two revisions of the same
-- post.
INSERT INTO content (id, content, summary) VALUES
    (1,
     'This is the main content of revision one.',
     'This is the summary of revision one.');

INSERT INTO content (id, content, summary) VALUES
    (2,
     'This is the main content of revision two.',
     'This is the summary of revision two.');

-- Insert a sample person (me).  Not my actual email
INSERT INTO people (name, uri, email) VALUES
    ('Robert Escriva',
     'rob@/dev/null',
     'http://robescriva.com');

-- Insert a general category.
INSERT INTO categories (term, label) VALUES ('General', 'All topics');

-- Insert the test entry and its two revisions.
INSERT INTO entries
    (slug, published_date, published_time, author, category, rights) VALUES
    ('sample',
     '2009-2-13',
     '233130 EST',
     'Robert Escriva',
     'General',
     'Same as source.');

INSERT INTO entry_revisions
    (slug, published_date, updated, title, content) VALUES
    ('sample',
     '2009-2-13',
     '2009-2-13 233130 EST',
     'Unix 1234567890',
     1);

INSERT INTO entry_revisions
    (slug, published_date, updated, title, content) VALUES
    ('sample',
     '2009-2-13',
     '2009-2-13 233131 EST',
     'Unix 1234567890',
     2);
