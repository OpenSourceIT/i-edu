--
-- PostgreSQL database dump
--

-- Dumped from database version 9.2.23
-- Dumped by pg_dump version 9.2.23
-- Started on 2018-04-10 11:14:09 CEST

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

--
-- TOC entry 3278 (class 0 OID 16548)
-- Dependencies: 188
-- Data for Name: operatingsystems; Type: TABLE DATA; Schema: public; Owner: foreman
--

COPY operatingsystems (id, major, name, minor, nameindicator, created_at, updated_at, release_name, type, description, password_hash, title) FROM stdin;
100	1	kubuntu1604		\N	2016-11-21 11:48:44.478327	2016-11-21 11:48:44.478327	xenial	Debian	Kubuntu 16.04 Kickstart	SHA256	Kubuntu 16.04 Kickstart
101	16	i-EDU-Ubuntu	4	\N	2017-05-29 13:18:27.639814	2018-01-31 07:35:16.579962	xenial	Debian	i-EDU Ubuntu	SHA256	i-EDU Ubuntu
\.


--
-- TOC entry 3284 (class 0 OID 0)
-- Dependencies: 187
-- Name: operatingsystems_id_seq; Type: SEQUENCE SET; Schema: public; Owner: foreman
--

SELECT pg_catalog.setval('operatingsystems_id_seq', 10, true);


-- Completed on 2018-04-10 11:14:24 CEST

--
-- PostgreSQL database dump complete
--

