--
-- PostgreSQL database dump
--

\restrict UhYSequ3lMeazNdwykqJwOORIVZjb80XiXtxNR5a3uglz9Vxh296o3E0XLgrbAi

-- Dumped from database version 15.15
-- Dumped by pg_dump version 18.1

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

INSERT INTO public.alembic_version (version_num) VALUES ('b6e6ebe3f762');
INSERT INTO public.alembic_version (version_num) VALUES ('6195322f0754');
INSERT INTO public.alembic_version (version_num) VALUES ('4c2950a19dcd');


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.user_roles (id, name, description, created_at, updated_at) VALUES (1, 'admin', 'Administrator Role', '2026-02-20 10:52:52.210006+00', '2026-02-20 10:52:52.210006+00');
INSERT INTO public.user_roles (id, name, description, created_at, updated_at) VALUES (3, 'client', 'Client Role', '2026-03-29 12:01:59.62993+00', '2026-03-29 12:01:59.62993+00');
INSERT INTO public.user_roles (id, name, description, created_at, updated_at) VALUES (4, 'musician', 'Musician Role', '2026-03-29 12:02:12.136474+00', '2026-03-29 12:02:12.136474+00');
INSERT INTO public.user_roles (id, name, description, created_at, updated_at) VALUES (5, 'auxiliar_musician', 'Auxiliar Musician Role', '2026-03-29 12:02:34.52858+00', '2026-03-29 12:02:34.52858+00');


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at) VALUES (2, 'admin', 'admin', NULL, 'admin@example.com', '$2b$12$/AH3rMR0i9AOvjJoYihPHOfFPOrHwT1BW4JF6e0ipaJdHIWt3feJO', '+59176523434', 1, '2026-03-29 12:00:28.157407+00', '2026-03-29 12:00:28.157407+00');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at) VALUES (3, 'juan', 'perez', 'garcia', 'juan.perez@example.com', '$2b$12$knhiu77dZmSRHux13/p2CObd6K.2EqQ7o7eHFSAqzeac/Dfcf/iUK', '+59176534523', 3, '2026-03-29 12:04:33.428574+00', '2026-03-29 12:04:33.428574+00');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at) VALUES (4, 'maria', 'garcia', 'rosales', 'maria.garcia@example.com', '$2b$12$fdoTn1ROgk8TS8t45Q3vUOmvP2t0NpX6gWlMmNKT.Mzr.QZugqpfW', '+59176845678', 3, '2026-03-29 12:05:02.86325+00', '2026-03-29 12:05:02.86325+00');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at) VALUES (5, 'gonzalo', 'reyes', 'garcia', 'gonzalo.reyes@example.com', '$2b$12$b3JzUZ0MNKl4tnEEwAJrx.D1BwAR39ty9DIZobpSCfmjWU9N32ZUS', '+59176543234', 4, '2026-04-17 03:37:28.420693+00', '2026-04-17 03:37:28.420693+00');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at) VALUES (6, 'jose carlos', 'higuera', 'rojas', 'carlos.higuera@example.com', '$2b$12$CaXAGn2QEMp6U1zznfcibeuT5v92VguoaMVA2O.ysjATPvOJfXboG', '+59175698234', 5, '2026-04-17 03:38:17.817745+00', '2026-04-17 03:38:17.817745+00');


--
-- Data for Name: events; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.events (id, name, place, description, start_datetime, end_datetime, is_all_day, status, user_id, price, created_at, updated_at) VALUES (2, 'Cumple de Juana', 'Punata', 'cumple de Juana', '2026-04-05 08:00:00', '2026-04-05 23:00:00', true, 'PENDING', 4, 0.00, '2026-03-29 12:07:53.115871+00', '2026-03-29 12:07:53.115871+00');
INSERT INTO public.events (id, name, place, description, start_datetime, end_datetime, is_all_day, status, user_id, price, created_at, updated_at) VALUES (1, 'Feria en Cliza', 'feria en cliza', 'Feria en cliza', '2026-04-04 18:00:00', '2026-04-04 21:00:00', false, 'PENDING', 4, 2000.00, '2026-03-29 12:06:54.104424+00', '2026-03-29 12:09:26.08528+00');
INSERT INTO public.events (id, name, place, description, start_datetime, end_datetime, is_all_day, status, user_id, price, created_at, updated_at) VALUES (3, 'Graduacion de emily', 'Calle Jordan y Oquendo', 'Graduacion de Emily', '2026-04-24 08:00:00', '2026-04-24 23:00:00', true, 'CONFIRMED', 4, 3000.00, '2026-04-17 03:41:58.710159+00', '2026-04-17 03:43:00.657712+00');


