--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- Name: atom; Type: SCHEMA; Schema: -; Owner: axelrod
--

CREATE SCHEMA atom;


ALTER SCHEMA atom OWNER TO axelrod;

--
-- Name: SCHEMA atom; Type: COMMENT; Schema: -; Owner: axelrod
--

COMMENT ON SCHEMA atom IS 'Need to add support for has many relationsihps, rather than just has one.';


SET search_path = atom, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: _entries_authors_join; Type: TABLE; Schema: atom; Owner: axelrod; Tablespace: 
--

CREATE TABLE _entries_authors_join (
    entry_id character varying,
    author_id character varying
);


ALTER TABLE atom._entries_authors_join OWNER TO axelrod;

--
-- Name: _feeds_entries_join; Type: TABLE; Schema: atom; Owner: axelrod; Tablespace: 
--

CREATE TABLE _feeds_entries_join (
    feed_id character varying,
    entry_id character varying
);


ALTER TABLE atom._feeds_entries_join OWNER TO axelrod;

--
-- Name: _link_rel_values; Type: TABLE; Schema: atom; Owner: axelrod; Tablespace: 
--

CREATE TABLE _link_rel_values (
    id character varying NOT NULL
);


ALTER TABLE atom._link_rel_values OWNER TO axelrod;

--
-- Name: TABLE _link_rel_values; Type: COMMENT; Schema: atom; Owner: axelrod
--

COMMENT ON TABLE _link_rel_values IS 'The possible values a link''s rel attribute can take.';


--
-- Name: categories; Type: TABLE; Schema: atom; Owner: axelrod; Tablespace: 
--

CREATE TABLE categories (
    term character varying NOT NULL,
    label character varying
);


ALTER TABLE atom.categories OWNER TO axelrod;

--
-- Name: TABLE categories; Type: COMMENT; Schema: atom; Owner: axelrod
--

COMMENT ON TABLE categories IS 'Scheme can be generated.';


--
-- Name: content; Type: TABLE; Schema: atom; Owner: axelrod; Tablespace: 
--

CREATE TABLE content (
    id integer NOT NULL,
    type character varying,
    src character varying,
    content text,
    summary text
);


ALTER TABLE atom.content OWNER TO axelrod;

--
-- Name: entries; Type: TABLE; Schema: atom; Owner: axelrod; Tablespace: 
--

CREATE TABLE entries (
    id character varying NOT NULL,
    title character varying NOT NULL,
    updated timestamp with time zone DEFAULT now() NOT NULL,
    author character varying,
    content integer,
    link integer,
    category character varying,
    published timestamp with time zone DEFAULT now(),
    rights text
);


ALTER TABLE atom.entries OWNER TO axelrod;

--
-- Name: TABLE entries; Type: COMMENT; Schema: atom; Owner: axelrod
--

COMMENT ON TABLE entries IS 'Source currently not supported.';


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


ALTER TABLE atom.feeds OWNER TO axelrod;

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


ALTER TABLE atom.links OWNER TO axelrod;

--
-- Name: TABLE links; Type: COMMENT; Schema: atom; Owner: axelrod
--

COMMENT ON TABLE links IS 'length is not supported for now.';


--
-- Name: people; Type: TABLE; Schema: atom; Owner: axelrod; Tablespace: 
--

CREATE TABLE people (
    name character varying NOT NULL,
    uri character varying,
    email character varying
);


ALTER TABLE atom.people OWNER TO axelrod;

--
-- Name: content_id_seq; Type: SEQUENCE; Schema: atom; Owner: axelrod
--

CREATE SEQUENCE content_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE atom.content_id_seq OWNER TO axelrod;

--
-- Name: content_id_seq; Type: SEQUENCE OWNED BY; Schema: atom; Owner: axelrod
--

ALTER SEQUENCE content_id_seq OWNED BY content.id;


--
-- Name: content_id_seq; Type: SEQUENCE SET; Schema: atom; Owner: axelrod
--

SELECT pg_catalog.setval('content_id_seq', 1, false);


--
-- Name: links_id_seq; Type: SEQUENCE; Schema: atom; Owner: axelrod
--

CREATE SEQUENCE links_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE atom.links_id_seq OWNER TO axelrod;

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

