--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: admin_users; Type: TABLE; Schema: public; Owner: doriakeung; Tablespace: 
--

CREATE TABLE admin_users (
    admin_id integer NOT NULL,
    jukebox_id character varying(64) NOT NULL
);


ALTER TABLE admin_users OWNER TO doriakeung;

--
-- Name: admin_users_admin_id_seq; Type: SEQUENCE; Schema: public; Owner: doriakeung
--

CREATE SEQUENCE admin_users_admin_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE admin_users_admin_id_seq OWNER TO doriakeung;

--
-- Name: admin_users_admin_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: doriakeung
--

ALTER SEQUENCE admin_users_admin_id_seq OWNED BY admin_users.admin_id;


--
-- Name: guest_users; Type: TABLE; Schema: public; Owner: doriakeung; Tablespace: 
--

CREATE TABLE guest_users (
    guest_id integer NOT NULL,
    jukebox_id character varying(64) NOT NULL
);


ALTER TABLE guest_users OWNER TO doriakeung;

--
-- Name: guest_users_guest_id_seq; Type: SEQUENCE; Schema: public; Owner: doriakeung
--

CREATE SEQUENCE guest_users_guest_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE guest_users_guest_id_seq OWNER TO doriakeung;

--
-- Name: guest_users_guest_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: doriakeung
--

ALTER SEQUENCE guest_users_guest_id_seq OWNED BY guest_users.guest_id;


--
-- Name: jukeboxes; Type: TABLE; Schema: public; Owner: doriakeung; Tablespace: 
--

CREATE TABLE jukeboxes (
    jukebox_id character varying(64) NOT NULL,
    created_at timestamp without time zone,
    last_updated timestamp without time zone
);


ALTER TABLE jukeboxes OWNER TO doriakeung;

--
-- Name: song_user_relationships; Type: TABLE; Schema: public; Owner: doriakeung; Tablespace: 
--

CREATE TABLE song_user_relationships (
    song_user_id integer NOT NULL,
    song_id integer NOT NULL,
    jukebox_id character varying(64) NOT NULL,
    user_id integer,
    "timestamp" timestamp without time zone
);


ALTER TABLE song_user_relationships OWNER TO doriakeung;

--
-- Name: song_user_relationships_song_user_id_seq; Type: SEQUENCE; Schema: public; Owner: doriakeung
--

CREATE SEQUENCE song_user_relationships_song_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE song_user_relationships_song_user_id_seq OWNER TO doriakeung;

--
-- Name: song_user_relationships_song_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: doriakeung
--

ALTER SEQUENCE song_user_relationships_song_user_id_seq OWNED BY song_user_relationships.song_user_id;


--
-- Name: songs; Type: TABLE; Schema: public; Owner: doriakeung; Tablespace: 
--

CREATE TABLE songs (
    song_id integer NOT NULL,
    "spotify_URI" character varying(256) NOT NULL
);


ALTER TABLE songs OWNER TO doriakeung;

--
-- Name: songs_song_id_seq; Type: SEQUENCE; Schema: public; Owner: doriakeung
--

CREATE SEQUENCE songs_song_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE songs_song_id_seq OWNER TO doriakeung;

--
-- Name: songs_song_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: doriakeung
--

ALTER SEQUENCE songs_song_id_seq OWNED BY songs.song_id;


--
-- Name: votes; Type: TABLE; Schema: public; Owner: doriakeung; Tablespace: 
--

CREATE TABLE votes (
    vote_id integer NOT NULL,
    song_id integer NOT NULL,
    guest_id integer NOT NULL,
    vote_value integer NOT NULL
);


ALTER TABLE votes OWNER TO doriakeung;

--
-- Name: votes_vote_id_seq; Type: SEQUENCE; Schema: public; Owner: doriakeung
--

CREATE SEQUENCE votes_vote_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE votes_vote_id_seq OWNER TO doriakeung;

--
-- Name: votes_vote_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: doriakeung
--

ALTER SEQUENCE votes_vote_id_seq OWNED BY votes.vote_id;


--
-- Name: admin_id; Type: DEFAULT; Schema: public; Owner: doriakeung
--

ALTER TABLE ONLY admin_users ALTER COLUMN admin_id SET DEFAULT nextval('admin_users_admin_id_seq'::regclass);


--
-- Name: guest_id; Type: DEFAULT; Schema: public; Owner: doriakeung
--

ALTER TABLE ONLY guest_users ALTER COLUMN guest_id SET DEFAULT nextval('guest_users_guest_id_seq'::regclass);


--
-- Name: song_user_id; Type: DEFAULT; Schema: public; Owner: doriakeung
--

ALTER TABLE ONLY song_user_relationships ALTER COLUMN song_user_id SET DEFAULT nextval('song_user_relationships_song_user_id_seq'::regclass);


--
-- Name: song_id; Type: DEFAULT; Schema: public; Owner: doriakeung
--

ALTER TABLE ONLY songs ALTER COLUMN song_id SET DEFAULT nextval('songs_song_id_seq'::regclass);


--
-- Name: vote_id; Type: DEFAULT; Schema: public; Owner: doriakeung
--

ALTER TABLE ONLY votes ALTER COLUMN vote_id SET DEFAULT nextval('votes_vote_id_seq'::regclass);


--
-- Data for Name: admin_users; Type: TABLE DATA; Schema: public; Owner: doriakeung
--

COPY admin_users (admin_id, jukebox_id) FROM stdin;
\.


