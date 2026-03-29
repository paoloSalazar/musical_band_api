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

INSERT INTO public.alembic_version (version_num) VALUES ('6195322f0754');
INSERT INTO public.alembic_version (version_num) VALUES ('4c2950a19dcd');


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.user_roles (id, name, description, created_at, updated_at) VALUES (1, 'admin', 'Administrator Role', '2026-02-20 10:52:52.210006+00', '2026-02-20 10:52:52.210006+00');
INSERT INTO public.user_roles (id, name, description, created_at, updated_at) VALUES (3, 'client', 'Client Role', '2026-03-29 12:01:59.62993+00', '2026-03-29 12:01:59.62993+00');
INSERT INTO public.user_roles (id, name, description, created_at, updated_at) VALUES (4, 'musician', 'Musician Role', '2026-03-29 12:02:12.136474+00', '2026-03-29 12:02:12.136474+00');
INSERT INTO public.user_roles (id, name, description, created_at, updated_at) VALUES (5, 'auxiliar musician', 'Auxiliar Musician Role', '2026-03-29 12:02:34.52858+00', '2026-03-29 12:02:34.52858+00');


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at) VALUES (2, 'admin', 'admin', NULL, 'admin@example.com', '$2b$12$/AH3rMR0i9AOvjJoYihPHOfFPOrHwT1BW4JF6e0ipaJdHIWt3feJO', '+59176523434', 1, '2026-03-29 12:00:28.157407+00', '2026-03-29 12:00:28.157407+00');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at) VALUES (3, 'juan', 'perez', 'garcia', 'juan.perez@example.com', '$2b$12$knhiu77dZmSRHux13/p2CObd6K.2EqQ7o7eHFSAqzeac/Dfcf/iUK', '+59176534523', 3, '2026-03-29 12:04:33.428574+00', '2026-03-29 12:04:33.428574+00');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at) VALUES (4, 'maria', 'garcia', 'rosales', 'maria.garcia@example.com', '$2b$12$fdoTn1ROgk8TS8t45Q3vUOmvP2t0NpX6gWlMmNKT.Mzr.QZugqpfW', '+59176845678', 3, '2026-03-29 12:05:02.86325+00', '2026-03-29 12:05:02.86325+00');


--
-- Data for Name: events; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.events (id, name, place, description, start_datetime, end_datetime, is_all_day, status, user_id, price, created_at, updated_at) VALUES (2, 'Cumple de Juana', 'Punata', 'cumple de Juana', '2026-04-05 08:00:00', '2026-04-05 23:00:00', true, 'PENDING', 4, 0.00, '2026-03-29 12:07:53.115871+00', '2026-03-29 12:07:53.115871+00');
INSERT INTO public.events (id, name, place, description, start_datetime, end_datetime, is_all_day, status, user_id, price, created_at, updated_at) VALUES (1, 'Feria en Cliza', 'feria en cliza', 'Feria en cliza', '2026-04-04 18:00:00', '2026-04-04 21:00:00', false, 'PENDING', 4, 2000.00, '2026-03-29 12:06:54.104424+00', '2026-03-29 12:09:26.08528+00');


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (1, 'read:user_roles', 'Read User Roles', '2026-02-20 11:00:43.596301+00', '2026-02-20 11:00:43.596301+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (2, 'write:user_roles', 'Permission to write user roles', '2026-02-20 11:07:57.569603+00', '2026-02-20 11:07:57.569603+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (3, 'delete:user_roles', 'Permission to delete user roles', '2026-02-20 11:14:51.232839+00', '2026-02-20 11:14:51.232839+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (4, 'read:users', 'Permission to read user information', '2026-02-20 11:15:58.249231+00', '2026-02-20 11:15:58.249231+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (5, 'write:users', 'Permission to read user information', '2026-02-20 11:16:04.854559+00', '2026-02-20 11:16:04.854559+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (6, 'delete:users', 'Permission to read user information', '2026-02-20 11:16:09.099053+00', '2026-02-20 11:16:09.099053+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (7, 'read:events', 'Permission to read events', '2026-03-29 12:02:52.631713+00', '2026-03-29 12:02:52.631713+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (8, 'write:events', 'Permission to write Events', '2026-03-29 12:03:09.566685+00', '2026-03-29 12:03:09.566685+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (9, 'delete:events', 'Permission to delete events', '2026-03-29 12:03:24.02362+00', '2026-03-29 12:03:24.02362+00');


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 1);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 2);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 3);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 4);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 5);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 6);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (3, 7);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (3, 8);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 7);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 8);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 9);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (4, 7);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (5, 7);


--
-- Data for Name: user_details; Type: TABLE DATA; Schema: public; Owner: paolo
--



--
-- Name: events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: paolo
--

SELECT pg_catalog.setval('public.events_id_seq', 2, true);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: paolo
--

SELECT pg_catalog.setval('public.permissions_id_seq', 9, true);


--
-- Name: user_details_id_seq; Type: SEQUENCE SET; Schema: public; Owner: paolo
--

SELECT pg_catalog.setval('public.user_details_id_seq', 1, false);


--
-- Name: user_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: paolo
--

SELECT pg_catalog.setval('public.user_roles_id_seq', 5, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: paolo
--

SELECT pg_catalog.setval('public.users_id_seq', 4, true);


--
-- PostgreSQL database dump complete
--