ALTER TABLE content ALTER COLUMN id SET DEFAULT nextval('content_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: atom; Owner: axelrod
--

ALTER TABLE links ALTER COLUMN id SET DEFAULT nextval('links_id_seq'::regclass);


--
-- Data for Name: _entries_authors_join; Type: TABLE DATA; Schema: atom; Owner: axelrod
--

COPY _entries_authors_join (entry_id, author_id) FROM stdin;
\.


--
-- Data for Name: _feeds_entries_join; Type: TABLE DATA; Schema: atom; Owner: axelrod
--

COPY _feeds_entries_join (feed_id, entry_id) FROM stdin;
\.


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
-- Data for Name: categories; Type: TABLE DATA; Schema: atom; Owner: axelrod
--

COPY categories (term, label) FROM stdin;
\.


--
-- Data for Name: content; Type: TABLE DATA; Schema: atom; Owner: axelrod
--

COPY content (id, type, src, content, summary) FROM stdin;
\.


--
-- Data for Name: entries; Type: TABLE DATA; Schema: atom; Owner: axelrod
--

COPY entries (id, title, updated, author, content, link, category, published, rights) FROM stdin;
\.


--
-- Data for Name: feeds; Type: TABLE DATA; Schema: atom; Owner: axelrod
--

COPY feeds (id, title, icon, logo, rights, subtitle, link) FROM stdin;
\.


--
-- Data for Name: links; Type: TABLE DATA; Schema: atom; Owner: axelrod
--

COPY links (id, href, type, hreflang, title, rel) FROM stdin;
\.


--
-- Data for Name: people; Type: TABLE DATA; Schema: atom; Owner: axelrod
--

COPY people (name, uri, email) FROM stdin;
\.


--
-- Name: _link_rel_values_pkey; Type: CONSTRAINT; Schema: atom; Owner: axelrod; Tablespace: 
--

ALTER TABLE ONLY _link_rel_values
    ADD CONSTRAINT _link_rel_values_pkey PRIMARY KEY (id);


--
-- Name: categories_pkey; Type: CONSTRAINT; Schema: atom; Owner: axelrod; Tablespace: 
--

ALTER TABLE ONLY categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (term);


--
-- Name: content_pkey; Type: CONSTRAINT; Schema: atom; Owner: axelrod; Tablespace: 
--

ALTER TABLE ONLY content
    ADD CONSTRAINT content_pkey PRIMARY KEY (id);


--
-- Name: entries_pkey; Type: CONSTRAINT; Schema: atom; Owner: axelrod; Tablespace: 
--

ALTER TABLE ONLY entries
    ADD CONSTRAINT entries_pkey PRIMARY KEY (id);


--
-- Name: feeds_pkey; Type: CONSTRAINT; Schema: atom; Owner: axelrod; Tablespace: 
--

ALTER TABLE ONLY feeds
    ADD CONSTRAINT feeds_pkey PRIMARY KEY (id);


--
-- Name: links_pkey; Type: CONSTRAINT; Schema: atom; Owner: axelrod; Tablespace: 
--

ALTER TABLE ONLY links
    ADD CONSTRAINT links_pkey PRIMARY KEY (id);


--
-- Name: people_pkey; Type: CONSTRAINT; Schema: atom; Owner: axelrod; Tablespace: 
--

ALTER TABLE ONLY people
    ADD CONSTRAINT people_pkey PRIMARY KEY (name);


--
-- Name: _entry_author_set_author_id_fkey; Type: FK CONSTRAINT; Schema: atom; Owner: axelrod
--

ALTER TABLE ONLY _entries_authors_join
    ADD CONSTRAINT _entry_author_set_author_id_fkey FOREIGN KEY (author_id) REFERENCES people(name) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: _entry_author_set_entry_id_fkey; Type: FK CONSTRAINT; Schema: atom; Owner: axelrod
--

ALTER TABLE ONLY _entries_authors_join
    ADD CONSTRAINT _entry_author_set_entry_id_fkey FOREIGN KEY (entry_id) REFERENCES entries(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: _feeds_entries_join_entry_id_fkey; Type: FK CONSTRAINT; Schema: atom; Owner: axelrod
--

ALTER TABLE ONLY _feeds_entries_join
    ADD CONSTRAINT _feeds_entries_join_entry_id_fkey FOREIGN KEY (entry_id) REFERENCES entries(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: _feeds_entries_join_feed_id_fkey; Type: FK CONSTRAINT; Schema: atom; Owner: axelrod
--

ALTER TABLE ONLY _feeds_entries_join
    ADD CONSTRAINT _feeds_entries_join_feed_id_fkey FOREIGN KEY (feed_id) REFERENCES feeds(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: entries_author_fkey; Type: FK CONSTRAINT; Schema: atom; Owner: axelrod
--

ALTER TABLE ONLY entries
    ADD CONSTRAINT entries_author_fkey FOREIGN KEY (author) REFERENCES people(name) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: entries_category_fkey; Type: FK CONSTRAINT; Schema: atom; Owner: axelrod
--

ALTER TABLE ONLY entries
    ADD CONSTRAINT entries_category_fkey FOREIGN KEY (category) REFERENCES categories(term) ON UPDATE CASCADE;


--
-- Name: entries_content_fkey; Type: FK CONSTRAINT; Schema: atom; Owner: axelrod
--

ALTER TABLE ONLY entries
    ADD CONSTRAINT entries_content_fkey FOREIGN KEY (content) REFERENCES content(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: entries_link_fkey; Type: FK CONSTRAINT; Schema: atom; Owner: axelrod
--

ALTER TABLE ONLY entries
    ADD CONSTRAINT entries_link_fkey FOREIGN KEY (link) REFERENCES links(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: feeds_link_fkey; Type: FK CONSTRAINT; Schema: atom; Owner: axelrod
--

ALTER TABLE ONLY feeds
    ADD CONSTRAINT feeds_link_fkey FOREIGN KEY (link) REFERENCES links(id) ON UPDATE CASCADE;


--
-- Name: links_rel_fkey; Type: FK CONSTRAINT; Schema: atom; Owner: axelrod
--

ALTER TABLE ONLY links
    ADD CONSTRAINT links_rel_fkey FOREIGN KEY (rel) REFERENCES _link_rel_values(id) ON UPDATE CASCADE;


--
-- Name: public; Type: ACL; Schema: -; Owner: pgsql
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM pgsql;
GRANT ALL ON SCHEMA public TO pgsql;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--
