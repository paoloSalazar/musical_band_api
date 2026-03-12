--
-- PostgreSQL database dump
--

-- Dumped from database version 15.15
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.alembic_version (version_num) VALUES ('4c2950a19dcd');


--
-- Data for Name: events; Type: TABLE DATA; Schema: public; Owner: paolo
--



--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (1, 'read:user_roles', 'Read User Roles', '2026-02-20 11:00:43.596301+00', '2026-02-20 11:00:43.596301+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (2, 'write:user_roles', 'Permission to write user roles', '2026-02-20 11:07:57.569603+00', '2026-02-20 11:07:57.569603+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (3, 'delete:user_roles', 'Permission to delete user roles', '2026-02-20 11:14:51.232839+00', '2026-02-20 11:14:51.232839+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (4, 'read:users', 'Permission to read user information', '2026-02-20 11:15:58.249231+00', '2026-02-20 11:15:58.249231+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (5, 'write:users', 'Permission to read user information', '2026-02-20 11:16:04.854559+00', '2026-02-20 11:16:04.854559+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (6, 'delete:users', 'Permission to read user information', '2026-02-20 11:16:09.099053+00', '2026-02-20 11:16:09.099053+00');


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.user_roles (id, name, description, created_at, updated_at) VALUES (1, 'admin', 'Administrator Role', '2026-02-20 10:52:52.210006+00', '2026-02-20 10:52:52.210006+00');


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 1);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 2);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 3);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 4);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 5);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 6);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.users (id, name, lastname, second_lastname, email, password, role_id, created_at, updated_at) VALUES (1, 'paolo', 'salazar', 'villarroel', 'paolo.salazar@example.com', '$2b$12$F5FR4YVuLIPm5ahziGma1OpHvkJQR.1tEUn7tFoqd.fg9a1J/fNWq', 1, '2026-02-20 10:54:28.286836+00', '2026-02-20 10:54:28.286836+00');


--
-- Name: events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: paolo
--

SELECT pg_catalog.setval('public.events_id_seq', 1, false);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: paolo
--

SELECT pg_catalog.setval('public.permissions_id_seq', 6, true);


--
-- Name: user_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: paolo
--

SELECT pg_catalog.setval('public.user_roles_id_seq', 1, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: paolo
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- PostgreSQL database dump complete
--

