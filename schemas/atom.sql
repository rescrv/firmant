-- This file contains the sql necessary to create a database used for storing
-- the data associated with atom feeds.  It provides the storage backend for
-- Firmant.

SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

CREATE SCHEMA atom;

COMMENT ON SCHEMA atom IS
'This schema provides the set of functionality defined in the atom specification
that Firmant requires.  Some attributes will be automatically generated, and are
not stored in these relations.';


SET search_path = atom;


--
-- Name: _entries_authors_join; Type: TABLE; Schema: atom; Owner: axelrod; Tablespace: 
--

CREATE TABLE _entries_authors_join (
    entry_id character varying,
    author_id character varying
);


--
-- Name: _feeds_entries_join; Type: TABLE; Schema: atom; Owner: axelrod; Tablespace: 
--

CREATE TABLE _feeds_entries_join (
    feed_id character varying,
    entry_id character varying
);


--
-- Name: _link_rel_values; Type: TABLE; Schema: atom; Owner: axelrod; Tablespace: 
--

CREATE TABLE _link_rel_values (
    id character varying NOT NULL
);


--
-- Name: TABLE _link_rel_values; Type: COMMENT; Schema: atom; Owner: axelrod
--

COMMENT ON TABLE _link_rel_values IS 'The possible values a link''s rel attribute can take.';


--
-- The people relation
--

CREATE TABLE people (
    name VARCHAR(32),
    uri VARCHAR(2048),
    email VARCHAR(320),
    CONSTRAINT people_pkey PRIMARY KEY (name)
);

COMMENT ON TABLE people IS
'The name is limited to 32 characters as that seems long enough for most any
name.

The URI is limited to 2048 characters as some browsers with majority market
share do not accept a longer URI (besides, such a link would most likely be
spam.)

The email is limited to 320 (64+1+255) characters as that is the maximum length
of an email address.';


--
-- The categories relation
--

CREATE TABLE categories (
    term VARCHAR(32),
    label VARCHAR(255),
    CONSTRAINT categories_pkey PRIMARY KEY (term),
    CONSTRAINT categories_valid_term CHECK (term ~ E'^[-\\_a-zA-Z0-9]{1,32}$')
);

COMMENT ON TABLE categories IS 'Scheme can be generated.';


--
-- The content relation
--

CREATE TABLE content (
    id SERIAL,
    content TEXT,
    summary TEXT,
    CONSTRAINT content_pkey PRIMARY KEY (id)
);

COMMENT ON TABLE content is
'This provides a minimal set of the functionality required by the atom spec.
Source attributes are not supported at this point in time.  The type attribute
is not stored in the database.  It will be generated when markdown support is
implemented.';


--
-- The entries relation
--