--
-- Data for Name: event_musicians; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (4, 1, 5, 'Unavailable Musician', 1200.00, 'PENDING', '2026-04-17 10:54:46.071988+00', '2026-04-17 10:54:46.071988+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (5, 3, 6, 'Vocalist', 500.00, 'PENDING', '2026-04-17 10:56:06.513415+00', '2026-04-17 10:56:06.513415+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (3, 3, 5, 'Chorist', 500.00, 'PARTIAL', '2026-04-17 10:53:45.542907+00', '2026-04-17 10:59:18.205393+00');


--
-- Data for Name: event_payments; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.event_payments (id, event_id, user_id, amount, payment_type, payment_date, notes, created_at) VALUES (1, 3, 4, 1000.00, 'ADVANCE', '2026-04-17 03:43:00.643085+00', 'First Payment', '2026-04-17 03:43:00.643085+00');


--
-- Data for Name: musician_availability; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (2, 5, '2026-04-23', 'Family vacation', '2026-04-17 10:31:55.149013+00', '2026-04-17 10:31:55.149013+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (3, 5, '2026-04-21', 'Family vacation', '2026-04-17 10:31:55.149013+00', '2026-04-17 10:31:55.149013+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (1, 5, '2026-04-19', 'Rescheduled vacation', '2026-04-17 10:30:36.599677+00', '2026-04-17 10:32:51.461431+00');


--
-- Data for Name: musician_event_payments; Type: TABLE DATA; Schema: public; Owner: paolo
--

INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (1, 3, 5, 'ADVANCE', 100.00, '2026-04-17 06:59:18.149834+00', 'Payment for performance', '2026-04-17 10:59:18.196768+00', '2026-04-17 10:59:18.196768+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (2, 3, 5, 'ADVANCE', 100.00, '2026-04-17 07:00:09.617361+00', 'Payment for performance advance', '2026-04-17 11:00:09.651768+00', '2026-04-17 11:00:09.651768+00');


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
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (11, 'read:event_musician', 'Read event Musician records', '2026-04-17 12:43:39.220382+00', '2026-04-17 12:43:39.220382+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (13, 'delete:event_musician', 'Delete event musician records', '2026-04-17 12:44:03.434807+00', '2026-04-17 12:44:03.434807+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (12, 'write:event_musician', 'Create or modify event musician records', '2026-04-17 12:43:47.550183+00', '2026-04-17 12:44:17.846035+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (14, 'read:musician_availability', 'Read Musician Availability', '2026-04-17 12:45:02.609471+00', '2026-04-17 12:45:02.609471+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (15, 'write:musician_availability', 'Create or modify musician availability', '2026-04-17 12:45:29.848803+00', '2026-04-17 12:45:29.848803+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (16, 'delete:musician_availability', 'Delete musician availability', '2026-04-17 12:45:52.071949+00', '2026-04-17 12:45:52.071949+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (17, 'read:musician_event_payment', 'Read musician Event Payments', '2026-04-17 12:46:18.95787+00', '2026-04-17 12:46:18.95787+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (18, 'write:musician_event_payment', 'Create or modify musician event payments', '2026-04-17 12:46:48.670014+00', '2026-04-17 12:46:48.670014+00');
INSERT INTO public.permissions (id, name, description, created_at, updated_at) VALUES (19, 'delete:musician_event_payment', 'Delete musician event payment', '2026-04-17 12:47:20.678701+00', '2026-04-17 12:47:20.678701+00');


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
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 11);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 13);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 12);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 14);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 15);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 16);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 17);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 18);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (1, 19);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (4, 14);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (4, 17);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (4, 11);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (4, 15);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (4, 16);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (5, 11);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (5, 14);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (5, 15);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (5, 16);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (5, 17);


--
-- Data for Name: user_details; Type: TABLE DATA; Schema: public; Owner: paolo
--



--
-- Name: event_musicians_id_seq; Type: SEQUENCE SET; Schema: public; Owner: paolo
--

SELECT pg_catalog.setval('public.event_musicians_id_seq', 9, true);


--
-- Name: event_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: paolo
--

SELECT pg_catalog.setval('public.event_payments_id_seq', 1, true);


--
-- Name: events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: paolo
--

SELECT pg_catalog.setval('public.events_id_seq', 3, true);


--
-- Name: musician_availability_id_seq; Type: SEQUENCE SET; Schema: public; Owner: paolo
--

SELECT pg_catalog.setval('public.musician_availability_id_seq', 3, true);


--
-- Name: musician_event_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: paolo
--

SELECT pg_catalog.setval('public.musician_event_payments_id_seq', 10, true);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: paolo
--

SELECT pg_catalog.setval('public.permissions_id_seq', 19, true);


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

SELECT pg_catalog.setval('public.users_id_seq', 6, true);


--
-- PostgreSQL database dump complete
--

\unrestrict UhYSequ3lMeazNdwykqJwOORIVZjb80XiXtxNR5a3uglz9Vxh296o3E0XLgrbAi