--
-- Name: admin_users_admin_id_seq; Type: SEQUENCE SET; Schema: public; Owner: doriakeung
--

SELECT pg_catalog.setval('admin_users_admin_id_seq', 1, false);


--
-- Data for Name: guest_users; Type: TABLE DATA; Schema: public; Owner: doriakeung
--

COPY guest_users (guest_id, jukebox_id) FROM stdin;
\.


--
-- Name: guest_users_guest_id_seq; Type: SEQUENCE SET; Schema: public; Owner: doriakeung
--

SELECT pg_catalog.setval('guest_users_guest_id_seq', 1, false);


--
-- Data for Name: jukeboxes; Type: TABLE DATA; Schema: public; Owner: doriakeung
--

COPY jukeboxes (jukebox_id, created_at, last_updated) FROM stdin;
\.


--
-- Data for Name: song_user_relationships; Type: TABLE DATA; Schema: public; Owner: doriakeung
--

COPY song_user_relationships (song_user_id, song_id, jukebox_id, user_id, "timestamp") FROM stdin;
\.


--
-- Name: song_user_relationships_song_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: doriakeung
--

SELECT pg_catalog.setval('song_user_relationships_song_user_id_seq', 1, false);


--
-- Data for Name: songs; Type: TABLE DATA; Schema: public; Owner: doriakeung
--

COPY songs (song_id, "spotify_URI") FROM stdin;
\.


--
-- Name: songs_song_id_seq; Type: SEQUENCE SET; Schema: public; Owner: doriakeung
--

SELECT pg_catalog.setval('songs_song_id_seq', 1, false);


--
-- Data for Name: votes; Type: TABLE DATA; Schema: public; Owner: doriakeung
--

COPY votes (vote_id, song_id, guest_id, vote_value) FROM stdin;
\.


--
-- Name: votes_vote_id_seq; Type: SEQUENCE SET; Schema: public; Owner: doriakeung
--

SELECT pg_catalog.setval('votes_vote_id_seq', 1, false);


--
-- Name: admin_users_pkey; Type: CONSTRAINT; Schema: public; Owner: doriakeung; Tablespace: 
--

ALTER TABLE ONLY admin_users
    ADD CONSTRAINT admin_users_pkey PRIMARY KEY (admin_id);


--
-- Name: guest_users_pkey; Type: CONSTRAINT; Schema: public; Owner: doriakeung; Tablespace: 
--

ALTER TABLE ONLY guest_users
    ADD CONSTRAINT guest_users_pkey PRIMARY KEY (guest_id);


--
-- Name: jukeboxes_pkey; Type: CONSTRAINT; Schema: public; Owner: doriakeung; Tablespace: 
--

ALTER TABLE ONLY jukeboxes
    ADD CONSTRAINT jukeboxes_pkey PRIMARY KEY (jukebox_id);


--
-- Name: song_user_relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: doriakeung; Tablespace: 
--

ALTER TABLE ONLY song_user_relationships
    ADD CONSTRAINT song_user_relationships_pkey PRIMARY KEY (song_user_id);


--
-- Name: songs_pkey; Type: CONSTRAINT; Schema: public; Owner: doriakeung; Tablespace: 
--

ALTER TABLE ONLY songs
    ADD CONSTRAINT songs_pkey PRIMARY KEY (song_id);


--
-- Name: votes_pkey; Type: CONSTRAINT; Schema: public; Owner: doriakeung; Tablespace: 
--

ALTER TABLE ONLY votes
    ADD CONSTRAINT votes_pkey PRIMARY KEY (vote_id);


--
-- Name: admin_users_jukebox_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: doriakeung
--

ALTER TABLE ONLY admin_users
    ADD CONSTRAINT admin_users_jukebox_id_fkey FOREIGN KEY (jukebox_id) REFERENCES jukeboxes(jukebox_id);


--
-- Name: guest_users_jukebox_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: doriakeung
--

ALTER TABLE ONLY guest_users
    ADD CONSTRAINT guest_users_jukebox_id_fkey FOREIGN KEY (jukebox_id) REFERENCES jukeboxes(jukebox_id);


--
-- Name: song_user_relationships_jukebox_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: doriakeung
--

ALTER TABLE ONLY song_user_relationships
    ADD CONSTRAINT song_user_relationships_jukebox_id_fkey FOREIGN KEY (jukebox_id) REFERENCES jukeboxes(jukebox_id);


--
-- Name: song_user_relationships_song_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: doriakeung
--

ALTER TABLE ONLY song_user_relationships
    ADD CONSTRAINT song_user_relationships_song_id_fkey FOREIGN KEY (song_id) REFERENCES songs(song_id);


--
-- Name: song_user_relationships_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: doriakeung
--

ALTER TABLE ONLY song_user_relationships
    ADD CONSTRAINT song_user_relationships_user_id_fkey FOREIGN KEY (user_id) REFERENCES guest_users(guest_id);


--
-- Name: votes_guest_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: doriakeung
--

ALTER TABLE ONLY votes
    ADD CONSTRAINT votes_guest_id_fkey FOREIGN KEY (guest_id) REFERENCES guest_users(guest_id);


--
-- Name: votes_song_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: doriakeung
--

ALTER TABLE ONLY votes
    ADD CONSTRAINT votes_song_id_fkey FOREIGN KEY (song_id) REFERENCES songs(song_id);


--
-- Name: public; Type: ACL; Schema: -; Owner: doriakeung
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM doriakeung;
GRANT ALL ON SCHEMA public TO doriakeung;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