CREATE TABLE entries (
    slug VARCHAR(96) NOT NULL,
    published_date DATE,
    published_time TIME(0) WITH TIME ZONE,
    author VARCHAR(32),
    category VARCHAR(32),
    rights TEXT,
    CONSTRAINT entries_pkey PRIMARY KEY (slug, published_date),
    CONSTRAINT entries_valid_slug CHECK (slug ~ E'^[-\\_a-zA-Z0-9]{1,96}$'),
    CONSTRAINT entries_author_fkey
        FOREIGN KEY (author) REFERENCES people (name)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT entries_category_fkey
        FOREIGN KEY (category) REFERENCES categories (term)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

COMMENT ON TABLE entries IS
'This table contains the information that should be the same for all
revisions of a post.  As only the most current revision should be public, this
table ensures that the author, categories and rights stay consistent across
edits.';


--
-- The entry_revisions relation
--

CREATE TABLE entry_revisions (
    slug VARCHAR(96) NOT NULL,
    published_date DATE,
    published_time TIME(0) WITH TIME ZONE,
    updated TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    title VARCHAR(96) NOT NULL,
    content INTEGER,
    summary INTEGER,
    CONSTRAINT entry_revisions_pkey PRIMARY KEY (slug, published_date, updated),
    CONSTRAINT entry_revisions_entries_fkey
        FOREIGN KEY (slug, published_date)
        REFERENCES entries (slug, published_date)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT entry_revisions_content_fkey
        FOREIGN KEY (content) REFERENCES content (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT entry_revisions_summary_fkey
        FOREIGN KEY (summary) REFERENCES content (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

COMMENT ON TABLE entry_revisions IS
'This table has information that is able to be unique to a particular edit.  The
slug and published relate to the ''entries'' table.  The title can change in a
particular revision, as can the references to the content and summary.';


--
-- Name: feeds; Type: TABLE; Schema: atom; Owner: axelrod; Tablespace: 
--

CREATE TABLE feeds (
    id character varying NOT NULL,
    title character varying NOT NULL,
    icon character varying,
    logo character varying,
    rights text,
    subtitle text,
    link integer
);


--
-- Name: TABLE feeds; Type: COMMENT; Schema: atom; Owner: axelrod
--

COMMENT ON TABLE feeds IS 'Updated should be generated from the feed''s contents.
Author is left for each entry to have.
Category is left for each entry to have.
Contributor is not currently implemented.
Generator should be generated by the software.

Currently only one link is supported (we may want to change this).

Constraints not currently implemented for links: "A feed is limited to one alternate per type and hreflang. A feed should contain a link back to the feed itself."';


--
-- Name: links; Type: TABLE; Schema: atom; Owner: axelrod; Tablespace: 
--

CREATE TABLE links (
    id integer NOT NULL,
    href character varying NOT NULL,
    type character varying,
    hreflang character varying,
    title character varying,
    rel character varying DEFAULT 'alternate'::character varying
);


--
-- Name: TABLE links; Type: COMMENT; Schema: atom; Owner: axelrod
--

COMMENT ON TABLE links IS 'length is not supported for now.';


--
-- Name: links_id_seq; Type: SEQUENCE; Schema: atom; Owner: axelrod
--

CREATE SEQUENCE links_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: links_id_seq; Type: SEQUENCE OWNED BY; Schema: atom; Owner: axelrod
--

ALTER SEQUENCE links_id_seq OWNED BY links.id;


--
-- Name: links_id_seq; Type: SEQUENCE SET; Schema: atom; Owner: axelrod
--

SELECT pg_catalog.setval('links_id_seq', 1, false);


--
-- Name: id; Type: DEFAULT; Schema: atom; Owner: axelrod
--

ALTER TABLE links ALTER COLUMN id SET DEFAULT nextval('links_id_seq'::regclass);


--
-- Data for Name: _link_rel_values; Type: TABLE DATA; Schema: atom; Owner: axelrod
--

COPY _link_rel_values (id) FROM stdin;
alternate
enclosure
related
self
via
\.


--
-- Name: _link_rel_values_pkey; Type: CONSTRAINT; Schema: atom; Owner: axelrod; Tablespace: 
--

--ALTER TABLE ONLY _link_rel_values
--    ADD CONSTRAINT _link_rel_values_pkey PRIMARY KEY (id);


--
-- Name: feeds_pkey; Type: CONSTRAINT; Schema: atom; Owner: axelrod; Tablespace: 
--

--ALTER TABLE ONLY feeds
--    ADD CONSTRAINT feeds_pkey PRIMARY KEY (id);


--
-- Name: links_pkey; Type: CONSTRAINT; Schema: atom; Owner: axelrod; Tablespace: 
--

--ALTER TABLE ONLY links
--    ADD CONSTRAINT links_pkey PRIMARY KEY (id);


--
-- Name: _entry_author_set_author_id_fkey; Type: FK CONSTRAINT; Schema: atom; Owner: axelrod
--

--ALTER TABLE ONLY _entries_authors_join
--    ADD CONSTRAINT _entry_author_set_author_id_fkey FOREIGN KEY (author_id) REFERENCES people(name) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: _entry_author_set_entry_id_fkey; Type: FK CONSTRAINT; Schema: atom; Owner: axelrod
--

--ALTER TABLE ONLY _entries_authors_join
--    ADD CONSTRAINT _entry_author_set_entry_id_fkey FOREIGN KEY (entry_id) REFERENCES entries(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: _feeds_entries_join_entry_id_fkey; Type: FK CONSTRAINT; Schema: atom; Owner: axelrod
--

--ALTER TABLE ONLY _feeds_entries_join
--    ADD CONSTRAINT _feeds_entries_join_entry_id_fkey FOREIGN KEY (entry_id) REFERENCES entries(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: _feeds_entries_join_feed_id_fkey; Type: FK CONSTRAINT; Schema: atom; Owner: axelrod
--

--ALTER TABLE ONLY _feeds_entries_join
--    ADD CONSTRAINT _feeds_entries_join_feed_id_fkey FOREIGN KEY (feed_id) REFERENCES feeds(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: feeds_link_fkey; Type: FK CONSTRAINT; Schema: atom; Owner: axelrod
--

--ALTER TABLE ONLY feeds
--    ADD CONSTRAINT feeds_link_fkey FOREIGN KEY (link) REFERENCES links(id) ON UPDATE CASCADE;


--
-- Name: links_rel_fkey; Type: FK CONSTRAINT; Schema: atom; Owner: axelrod
--

--ALTER TABLE ONLY links
--    ADD CONSTRAINT links_rel_fkey FOREIGN KEY (rel) REFERENCES _link_rel_values(id) ON UPDATE CASCADE;


--
-- PostgreSQL database dump complete
--

