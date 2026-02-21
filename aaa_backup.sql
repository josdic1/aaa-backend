--
-- PostgreSQL database dump
--

\restrict e28i836f00o6fCQ1giIzKwGebjdJOtlU7AJ89hZWiCP8iz2e9Q5qgpmE3wij2dc

-- Dumped from database version 14.20 (Homebrew)
-- Dumped by pg_dump version 16.12 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: joshdicker
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO joshdicker;

--
-- Name: dietary_restriction_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.dietary_restriction_enum AS ENUM (
    'dairy_free',
    'egg_free',
    'fish_allergy',
    'gluten_free',
    'halal',
    'kosher',
    'nut_allergy',
    'peanut_allergy',
    'sesame_allergy',
    'shellfish_allergy',
    'soy_free',
    'vegan',
    'vegetarian'
);


ALTER TYPE public.dietary_restriction_enum OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: dining_rooms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dining_rooms (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    description character varying(255),
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL
);


ALTER TABLE public.dining_rooms OWNER TO postgres;

--
-- Name: dining_rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dining_rooms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.dining_rooms_id_seq OWNER TO postgres;

--
-- Name: dining_rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dining_rooms_id_seq OWNED BY public.dining_rooms.id;


--
-- Name: members; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.members (
    id integer NOT NULL,
    user_id integer NOT NULL,
    name character varying(120) NOT NULL,
    relation character varying(50),
    dietary_restrictions public.dietary_restriction_enum[],
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.members OWNER TO postgres;

--
-- Name: members_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.members_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.members_id_seq OWNER TO postgres;

--
-- Name: members_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.members_id_seq OWNED BY public.members.id;


--
-- Name: menu_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.menu_items (
    id integer NOT NULL,
    name character varying(140) NOT NULL,
    description character varying(500),
    price_cents integer NOT NULL,
    dietary_restrictions jsonb DEFAULT '[]'::jsonb NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.menu_items OWNER TO postgres;

--
-- Name: menu_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.menu_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.menu_items_id_seq OWNER TO postgres;

--
-- Name: menu_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.menu_items_id_seq OWNED BY public.menu_items.id;


--
-- Name: messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    reservation_id integer NOT NULL,
    body text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    sender_user_id integer NOT NULL
);


ALTER TABLE public.messages OWNER TO postgres;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.messages_id_seq OWNER TO postgres;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_items (
    id integer NOT NULL,
    order_id integer NOT NULL,
    menu_item_id integer NOT NULL,
    quantity integer DEFAULT 1 NOT NULL,
    status character varying(20) DEFAULT 'selected'::character varying NOT NULL,
    name_snapshot character varying(140),
    price_cents_snapshot integer,
    meta json,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.order_items OWNER TO postgres;

--
-- Name: order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_items_id_seq OWNER TO postgres;

--
-- Name: order_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.order_items_id_seq OWNED BY public.order_items.id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    attendee_id integer NOT NULL,
    status character varying(20) DEFAULT 'open'::character varying NOT NULL,
    notes character varying(500),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.orders_id_seq OWNER TO postgres;

--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- Name: reservation_attendees; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reservation_attendees (
    id integer NOT NULL,
    reservation_id integer NOT NULL,
    member_id integer,
    guest_name character varying(120),
    dietary_restrictions public.dietary_restriction_enum[],
    meta json,
    selection_confirmed boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT ck_reservation_attendees_member_or_guest CHECK (((member_id IS NOT NULL) OR ((guest_name IS NOT NULL) AND (length(btrim((guest_name)::text)) > 0))))
);


ALTER TABLE public.reservation_attendees OWNER TO postgres;

--
-- Name: reservation_attendees_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reservation_attendees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reservation_attendees_id_seq OWNER TO postgres;

--
-- Name: reservation_attendees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reservation_attendees_id_seq OWNED BY public.reservation_attendees.id;


--
-- Name: reservations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reservations (
    id integer NOT NULL,
    user_id integer NOT NULL,
    date date NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone,
    status character varying(20) DEFAULT 'draft'::character varying NOT NULL,
    notes character varying(500),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.reservations OWNER TO postgres;

--
-- Name: reservations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reservations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reservations_id_seq OWNER TO postgres;

--
-- Name: reservations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reservations_id_seq OWNED BY public.reservations.id;


--
-- Name: revoked_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.revoked_tokens (
    id integer NOT NULL,
    jti character varying(36) NOT NULL,
    revoked_at timestamp with time zone NOT NULL
);


ALTER TABLE public.revoked_tokens OWNER TO postgres;

--
-- Name: revoked_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.revoked_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.revoked_tokens_id_seq OWNER TO postgres;

--
-- Name: revoked_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.revoked_tokens_id_seq OWNED BY public.revoked_tokens.id;


--
-- Name: tables; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tables (
    id integer NOT NULL,
    dining_room_id integer NOT NULL,
    name character varying(80) NOT NULL,
    seat_count integer NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL
);


ALTER TABLE public.tables OWNER TO postgres;

--
-- Name: tables_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tables_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tables_id_seq OWNER TO postgres;

--
-- Name: tables_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tables_id_seq OWNED BY public.tables.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    password_hash character varying(255) DEFAULT ''::character varying NOT NULL,
    role character varying(20) DEFAULT 'member'::character varying NOT NULL,
    permissions json
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: dining_rooms id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dining_rooms ALTER COLUMN id SET DEFAULT nextval('public.dining_rooms_id_seq'::regclass);


--
-- Name: members id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.members ALTER COLUMN id SET DEFAULT nextval('public.members_id_seq'::regclass);


--
-- Name: menu_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_items ALTER COLUMN id SET DEFAULT nextval('public.menu_items_id_seq'::regclass);


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: order_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items ALTER COLUMN id SET DEFAULT nextval('public.order_items_id_seq'::regclass);


--
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- Name: reservation_attendees id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservation_attendees ALTER COLUMN id SET DEFAULT nextval('public.reservation_attendees_id_seq'::regclass);


--
-- Name: reservations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations ALTER COLUMN id SET DEFAULT nextval('public.reservations_id_seq'::regclass);


--
-- Name: revoked_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revoked_tokens ALTER COLUMN id SET DEFAULT nextval('public.revoked_tokens_id_seq'::regclass);


--
-- Name: tables id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tables ALTER COLUMN id SET DEFAULT nextval('public.tables_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
8978ac8b0387
\.


--
-- Data for Name: dining_rooms; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dining_rooms (id, name, description, is_active, created_at) FROM stdin;
1	Main Dining Room	Primary floor seating	t	2026-02-20 18:23:24.753647-05
2	Bar	Bar seating area	t	2026-02-20 18:23:24.753647-05
3	Patio	Outdoor seating	t	2026-02-20 18:23:24.753647-05
4	Private Room	Private events and parties	t	2026-02-20 18:23:24.753647-05
\.


--
-- Data for Name: members; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.members (id, user_id, name, relation, dietary_restrictions, created_at, updated_at) FROM stdin;
3	3	Fordlian	Spouse	{vegan}	2026-02-20 19:50:43.607074-05	2026-02-20 19:50:43.607079-05
4	3	Reese	Child	{}	2026-02-20 20:30:03.456928-05	2026-02-20 20:30:03.456932-05
5	3	Reese	Child	{}	2026-02-20 20:37:58.54874-05	2026-02-20 20:37:58.548743-05
\.


--
-- Data for Name: menu_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.menu_items (id, name, description, price_cents, dietary_restrictions, is_active, created_at, updated_at) FROM stdin;
1	House Salad	Mixed greens, seasonal vegetables, house vinaigrette.	900	["vegetarian", "gluten_free_option"]	t	2026-02-20 16:10:47.789204-05	2026-02-20 16:10:47.789204-05
2	Tomato Soup	Roasted tomato soup, basil, olive oil.	800	["vegetarian", "gluten_free"]	t	2026-02-20 16:10:47.789204-05	2026-02-20 16:10:47.789204-05
3	Grilled Chicken Plate	Herb grilled chicken, rice, seasonal vegetables.	1800	["gluten_free"]	t	2026-02-20 16:10:47.789204-05	2026-02-20 16:10:47.789204-05
4	Vegan Bowl	Quinoa, roasted vegetables, chickpeas, tahini sauce.	1700	["vegan", "gluten_free"]	t	2026-02-20 16:10:47.789204-05	2026-02-20 16:10:47.789204-05
5	Cheeseburger	Beef patty, cheddar, lettuce, tomato, house sauce.	1600	["contains_dairy", "gluten"]	t	2026-02-20 16:10:47.789204-05	2026-02-20 16:10:47.789204-05
6	Kids Pasta	Butter noodles with parmesan (can omit parmesan).	1100	["vegetarian", "contains_dairy", "gluten"]	t	2026-02-20 16:10:47.789204-05	2026-02-20 16:10:47.789204-05
7	Test Item	tmp	1234	["gluten_free"]	f	2026-02-20 17:10:53.679041-05	2026-02-20 17:11:13.801493-05
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.messages (id, reservation_id, body, created_at, sender_user_id) FROM stdin;
1	2	This message ssays gtf home	2026-02-20 17:42:41.351132-05	3
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_items (id, order_id, menu_item_id, quantity, status, name_snapshot, price_cents_snapshot, meta, created_at, updated_at) FROM stdin;
1	1	1	2	selected	House Salad	900	null	2026-02-20 22:24:24.083546-05	2026-02-20 22:24:24.083547-05
2	3	1	1	selected	House Salad	900	null	2026-02-20 22:57:34.643398-05	2026-02-20 22:57:34.643405-05
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.orders (id, attendee_id, status, notes, created_at, updated_at) FROM stdin;
1	4	open	\N	2026-02-20 22:24:04.331897-05	2026-02-20 22:24:04.3319-05
2	5	open	\N	2026-02-20 22:53:13.935889-05	2026-02-20 22:53:13.935892-05
3	6	open	\N	2026-02-20 22:56:54.800067-05	2026-02-20 22:56:54.800072-05
\.


--
-- Data for Name: reservation_attendees; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reservation_attendees (id, reservation_id, member_id, guest_name, dietary_restrictions, meta, selection_confirmed, created_at, updated_at) FROM stdin;
4	2	\N	John Doe dungeouys	{dairy_free}	{}	t	2026-02-20 20:11:38.431052-05	2026-02-20 20:17:52.8434-05
5	2	3	\N	{vegan}	{}	f	2026-02-20 20:32:05.466566-05	2026-02-20 20:32:05.46657-05
6	2	\N	Random Guest	{dairy_free}	{}	t	2026-02-20 20:32:10.78884-05	2026-02-20 20:32:10.788841-05
7	4	\N	John Doe	{dairy_free}	{}	t	2026-02-20 20:39:04.19854-05	2026-02-20 20:39:04.198543-05
\.


--
-- Data for Name: reservations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reservations (id, user_id, date, start_time, end_time, status, notes, created_at, updated_at) FROM stdin;
2	3	2026-02-20	20:09:06.42	20:09:06.42	confirmed	Dinner Sucks	2026-02-20 20:09:25.328441-05	2026-02-20 20:09:25.328446-05
3	3	2026-02-22	18:00:00	20:00:00	draft	Random reservation	2026-02-20 15:31:59.319219-05	2026-02-20 15:31:59.319222-05
4	3	2026-02-22	18:00:00	20:00:00	draft	Random reservation	2026-02-20 15:38:05.120622-05	2026-02-20 15:38:05.120623-05
\.


--
-- Data for Name: revoked_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.revoked_tokens (id, jti, revoked_at) FROM stdin;
1	b1680fca-b592-4b1a-a540-e20c17584adf	2026-02-20 09:59:43.91061-05
\.


--
-- Data for Name: tables; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tables (id, dining_room_id, name, seat_count, is_active, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, created_at, password_hash, role, permissions) FROM stdin;
3	josh@josh.com	2026-02-20 11:07:16.01412-05	$2b$12$M1yc1E.FlVv4J3IA3PdANenKLu18GM5o7fNEv0DtArHsqkVc0iQAC	admin	\N
4	gag@ga.com	2026-02-20 11:15:20.454335-05	$2b$12$R9R9TzdpFvXF2rFF.2vS8.HFiGPesasB/3KPdYaWip6VlAh.UwwP6	member	\N
\.


--
-- Name: dining_rooms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dining_rooms_id_seq', 4, true);


--
-- Name: members_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.members_id_seq', 5, true);


--
-- Name: menu_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.menu_items_id_seq', 7, true);


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.messages_id_seq', 1, true);


--
-- Name: order_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.order_items_id_seq', 2, true);


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.orders_id_seq', 3, true);


--
-- Name: reservation_attendees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reservation_attendees_id_seq', 7, true);


--
-- Name: reservations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reservations_id_seq', 4, true);


--
-- Name: revoked_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.revoked_tokens_id_seq', 1, true);


--
-- Name: tables_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tables_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 4, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: dining_rooms dining_rooms_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dining_rooms
    ADD CONSTRAINT dining_rooms_name_key UNIQUE (name);


--
-- Name: dining_rooms dining_rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dining_rooms
    ADD CONSTRAINT dining_rooms_pkey PRIMARY KEY (id);


--
-- Name: members members_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_pkey PRIMARY KEY (id);


--
-- Name: menu_items menu_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_items
    ADD CONSTRAINT menu_items_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: reservation_attendees reservation_attendees_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservation_attendees
    ADD CONSTRAINT reservation_attendees_pkey PRIMARY KEY (id);


--
-- Name: reservations reservations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations
    ADD CONSTRAINT reservations_pkey PRIMARY KEY (id);


--
-- Name: revoked_tokens revoked_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revoked_tokens
    ADD CONSTRAINT revoked_tokens_pkey PRIMARY KEY (id);


--
-- Name: tables tables_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tables
    ADD CONSTRAINT tables_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_members_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_members_user_id ON public.members USING btree (user_id);


--
-- Name: ix_menu_items_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_menu_items_is_active ON public.menu_items USING btree (is_active);


--
-- Name: ix_menu_items_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_menu_items_name ON public.menu_items USING btree (name);


--
-- Name: ix_messages_reservation_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_messages_reservation_id ON public.messages USING btree (reservation_id);


--
-- Name: ix_messages_sender_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_messages_sender_user_id ON public.messages USING btree (sender_user_id);


--
-- Name: ix_order_items_menu_item_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_order_items_menu_item_id ON public.order_items USING btree (menu_item_id);


--
-- Name: ix_order_items_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_order_items_order_id ON public.order_items USING btree (order_id);


--
-- Name: ix_order_items_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_order_items_status ON public.order_items USING btree (status);


--
-- Name: ix_orders_attendee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_orders_attendee_id ON public.orders USING btree (attendee_id);


--
-- Name: ix_orders_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_orders_status ON public.orders USING btree (status);


--
-- Name: ix_reservation_attendees_member_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservation_attendees_member_id ON public.reservation_attendees USING btree (member_id);


--
-- Name: ix_reservation_attendees_reservation_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservation_attendees_reservation_id ON public.reservation_attendees USING btree (reservation_id);


--
-- Name: ix_reservations_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservations_date ON public.reservations USING btree (date);


--
-- Name: ix_reservations_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservations_status ON public.reservations USING btree (status);


--
-- Name: ix_reservations_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservations_user_id ON public.reservations USING btree (user_id);


--
-- Name: ix_revoked_tokens_jti; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_revoked_tokens_jti ON public.revoked_tokens USING btree (jti);


--
-- Name: ix_tables_dining_room_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tables_dining_room_id ON public.tables USING btree (dining_room_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_role; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_role ON public.users USING btree (role);


--
-- Name: members members_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: messages messages_reservation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_reservation_id_fkey FOREIGN KEY (reservation_id) REFERENCES public.reservations(id) ON DELETE CASCADE;


--
-- Name: messages messages_sender_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_sender_user_id_fkey FOREIGN KEY (sender_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: order_items order_items_menu_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_menu_item_id_fkey FOREIGN KEY (menu_item_id) REFERENCES public.menu_items(id) ON DELETE RESTRICT;


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: orders orders_attendee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_attendee_id_fkey FOREIGN KEY (attendee_id) REFERENCES public.reservation_attendees(id) ON DELETE CASCADE;


--
-- Name: reservation_attendees reservation_attendees_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservation_attendees
    ADD CONSTRAINT reservation_attendees_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(id) ON DELETE SET NULL;


--
-- Name: reservation_attendees reservation_attendees_reservation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservation_attendees
    ADD CONSTRAINT reservation_attendees_reservation_id_fkey FOREIGN KEY (reservation_id) REFERENCES public.reservations(id) ON DELETE CASCADE;


--
-- Name: reservations reservations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations
    ADD CONSTRAINT reservations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: tables tables_dining_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tables
    ADD CONSTRAINT tables_dining_room_id_fkey FOREIGN KEY (dining_room_id) REFERENCES public.dining_rooms(id) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: joshdicker
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

\unrestrict e28i836f00o6fCQ1giIzKwGebjdJOtlU7AJ89hZWiCP8iz2e9Q5qgpmE3wij2dc

