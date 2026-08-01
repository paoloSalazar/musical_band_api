--
-- PostgreSQL database dump
--

\restrict dSIh4qZsz3BiD80KGMWtgVtoSN6rdWsTcPgYKkk33mJv1PxYLKW7UQRsh1fwJtM

-- Dumped from database version 15.15
-- Dumped by pg_dump version 18.3

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
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: musician
--

INSERT INTO public.alembic_version (version_num) VALUES ('d5bc9ddda396');
INSERT INTO public.alembic_version (version_num) VALUES ('b6e6ebe3f762');
INSERT INTO public.alembic_version (version_num) VALUES ('6195322f0754');
INSERT INTO public.alembic_version (version_num) VALUES ('4c2950a19dcd');


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: musician
--

INSERT INTO public.user_roles (id, name, description, created_at, updated_at) VALUES (1, 'admin', 'Administrator Role', '2026-02-20 10:52:52.210006+00', '2026-02-20 10:52:52.210006+00');
INSERT INTO public.user_roles (id, name, description, created_at, updated_at) VALUES (3, 'client', 'Client Role', '2026-03-29 12:01:59.62993+00', '2026-03-29 12:01:59.62993+00');
INSERT INTO public.user_roles (id, name, description, created_at, updated_at) VALUES (4, 'musician', 'Musician Role', '2026-03-29 12:02:12.136474+00', '2026-03-29 12:02:12.136474+00');
INSERT INTO public.user_roles (id, name, description, created_at, updated_at) VALUES (5, 'auxiliar_musician', 'Auxiliar Musician Role', '2026-03-29 12:02:34.52858+00', '2026-03-29 12:02:34.52858+00');
INSERT INTO public.user_roles (id, name, description, created_at, updated_at) VALUES (6, 'helper', 'ayudante', '2026-06-29 09:50:32.775265+00', '2026-06-29 09:50:32.775265+00');


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: musician
--

INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (2, 'admin', 'admin', NULL, 'admin@example.com', '$2b$12$/AH3rMR0i9AOvjJoYihPHOfFPOrHwT1BW4JF6e0ipaJdHIWt3feJO', '+59176523434', 1, '2026-03-29 12:00:28.157407+00', '2026-03-29 12:00:28.157407+00', NULL);
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (7, 'Paolo', 'Salazar', 'Villarroel', 'paolo.salazar@example.com', '$2b$12$7HHGqbzuT6gKjtDQS1npl.TW1NaLPAa46S0SbExj7MT9/H7X0KQ8m', '+59175474592', 4, '2026-07-21 04:50:24.54687+00', '2026-07-21 04:50:24.54687+00', '0000000');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (8, 'Jose Luis', 'Cosio', 'Lopez', 'joseluis.cosio@example.com', '$2b$12$ErP1mJ8zTncpPwUsoe7ev.x8NnvSSr6TpPlsFcwnbzWfwbtw6yZk2', '+59179723902', 4, '2026-07-21 04:52:09.716797+00', '2026-07-21 04:52:09.716797+00', '000000');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (9, 'edgar', 'cosio', 'lopez', 'edgar.cosio@example.com', '$2b$12$gbgUf2DwFkvmgfggSHF3aOwsg0.Ibmh6f2oIUw.WQnXBWDDO/MXvu', '+59165701228', 4, '2026-07-21 04:53:34.062454+00', '2026-07-21 04:53:34.062454+00', '0000000');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (10, 'Jorge', 'Mamani', 'Yavi', 'jorge.mamani@example.com', '$2b$12$pQBYXBpOzD44OoQnetjXR.1Y.BQwgAP2X7sMq.orGZQfuPkr9ouC.', '+59176438132', 4, '2026-07-21 04:54:46.097273+00', '2026-07-21 04:54:46.097273+00', '0000000');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (11, 'Sandino', 'Cordova', 'Alba', 'sandino.cordova@example.com', '$2b$12$W8VwJjyIU6Ih3U3tXAb0qOmlNoIm21sVGjWZTAy7uLUEBKqcf0bFm', '+59163981424', 4, '2026-07-21 04:56:03.246146+00', '2026-07-21 04:56:03.246146+00', '000000');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (12, 'Omar', 'Saavedra', NULL, 'omar.saavedra@example.com', '$2b$12$Qre6h9mcmPXq6cRK.vdZb.Qux.fkI5FeWXm/DKUaimbufx6h8xOEa', '+59171776690', 5, '2026-07-21 04:57:38.986118+00', '2026-07-21 04:57:38.986118+00', '000000');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (13, 'jorge luis', 'cardozo', 'ancieta', 'jorgeluis.cardozo@example.com', '$2b$12$umAvupTaSn1HRfsnPC.GF.qTjHjl5/P2aWjlLHkakMr/iUBMviNfa', '+59167434686', 5, '2026-07-21 05:00:05.917869+00', '2026-07-21 05:00:05.917869+00', '000000');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (14, 'Erika', 'Hurtado', 'Patino', 'erika.hurtado@example.com', '$2b$12$UmYTXOyJ514Ce0SXf.607O67PAElmxehH7Tcl3UiDNFesgPSmYCD2', '+59169544497', 3, '2026-07-21 05:02:01.281638+00', '2026-07-21 05:02:01.281638+00', '0000000');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (16, 'Edgar', 'Zurita', NULL, 'edgar.zurita@example.com', '$2b$12$KpU2XycPNMM5fcwKuDrtO.GhERrG0prBMdEJ2kyYFNUJobBznl3Z2', '+59177975573', 3, '2026-07-21 05:37:35.689966+00', '2026-07-21 05:37:35.689966+00', '000000');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (17, 'pozo', 'kjochi', NULL, 'pozo.kjochi@example.com', '$2b$12$SagKIXBOp.mX.eP46OcI8eMoekWHHomarOBLeYZZQfyhO4xGnOCiC', '+59169461916', 3, '2026-07-21 05:48:23.733421+00', '2026-07-21 05:48:23.733421+00', '0000000');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (18, 'Jimmy', 'Ugarte', 'Rea', 'jimmy.ugarte@example.com', '$2b$12$ZWuRlHC1Ng/MmzLSWIm5puU..cn48YdKKtKOINm3MHOYwoUvgMFCy', '+59170764252', 3, '2026-07-23 13:05:54.276423+00', '2026-07-23 13:05:54.276423+00', '0000000');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (19, 'Jhimy', 'Franco', NULL, 'jhimy.franco@example.com', '$2b$12$R6IlSPKtavxfLZ.VeNLbJ.fai7Iit9/sKGDTOzMs0wucRPd1Yxf2e', '+59168482741', 5, '2026-07-30 10:54:10.202509+00', '2026-07-30 10:54:10.202509+00', '0000000');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (20, 'Elvis', 'Rojas', 'Jimenez', 'elvis.rojas@example.com', '$2b$12$q2WIeIIrgN1d.Soe4.hgCeagq7wLFYmkROl1kB5k/Hd8xLIR8NVVy', '+59170384453', 5, '2026-07-30 11:13:19.597702+00', '2026-07-30 11:13:19.597702+00', '0000000');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (21, 'Nelvy', 'Veizaga', 'Soliz', 'nelvy.veizaga@example.com', '$2b$12$9DuneHgTtzbJBgROVP6wv.vPo.d7MZB9h8RucEpNmTkYxAlYsNdCK', '+59167587147', 3, '2026-07-31 17:32:11.643652+00', '2026-07-31 17:32:11.643652+00', '000000');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (22, 'Jaime', 'Cespedes', 'Huanca', 'jaime.cespedes@example.com', '$2b$12$r17BdYHeiRyddfif8at6MOFBuLadYhRMZKH5FRkwEDYxR1ncUy8LG', '+59176418442', 5, '2026-07-31 17:41:54.486371+00', '2026-07-31 17:41:54.486371+00', '00000');
INSERT INTO public.users (id, name, lastname, second_lastname, email, password, phone_number, role_id, created_at, updated_at, ci) VALUES (15, 'Mauricio', 'Rodriguez', 'Imaca', 'mauricio.ri@example.com', '$2b$12$lRJMxtZDpAZ5curjHVMwxOvVHLzUFaDFzuLYZysd0gM.tqHBlpOga', '+59165396182', 3, '2026-07-21 05:22:18.576746+00', '2026-08-01 16:58:56.326254+00', '0000000');


--
-- Data for Name: events; Type: TABLE DATA; Schema: public; Owner: musician
--

