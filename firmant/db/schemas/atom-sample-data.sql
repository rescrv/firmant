SET search_path = atom;

DELETE FROM entry_revisions CASCADE;
DELETE FROM entries CASCADE;
DELETE FROM people CASCADE;
DELETE FROM categories CASCADE;
DELETE FROM content CASCADE;
DELETE FROM feeds CASCADE;
DELETE FROM _feeds_entries_join;

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

INSERT INTO content (id, content, summary) VALUES
    (3,
     'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus eget
     ante sit amet elit condimentum varius. Nullam blandit pede quis neque.
     Suspendisse elit erat, malesuada quis, ultrices cursus, pretium eget,
     tortor. Sed volutpat pede in neque rhoncus aliquet. In vulputate, tellus id
     scelerisque vestibulum, eros diam vehicula massa, ac mollis leo augue quis
     tortor. Vivamus sed eros vitae tortor tincidunt consequat. Morbi in erat
     non erat tristique accumsan. Quisque ornare libero ut turpis. Phasellus et
     tortor. Vestibulum dapibus aliquet sapien. Quisque ut ante in erat auctor
     accumsan. Morbi accumsan dolor ut est.

     Nam urna lectus, auctor vel, placerat ac, fringilla interdum, leo. Donec
     congue venenatis lorem. Mauris pellentesque venenatis est. Mauris nisl
     dolor, ultrices a, condimentum vel, consequat sit amet, risus. Nulla
     porttitor nisl ut magna venenatis commodo. Donec sagittis leo in neque. Cum
     sociis natoque penatibus et magnis dis parturient montes, nascetur
     ridiculus mus. In hac habitasse platea dictumst. Praesent libero velit,
     volutpat sit amet, molestie id, condimentum nec, lorem. Aliquam erat
     volutpat. Vivamus scelerisque purus nec nulla. Aliquam tortor. Suspendisse
     laoreet porta augue. Curabitur at sapien in enim consequat blandit. Nulla
     ac dui. Nunc felis est, tempor sit amet, tincidunt id, auctor quis, eros.
     In molestie est a neque. Aliquam erat volutpat. Nam commodo tincidunt
     magna.  Morbi justo leo, faucibus nec, consectetur id, sodales vitae,
     nunc.',
     'A generated loren ipsum paragraph.');

-- Insert a sample person (me).  Not my actual email
INSERT INTO people (name, uri, email) VALUES
    ('Robert Escriva',
     'http://robescriva.com',
     'rob@example.org');

INSERT INTO people (name, uri, email) VALUES
    ('Loren Ipsum Generator',
     'http://www.lipsum.com',
     'lipsum@example.org');

-- Insert a general category.
INSERT INTO categories (term, label) VALUES ('General', 'All topics');
INSERT INTO categories (term, label) VALUES
    ('Generated',
     E'You can\'t tell a computer wrote it.');

-- Insert the test entry and its two revisions.
INSERT INTO entries
    (slug, published_date, published_time, author, category, rights) VALUES
    ('sample',
     '2009-2-13',
     '233130 EST',
     'Robert Escriva',
     'General',
     'Same as source.');

INSERT INTO entries
    (slug, published_date, published_time, author, category, rights) VALUES
    ('loren-ipsum',
     '2009-2-17',
     '113130 EST',
     'Loren Ipsum Generator',
     'Generated',
     'Same as source.');

INSERT INTO entries
    (slug, published_date, published_time, author, category, rights) VALUES
    ('sample',
     '2009-2-17',
     '163130 EST',
     'Loren Ipsum Generator',
     'Generated',
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

INSERT INTO entry_revisions
    (slug, published_date, updated, title, content) VALUES
    ('loren-ipsum',
     '2009-2-17',
     '2009-2-17 113130 EST',
     'Loren Ipsum ...',
     3);

INSERT INTO entry_revisions
    (slug, published_date, updated, title, content) VALUES
    ('sample',
     '2009-2-17',
     '2009-2-17 113130 EST',
     'Loren Ipsum ...',
     1);

INSERT INTO feeds
    (slug, title, rights, subtitle) VALUES
    ('general',
     'General Content',
     'Same as source.',
     'This is a feed that holds general content');

INSERT INTO _feeds_entries_join
    (feeds_slug, entries_slug, entries_published_date) VALUES
    ('general',
     'sample',
     '2009-2-13');

INSERT INTO _feeds_entries_join
    (feeds_slug, entries_slug, entries_published_date) VALUES
    ('general',
     'loren-ipsum',
     '2009-2-17');