INSERT INTO public.events (id, name, place, description, start_datetime, end_datetime, is_all_day, status, user_id, price, created_at, updated_at) VALUES (6, 'Cabo de año en Perez Rancho', 'Perez Rancho, Cliza', 'Cabo de año en perez rancho', '2026-08-19 08:00:00', '2026-08-19 23:00:00', true, 'CONFIRMED', 16, 3500.00, '2026-07-21 05:40:00.280833+00', '2026-07-21 05:40:34.097046+00');
INSERT INTO public.events (id, name, place, description, start_datetime, end_datetime, is_all_day, status, user_id, price, created_at, updated_at) VALUES (8, 'Cumple Cliza', 'Cliza, Lado Colegio JEMA', 'Cumpleanos en cliza lado colegio JEMA', '2026-08-17 08:00:00', '2026-08-17 23:00:00', true, 'CONFIRMED', 18, 3500.00, '2026-07-23 13:08:01.374485+00', '2026-07-23 13:08:52.840826+00');
INSERT INTO public.events (id, name, place, description, start_datetime, end_datetime, is_all_day, status, user_id, price, created_at, updated_at) VALUES (7, 'Bendicion de Pozo', 'Kjochi, Cliza', 'Bendicion de Pozo en Kjochi', '2026-07-26 08:00:00', '2026-07-26 23:00:00', true, 'COMPLETED', 17, 3200.00, '2026-07-21 05:55:03.708389+00', '2026-07-21 05:55:44.8736+00');
INSERT INTO public.events (id, name, place, description, start_datetime, end_datetime, is_all_day, status, user_id, price, created_at, updated_at) VALUES (9, 'Cumple Cliza Cordillera', 'Cliza, Agencia Cordillear', 'Cumple en cliza agencia cordillera', '2026-07-31 08:00:00', '2026-07-31 23:00:00', true, 'CONFIRMED', 21, 3500.00, '2026-07-31 17:36:04.301493+00', '2026-07-31 17:36:04.301493+00');
INSERT INTO public.events (id, name, place, description, start_datetime, end_datetime, is_all_day, status, user_id, price, created_at, updated_at) VALUES (5, 'Cumpleanos en Punata', 'Punata Centro', 'Cumple en Punata', '2026-07-30 08:00:00', '2026-07-30 23:00:00', true, 'CONFIRMED', 15, 3500.00, '2026-07-21 05:23:39.773069+00', '2026-07-21 05:24:11.335801+00');
INSERT INTO public.events (id, name, place, description, start_datetime, end_datetime, is_all_day, status, user_id, price, created_at, updated_at) VALUES (10, 'Cumple Punata', 'Punata, Centro', 'Cumpleanos en Punata', '2026-12-16 08:00:00', '2026-12-16 23:00:00', true, 'CONFIRMED', 15, 3500.00, '2026-08-01 16:40:44.123457+00', '2026-08-01 16:41:21.617134+00');
INSERT INTO public.events (id, name, place, description, start_datetime, end_datetime, is_all_day, status, user_id, price, created_at, updated_at) VALUES (4, 'Cumpleanos En villa Surumi', 'Villa Surumi, Cliza', 'Cumpleanos de don Celso Hurtado', '2026-07-28 08:00:00', '2026-07-28 23:00:00', true, 'CONFIRMED', 14, 2800.00, '2026-07-21 05:04:12.40187+00', '2026-07-21 05:05:39.136496+00');


--
-- Data for Name: event_musicians; Type: TABLE DATA; Schema: public; Owner: musician
--

INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (14, 4, 12, 'Guitarrista', 450.00, 'PENDING', '2026-07-21 05:07:55.744539+00', '2026-07-21 05:07:55.744539+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (20, 6, 7, 'Bajista', 400.00, 'PENDING', '2026-07-21 05:43:43.018588+00', '2026-07-21 05:43:43.018588+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (21, 6, 8, 'Tecladista', 450.00, 'PENDING', '2026-07-21 05:43:55.8917+00', '2026-07-21 05:43:55.8917+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (22, 6, 9, 'Baterista', 450.00, 'PENDING', '2026-07-21 05:44:28.942428+00', '2026-07-21 05:44:28.942428+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (23, 6, 10, 'Vocalista', 450.00, 'PENDING', '2026-07-21 05:44:56.643354+00', '2026-07-21 05:44:56.643354+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (24, 6, 12, 'Guitarrista', 450.00, 'PENDING', '2026-07-21 05:45:12.088047+00', '2026-07-21 05:45:12.088047+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (25, 7, 7, 'Bajista', 400.00, 'COMPLETED', '2026-07-23 12:59:14.828463+00', '2026-07-30 10:50:42.141938+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (27, 7, 10, 'Vocalista', 450.00, 'COMPLETED', '2026-07-23 12:59:58.802766+00', '2026-07-30 10:55:03.39422+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (28, 7, 12, 'Guitarrista', 450.00, 'COMPLETED', '2026-07-23 13:00:16.589104+00', '2026-07-30 10:55:32.871171+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (29, 7, 13, 'Tecladista', 450.00, 'COMPLETED', '2026-07-23 13:00:36.079997+00', '2026-07-30 10:55:58.390567+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (30, 7, 19, 'Baterista', 450.00, 'COMPLETED', '2026-07-30 10:54:38.657599+00', '2026-07-30 10:56:35.631264+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (12, 4, 9, 'Baterista', 400.00, 'COMPLETED', '2026-07-21 05:07:16.193874+00', '2026-07-30 11:01:37.737881+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (10, 4, 7, 'Bajista', 400.00, 'COMPLETED', '2026-07-21 05:06:22.881253+00', '2026-07-30 11:02:10.830613+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (13, 4, 10, 'Vocalista', 450.00, 'COMPLETED', '2026-07-21 05:07:28.250049+00', '2026-07-30 11:02:32.708033+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (31, 5, 20, 'Guitarrista', 450.00, 'PENDING', '2026-07-30 11:14:38.872246+00', '2026-07-30 11:14:38.872246+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (34, 9, 10, 'Vocalista', 480.00, 'PENDING', '2026-07-31 17:43:08.874019+00', '2026-07-31 17:43:08.874019+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (35, 9, 22, 'Guitarrista', 450.00, 'PENDING', '2026-07-31 17:43:26.11388+00', '2026-07-31 17:43:26.11388+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (32, 9, 7, 'Bajista', 400.00, 'COMPLETED', '2026-07-31 17:42:34.869912+00', '2026-08-01 16:36:46.988828+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (36, 9, 8, 'Tecladista', 450.00, 'COMPLETED', '2026-07-31 17:43:41.096173+00', '2026-08-01 16:37:04.431487+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (33, 9, 9, 'Baterista', 450.00, 'COMPLETED', '2026-07-31 17:42:50.56045+00', '2026-08-01 16:37:26.62091+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (15, 5, 7, 'Bajista', 400.00, 'COMPLETED', '2026-07-21 05:32:23.283338+00', '2026-08-01 16:46:22.016086+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (17, 5, 8, 'Tecladista', 450.00, 'COMPLETED', '2026-07-21 05:33:51.249527+00', '2026-08-01 16:46:49.998384+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (19, 5, 10, 'Vocalista', 480.00, 'PENDING', '2026-07-21 05:34:18.094643+00', '2026-08-01 16:47:13.754587+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (16, 5, 9, 'Baterista', 450.00, 'COMPLETED', '2026-07-21 05:33:33.27119+00', '2026-08-01 16:48:09.114925+00');
INSERT INTO public.event_musicians (id, event_id, musician_id, role, salary, payment_status, created_at, updated_at) VALUES (11, 4, 8, 'Tecladista', 400.00, 'COMPLETED', '2026-07-21 05:07:00.817334+00', '2026-08-01 16:52:01.801285+00');


--
-- Data for Name: event_payments; Type: TABLE DATA; Schema: public; Owner: musician
--

INSERT INTO public.event_payments (id, event_id, user_id, amount, payment_type, payment_date, notes, created_at) VALUES (2, 4, 14, 1000.00, 'ADVANCE', '2026-07-21 05:05:39.125542+00', 'Adelanto el 17 de Julio', '2026-07-21 05:05:39.125542+00');
INSERT INTO public.event_payments (id, event_id, user_id, amount, payment_type, payment_date, notes, created_at) VALUES (3, 5, 15, 1000.00, 'ADVANCE', '2026-07-21 05:28:42.146701+00', 'Adelanto', '2026-07-21 05:28:42.146701+00');
INSERT INTO public.event_payments (id, event_id, user_id, amount, payment_type, payment_date, notes, created_at) VALUES (4, 6, 16, 1000.00, 'ADVANCE', '2026-07-21 05:41:59.399455+00', 'Adelanto', '2026-07-21 05:41:59.399455+00');
INSERT INTO public.event_payments (id, event_id, user_id, amount, payment_type, payment_date, notes, created_at) VALUES (5, 7, 17, 400.00, 'ADVANCE', '2026-07-21 05:57:51.019686+00', NULL, '2026-07-21 05:57:51.019686+00');
INSERT INTO public.event_payments (id, event_id, user_id, amount, payment_type, payment_date, notes, created_at) VALUES (6, 8, 18, 1500.00, 'ADVANCE', '2026-07-23 13:08:52.821864+00', 'Adelanto', '2026-07-23 13:08:52.821864+00');
INSERT INTO public.event_payments (id, event_id, user_id, amount, payment_type, payment_date, notes, created_at) VALUES (7, 7, 17, 2800.00, 'REMAINING', '2026-07-30 10:49:42.724651+00', 'Pago en efectivo', '2026-07-30 10:49:42.724651+00');
INSERT INTO public.event_payments (id, event_id, user_id, amount, payment_type, payment_date, notes, created_at) VALUES (8, 9, 21, 1500.00, 'ADVANCE', '2026-07-31 10:49:42.724+00', 'PAgo por QR', '2026-07-31 17:38:10.982334+00');
INSERT INTO public.event_payments (id, event_id, user_id, amount, payment_type, payment_date, notes, created_at) VALUES (9, 9, 21, 2000.00, 'REMAINING', '2026-08-01 16:34:45.714845+00', 'Pago completado', '2026-08-01 16:34:45.714845+00');
INSERT INTO public.event_payments (id, event_id, user_id, amount, payment_type, payment_date, notes, created_at) VALUES (10, 10, 15, 1000.00, 'ADVANCE', '2026-08-01 16:43:15.65113+00', 'Adelanto', '2026-07-21 05:28:42.146701+00');
INSERT INTO public.event_payments (id, event_id, user_id, amount, payment_type, payment_date, notes, created_at) VALUES (11, 5, 15, 2500.00, 'REMAINING', '2026-08-01 16:44:16.435944+00', 'pago restante', '2026-08-01 16:44:16.435944+00');
INSERT INTO public.event_payments (id, event_id, user_id, amount, payment_type, payment_date, notes, created_at) VALUES (12, 4, 14, 1800.00, 'REMAINING', '2026-08-01 16:51:01.476546+00', 'saldo restante', '2026-08-01 16:51:01.476546+00');


--
-- Data for Name: musician_availability; Type: TABLE DATA; Schema: public; Owner: musician
--

INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (4, 8, '2026-07-25', 'Pegas Julio', '2026-07-21 05:12:05.830219+00', '2026-07-21 05:12:05.830219+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (5, 8, '2026-07-26', 'Pegas Julio', '2026-07-21 05:12:05.830219+00', '2026-07-21 05:12:05.830219+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (6, 8, '2026-07-27', 'Pegas Julio', '2026-07-21 05:12:05.830219+00', '2026-07-21 05:12:05.830219+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (7, 8, '2026-08-01', 'Pegas Agosto', '2026-07-21 05:12:46.84222+00', '2026-07-21 05:12:46.84222+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (8, 8, '2026-08-08', 'Pegas Agosto', '2026-07-21 05:12:46.84222+00', '2026-07-21 05:12:46.84222+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (9, 8, '2026-08-15', 'Pegas Agosto', '2026-07-21 05:12:46.84222+00', '2026-07-21 05:12:46.84222+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (10, 8, '2026-08-16', 'Pegas Agosto', '2026-07-21 05:12:46.84222+00', '2026-07-21 05:12:46.84222+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (11, 8, '2026-09-05', 'Pegas Septiembre Clizband', '2026-07-21 05:13:38.373884+00', '2026-07-21 05:13:38.373884+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (12, 8, '2026-09-06', 'Pegas Septiembre Clizband', '2026-07-21 05:13:38.373884+00', '2026-07-21 05:13:38.373884+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (13, 8, '2026-09-12', 'Pegas Septiembre Clizband', '2026-07-21 05:13:38.373884+00', '2026-07-21 05:13:38.373884+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (14, 8, '2026-09-13', 'Pegas Septiembre Clizband', '2026-07-21 05:13:38.373884+00', '2026-07-21 05:13:38.373884+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (15, 8, '2026-09-19', 'Pegas Septiembre Clizband', '2026-07-21 05:13:38.373884+00', '2026-07-21 05:13:38.373884+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (16, 8, '2026-09-20', 'Pegas Septiembre Clizband', '2026-07-21 05:13:38.373884+00', '2026-07-21 05:13:38.373884+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (17, 8, '2026-09-26', 'Pegas Septiembre Clizband', '2026-07-21 05:13:38.373884+00', '2026-07-21 05:13:38.373884+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (18, 8, '2026-10-10', 'Pegas Octubre', '2026-07-21 05:14:19.241242+00', '2026-07-21 05:14:19.241242+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (19, 8, '2026-10-17', 'Pegas Octubre', '2026-07-21 05:14:19.241242+00', '2026-07-21 05:14:19.241242+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (20, 8, '2026-10-18', 'Pegas Octubre', '2026-07-21 05:14:19.241242+00', '2026-07-21 05:14:19.241242+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (21, 8, '2026-11-07', 'Pegas Noviembre', '2026-07-21 05:15:16.245989+00', '2026-07-21 05:15:16.245989+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (22, 8, '2026-12-05', 'Pegas Diciembre', '2026-07-21 05:17:21.167059+00', '2026-07-21 05:17:21.167059+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (23, 8, '2026-12-06', 'Pegas Diciembre', '2026-07-21 05:17:21.167059+00', '2026-07-21 05:17:21.167059+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (24, 8, '2026-12-12', 'Pegas Diciembre', '2026-07-21 05:17:21.167059+00', '2026-07-21 05:17:21.167059+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (25, 8, '2026-12-13', 'Pegas Diciembre', '2026-07-21 05:17:21.167059+00', '2026-07-21 05:17:21.167059+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (26, 8, '2026-12-19', 'Pegas Diciembre', '2026-07-21 05:17:21.167059+00', '2026-07-21 05:17:21.167059+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (27, 8, '2026-12-20', 'Pegas Diciembre', '2026-07-21 05:17:21.167059+00', '2026-07-21 05:17:21.167059+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (28, 8, '2026-12-26', 'Pegas Diciembre', '2026-07-21 05:17:21.167059+00', '2026-07-21 05:17:21.167059+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (29, 8, '2026-12-27', 'Pegas Diciembre', '2026-07-21 05:17:21.167059+00', '2026-07-21 05:17:21.167059+00');
INSERT INTO public.musician_availability (id, musician_id, unavailable_date, reason, created_at, updated_at) VALUES (30, 12, '2026-07-25', 'pega santiago', '2026-07-21 05:19:04.969035+00', '2026-07-21 05:19:04.969035+00');


--
-- Data for Name: musician_event_payments; Type: TABLE DATA; Schema: public; Owner: musician
--

INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (11, 4, 9, 'ADVANCE', 200.00, '2026-07-21 05:08:19.297202+00', 'Adelanto', '2026-07-21 05:08:19.321713+00', '2026-07-21 05:08:19.321713+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (12, 7, 7, 'TOTAL', 400.00, '2026-07-30 10:50:42.107353+00', 'pago', '2026-07-30 10:50:42.131821+00', '2026-07-30 10:50:42.131821+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (13, 7, 10, 'TOTAL', 450.00, '2026-07-30 10:55:03.367527+00', NULL, '2026-07-30 10:55:03.386937+00', '2026-07-30 10:55:03.386937+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (14, 7, 12, 'TOTAL', 450.00, '2026-07-30 10:55:32.854713+00', 'Pago en efectivo', '2026-07-30 10:55:32.867074+00', '2026-07-30 10:55:32.867074+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (15, 7, 13, 'TOTAL', 450.00, '2026-07-30 10:55:58.371462+00', 'Pago en efectivo', '2026-07-30 10:55:58.386311+00', '2026-07-30 10:55:58.386311+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (16, 7, 19, 'TOTAL', 450.00, '2026-07-30 10:56:35.613725+00', 'Pago en efectivo', '2026-07-30 10:56:35.627162+00', '2026-07-30 10:56:35.627162+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (17, 4, 9, 'ADVANCE', 150.00, '2026-07-18 13:08:19.297+00', 'Adelanto', '2026-07-21 05:08:19.321713+00', '2026-07-21 05:08:19.321713+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (18, 4, 9, 'REMAINING', 50.00, '2026-07-30 11:01:37.715251+00', 'Saldo por QR', '2026-07-30 11:01:37.731203+00', '2026-07-30 11:01:37.731203+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (19, 4, 7, 'TOTAL', 400.00, '2026-07-30 11:02:10.809302+00', NULL, '2026-07-30 11:02:10.823927+00', '2026-07-30 11:02:10.823927+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (20, 4, 10, 'TOTAL', 450.00, '2026-07-30 11:02:32.686087+00', 'pago por qr', '2026-07-30 11:02:32.701833+00', '2026-07-30 11:02:32.701833+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (21, 4, 12, 'ADVANCE', 400.00, '2026-07-29 10:55:32.854+00', 'Pago en efectivo', '2026-07-30 10:55:32.867074+00', '2026-07-30 10:55:32.867074+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (22, 5, 9, 'ADVANCE', 100.00, '2026-07-29 16:02:32.686+00', 'pago por qr', '2026-07-30 11:02:32.701833+00', '2026-07-30 11:02:32.701833+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (23, 5, 10, 'ADVANCE', 100.00, '2026-07-29 16:02:32.686+00', 'pago por qr', '2026-07-30 11:02:32.701833+00', '2026-07-30 11:02:32.701833+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (24, 9, 7, 'TOTAL', 400.00, '2026-08-01 16:36:46.929123+00', 'pago total', '2026-08-01 16:36:46.967753+00', '2026-08-01 16:36:46.967753+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (25, 9, 8, 'TOTAL', 450.00, '2026-08-01 16:37:04.400936+00', 'pago total', '2026-08-01 16:37:04.42229+00', '2026-08-01 16:37:04.42229+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (26, 9, 9, 'TOTAL', 450.00, '2026-08-01 16:37:26.593925+00', 'pago total por QR', '2026-08-01 16:37:26.614772+00', '2026-08-01 16:37:26.614772+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (27, 5, 7, 'TOTAL', 400.00, '2026-08-01 16:46:21.998196+00', 'pago total', '2026-08-01 16:46:22.011112+00', '2026-08-01 16:46:22.011112+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (28, 5, 8, 'TOTAL', 450.00, '2026-08-01 16:46:49.975058+00', NULL, '2026-08-01 16:46:49.992323+00', '2026-08-01 16:46:49.992323+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (29, 5, 9, 'REMAINING', 350.00, '2026-08-01 16:48:09.085073+00', 'saldo', '2026-08-01 16:48:09.105237+00', '2026-08-01 16:48:09.105237+00');
INSERT INTO public.musician_event_payments (id, event_id, musician_id, payment_type, amount, payment_date, notes, created_at, updated_at) VALUES (30, 4, 8, 'TOTAL', 400.00, '2026-08-01 16:52:01.77855+00', 'pago total', '2026-08-01 16:52:01.794242+00', '2026-08-01 16:52:01.794242+00');


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: musician
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
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: musician
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
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (6, 7);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (6, 15);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (6, 16);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (6, 14);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (6, 17);
INSERT INTO public.role_permissions (role_id, permission_id) VALUES (6, 11);


--
-- Data for Name: user_details; Type: TABLE DATA; Schema: public; Owner: musician
--



--
-- Name: event_musicians_id_seq; Type: SEQUENCE SET; Schema: public; Owner: musician
--

SELECT pg_catalog.setval('public.event_musicians_id_seq', 36, true);


--
-- Name: event_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: musician
--

SELECT pg_catalog.setval('public.event_payments_id_seq', 12, true);


--
-- Name: events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: musician
--

SELECT pg_catalog.setval('public.events_id_seq', 10, true);


--
-- Name: musician_availability_id_seq; Type: SEQUENCE SET; Schema: public; Owner: musician
--

SELECT pg_catalog.setval('public.musician_availability_id_seq', 30, true);


--
-- Name: musician_event_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: musician
--

SELECT pg_catalog.setval('public.musician_event_payments_id_seq', 30, true);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: musician
--

SELECT pg_catalog.setval('public.permissions_id_seq', 19, true);


--
-- Name: user_details_id_seq; Type: SEQUENCE SET; Schema: public; Owner: musician
--

SELECT pg_catalog.setval('public.user_details_id_seq', 1, false);


--
-- Name: user_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: musician
--

SELECT pg_catalog.setval('public.user_roles_id_seq', 6, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: musician
--

SELECT pg_catalog.setval('public.users_id_seq', 22, true);


--
-- PostgreSQL database dump complete
--

\unrestrict dSIh4qZsz3BiD80KGMWtgVtoSN6rdWsTcPgYKkk33mJv1PxYLKW7UQRsh1fwJtM

