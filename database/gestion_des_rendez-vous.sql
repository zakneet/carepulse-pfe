-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : mer. 15 avr. 2026 à 12:18
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `gestion_des_rendez-vous`
--

-- --------------------------------------------------------

--
-- Structure de la table `planning`
--

CREATE TABLE `planning` (
  `idPlanning` int(11) NOT NULL,
  `date` date NOT NULL,
  `idPersonnel` int(11) DEFAULT NULL,
  `heureDebut` time NOT NULL,
  `heureFin` time NOT NULL,
  `duree_creneau` int(11) NOT NULL DEFAULT 30
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `rdv`
--

CREATE TABLE `rdv` (
  `idRDV` int(11) NOT NULL,
  `dateRDV` date NOT NULL,
  `heureDebut` time NOT NULL,
  `heureFin` time NOT NULL,
  `motifConsultation` text NOT NULL,
  `idPatient` int(11) DEFAULT NULL,
  `idPersonnel` int(11) DEFAULT NULL,
  `agePatient` int(11) DEFAULT NULL,
  `isUrgent` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `rdv`
--

INSERT INTO `rdv` (`idRDV`, `dateRDV`, `heureDebut`, `heureFin`, `motifConsultation`, `idPatient`, `idPersonnel`, `agePatient`, `isUrgent`) VALUES
(1, '2026-03-31', '08:00:00', '08:30:00', 'urgence', 11, 10, 85, 1),
(2, '2026-04-20', '09:00:00', '09:30:00', 'consultation', 1, 10, NULL, 0),
(3, '2026-04-21', '10:00:00', '10:30:00', 'Test', 1, 10, NULL, 0),
(4, '2026-04-22', '11:00:00', '11:30:00', 'consultation', 1, 10, NULL, 0),
(5, '2026-04-03', '10:30:00', '11:00:00', 'consultation', 11, 13, NULL, 0),
(6, '2026-04-03', '10:30:00', '11:00:00', 'consultation', 11, 13, NULL, 0),
(7, '2026-04-23', '12:00:00', '12:30:00', 'controle', 1, 10, NULL, 0),
(8, '2026-04-04', '12:00:00', '12:30:00', 'consultation', 11, 13, NULL, 0),
(18, '2026-04-02', '14:00:00', '14:30:00', 'Annule - Consultation 14h', 1, 12, NULL, 0),
(19, '2026-04-02', '14:30:00', '15:00:00', 'Annule - Consultation 14h30', 1, 12, NULL, 0),
(20, '2026-04-02', '15:00:00', '15:30:00', 'Annule - Consultation 15h', 1, 12, NULL, 0),
(21, '2026-04-02', '15:30:00', '16:00:00', 'Annule - Consultation 15h30', 1, 12, NULL, 0),
(22, '2026-04-03', '11:00:00', '11:30:00', 'Annule - controle', 1, 12, NULL, 0),
(23, '2026-04-10', '09:30:00', '10:00:00', 'consultation', 12, 13, NULL, 0),
(24, '2026-04-10', '09:30:00', '10:00:00', 'consultation', 12, 13, NULL, 0),
(25, '2026-04-04', '12:00:00', '12:30:00', 'Annule - consultation', 1, 12, NULL, 0),
(26, '2026-04-12', '10:30:00', '11:00:00', 'consultation', 12, 13, NULL, 0),
(27, '2026-04-12', '10:30:00', '11:00:00', 'consultation', 12, 13, NULL, 0),
(28, '2026-04-12', '10:30:00', '11:00:00', 'consultation', 12, 13, NULL, 0),
(29, '2026-04-12', '10:30:00', '11:00:00', 'consultation', 12, 13, NULL, 0),
(30, '2026-04-12', '10:30:00', '11:00:00', 'consultation', 12, 13, NULL, 0),
(31, '2026-04-12', '10:30:00', '11:00:00', 'consultation', 12, 13, NULL, 0),
(32, '2026-04-12', '10:30:00', '11:00:00', 'consultation', 12, 13, NULL, 0),
(33, '2026-04-05', '13:00:00', '13:30:00', 'Annule - consultation', 16, 12, NULL, 0),
(34, '2026-04-09', '09:30:00', '10:00:00', 'controle', 12, 10, NULL, 0),
(35, '2026-04-07', '12:00:00', '12:30:00', 'consultation', 12, 13, NULL, 0),
(36, '2026-04-07', '12:00:00', '12:30:00', 'consultation', 12, 13, NULL, 0),
(37, '2026-04-07', '12:00:00', '12:30:00', 'consultation', 12, 13, NULL, 0),
(38, '2026-04-07', '12:00:00', '12:30:00', 'consultation', 12, 13, NULL, 0),
(39, '2026-04-07', '12:00:00', '12:30:00', 'consultation', 12, 13, NULL, 0),
(40, '2026-04-07', '12:00:00', '12:30:00', 'consultation', 12, 13, NULL, 0),
(41, '2026-04-05', '14:00:00', '14:30:00', 'RDV test popup patient', 1, 12, NULL, 0),
(45, '2026-04-06', '16:30:00', '17:00:00', 'Annule - [TEST-URGENCE] Consultation #1', 1, 12, NULL, 0),
(46, '2026-04-06', '17:00:00', '17:30:00', 'Annule - [TEST-URGENCE] Consultation #2', 1, 12, NULL, 0),
(47, '2026-04-06', '17:30:00', '18:00:00', 'Annule - [TEST-URGENCE] Consultation #3', 1, 12, NULL, 0),
(48, '2026-04-06', '17:30:00', '18:00:00', 'Annule - [TEST-URGENCE] Consultation #4', 1, 12, NULL, 0),
(49, '2026-04-06', '16:00:00', '16:30:00', 'Annule - [TEST-VISIBLE] Consultation #1', 1, 12, NULL, 0),
(50, '2026-04-06', '16:30:00', '17:00:00', 'Annule - [TEST-VISIBLE] Consultation #2', 1, 12, NULL, 0),
(51, '2026-04-06', '17:00:00', '17:30:00', 'Annule - [TEST-VISIBLE] Consultation #3', 1, 12, NULL, 0),
(52, '2026-04-06', '17:30:00', '18:00:00', 'Annule - [TEST-VISIBLE] Consultation #4', 1, 12, NULL, 0),
(53, '2026-04-07', '14:00:00', '14:30:00', 'Annule - [TEST-VISIBLE] Consultation #1', 1, 12, NULL, 0),
(54, '2026-04-07', '14:30:00', '15:00:00', 'Annule - [TEST-VISIBLE] Consultation #2', 1, 12, NULL, 0),
(55, '2026-04-07', '15:00:00', '15:30:00', 'Annule - [TEST-VISIBLE] Consultation #3', 1, 12, NULL, 0),
(56, '2026-04-07', '15:30:00', '16:00:00', 'Annule - [TEST-VISIBLE] Consultation #4', 1, 12, NULL, 0),
(57, '2026-04-08', '14:00:00', '14:30:00', 'Annule - [TEST-VISIBLE] Consultation #1', 1, 12, NULL, 0),
(58, '2026-04-08', '14:30:00', '15:00:00', 'Annule - [TEST-VISIBLE] Consultation #2', 1, 12, NULL, 0),
(59, '2026-04-08', '15:00:00', '15:30:00', 'Annule - [TEST-VISIBLE] Consultation #3', 1, 12, NULL, 0),
(60, '2026-04-08', '15:30:00', '16:00:00', 'Annule - [TEST-VISIBLE] Consultation #4', 1, 12, NULL, 0),
(65, '2026-04-10', '14:00:00', '14:30:00', 'Annule - [TEST-VISIBLE] Consultation #1', 1, 12, NULL, 0),
(66, '2026-04-10', '14:30:00', '15:00:00', 'Annule - [TEST-VISIBLE] Consultation #2', 1, 12, NULL, 0),
(67, '2026-04-10', '15:00:00', '15:30:00', 'Annule - [TEST-VISIBLE] Consultation #3', 1, 12, NULL, 0),
(68, '2026-04-10', '15:30:00', '16:00:00', 'Annule - [TEST-VISIBLE] Consultation #4', 1, 12, NULL, 0),
(69, '2026-04-11', '14:00:00', '14:30:00', 'Annule - [TEST-VISIBLE] Consultation #1', 1, 12, NULL, 0),
(70, '2026-04-11', '14:30:00', '15:00:00', 'Annule - [TEST-VISIBLE] Consultation #2', 1, 12, NULL, 0),
(71, '2026-04-11', '15:00:00', '15:30:00', 'Annule - [TEST-VISIBLE] Consultation #3', 1, 12, NULL, 0),
(72, '2026-04-11', '15:30:00', '16:00:00', 'Annule - [TEST-VISIBLE] Consultation #4', 1, 12, NULL, 0),
(73, '2026-04-12', '14:00:00', '14:30:00', 'Annule - [TEST-VISIBLE] Consultation #1', 1, 12, NULL, 0),
(74, '2026-04-12', '14:30:00', '15:00:00', 'Annule - [TEST-VISIBLE] Consultation #2', 1, 12, NULL, 0),
(75, '2026-04-12', '15:00:00', '15:30:00', 'Annule - [TEST-VISIBLE] Consultation #3', 1, 12, NULL, 0),
(76, '2026-04-12', '15:30:00', '16:00:00', 'Annule - [TEST-VISIBLE] Consultation #4', 1, 12, NULL, 0),
(97, '2026-04-09', '16:00:00', '16:30:00', 'Annule - TEST - Consultation 1', 1, 12, NULL, 0),
(98, '2026-04-09', '16:30:00', '17:00:00', 'Annule - TEST - Consultation 2', 1, 12, NULL, 0),
(99, '2026-04-09', '17:00:00', '17:30:00', 'Annule - TEST - Consultation 3', 1, 12, NULL, 0),
(100, '2026-04-09', '18:00:00', '18:30:00', 'Annule - TEST - Consultation 4', 1, 12, NULL, 0),
(101, '2026-04-14', '09:00:00', '09:30:00', 'consultation', 17, 13, NULL, 0),
(102, '2026-04-14', '09:30:00', '10:00:00', 'consultation', 19, 13, NULL, 0),
(103, '2026-04-17', '09:00:00', '09:30:00', 'consultation', 12, 13, NULL, 0),
(104, '2026-04-14', '10:00:00', '10:30:00', 'consultation', 21, 13, NULL, 0),
(105, '2026-04-14', '11:00:00', '11:30:00', 'consultation', 22, 13, NULL, 0),
(106, '2026-04-14', '16:30:00', '17:00:00', 'consultation', 24, 13, NULL, 0),
(107, '2026-04-17', '09:30:00', '10:00:00', 'consultation', 12, 13, NULL, 0),
(108, '2026-04-14', '10:30:00', '11:00:00', 'consultation', 25, 13, NULL, 0),
(109, '2026-04-14', '11:30:00', '12:00:00', 'consultation', 27, 13, NULL, 0),
(110, '2026-04-14', '15:00:00', '15:30:00', 'consultation', 28, 13, NULL, 0),
(111, '2026-04-17', '10:00:00', '10:30:00', 'consultation', 12, 13, NULL, 0),
(112, '2026-04-16', '09:00:00', '09:30:00', 'consultation', 12, 10, NULL, 0),
(113, '2026-04-14', '13:00:00', '13:30:00', 'consultation', 30, 13, NULL, 0),
(114, '2026-04-16', '10:00:00', '10:30:00', 'consultation', 12, 10, NULL, 0),
(115, '2026-04-15', '09:00:00', '09:30:00', 'consultation', 31, 13, NULL, 0),
(116, '2026-04-15', '08:00:00', '08:30:00', 'TEST - Consultation 1', 1, 12, NULL, 0),
(117, '2026-04-15', '09:30:00', '10:00:00', 'TEST - Consultation 2', 1, 12, NULL, 0),
(118, '2026-04-15', '09:30:00', '10:00:00', 'TEST - Consultation 3', 1, 12, NULL, 0),
(119, '2026-04-15', '10:30:00', '11:00:00', 'TEST - Consultation 4', 1, 12, NULL, 0),
(120, '2026-04-15', '11:00:00', '11:30:00', 'TEST 11H - Consultation 1', 1, 12, NULL, 0),
(121, '2026-04-15', '11:30:00', '12:00:00', 'TEST 11H - Consultation 2', 1, 12, NULL, 0),
(122, '2026-04-15', '12:00:00', '12:30:00', 'TEST 11H - Consultation 3', 1, 12, NULL, 0),
(123, '2026-04-15', '12:30:00', '13:00:00', 'TEST 11H - Consultation 4', 'consultation', 1, 12, NULL, 0);



CREATE TABLE `personnel_de_sante` (
  `id_personnel` int(11) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `specialite` varchar(120) DEFAULT NULL,
  `disponibilite` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

ALTER TABLE `personnel_de_sante`
  ADD PRIMARY KEY (`id_personnel`);

ALTER TABLE `personnel_de_sante`
  MODIFY `id_personnel` int(11) NOT NULL AUTO_INCREMENT;

-- --------------------------------------------------------

--
-- Structure de la table `user`
--
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `telephone` varchar(30) DEFAULT NULL,
  `specialite` varchar(120) DEFAULT NULL,
  `disponibilite` varchar(255) DEFAULT NULL,
  `statut` int(11) NOT NULL,
  `email` varchar(120) DEFAULT NULL,
  `password` varchar(255) NOT NULL DEFAULT '',
  `role` int(11) NOT NULL,
  `access_code` varchar(120) DEFAULT NULL,
  `cin` varchar(50) DEFAULT NULL,
  `sexe` varchar(20) DEFAULT NULL,
  `date_naissance` date DEFAULT NULL,
  `allergies` text DEFAULT NULL,
  `maladies` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `user`
--

INSERT INTO `user` (`id`, `nom`, `prenom`, `telephone`, `specialite`, `disponibilite`, `statut`, `email`, `password`, `role`, `access_code`, `cin`, `sexe`, `date_naissance`, `allergies`, `maladies`) VALUES
(1, 'yasmine', 'Dhaou', '26748930', NULL, NULL, 1, 'yasmine.dhaou321@gmail.com', '', 1, NULL, '14857309', 'Feminin', '2002-10-05', '', ''),
(2, 'Test', 'User', '0600000000', NULL, NULL, 1, NULL, '', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(3, 'Login', 'Check', '0600000001', NULL, NULL, 1, NULL, '', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(4, 'fekih ', 'zakaria', '51065096', NULL, NULL, 1, NULL, '', 1, NULL, NULL, NULL, NULL, NULL, NULL),

-- --------------------------------------------------------

--
-- Structure de la table `patient`
--

CREATE TABLE `patient` (
  `id_patient` int(11) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `telephone` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

ALTER TABLE `patient`
  ADD PRIMARY KEY (`id_patient`);

ALTER TABLE `patient`
  MODIFY `id_patient` int(11) NOT NULL AUTO_INCREMENT;

-- --------------------------------------------------------

--
-- Structure de la table `fiche_patient`
--

CREATE TABLE `fiche_patient` (
  `idfiche` int(11) NOT NULL,
  `idpatient` int(11) NOT NULL,
  `idpersonnel` int(11) DEFAULT NULL,
  `nom` varchar(100) DEFAULT NULL,
  `prenom` varchar(100) DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `etat_civil` varchar(120) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

ALTER TABLE `fiche_patient`
  ADD PRIMARY KEY (`idfiche`),
  ADD UNIQUE KEY `uq_dossier_patient` (`idpatient`),
  ADD KEY `idx_dossier_personnel` (`idpersonnel`);

ALTER TABLE `fiche_patient`
  MODIFY `idfiche` int(11) NOT NULL AUTO_INCREMENT;
(5, 'Testeur', 'Patient', '0123456789', NULL, NULL, 1, NULL, '', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(8, 'fekih ', 'zak', '24960458', NULL, NULL, 1, NULL, '', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(9, 'fekih', 'zakzouka', '51065096', NULL, NULL, 1, NULL, '', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(10, 'Med', 'Staff', '0600000000', 'Generaliste', 'Lun-Ven', 1, NULL, '', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(11, 'NomTestSave', 'PrenomTestSave', '0611111111', NULL, NULL, 1, 'save_test@example.com', '', 1, NULL, 'CIN-PERSIST-777', 'F', NULL, 'penicilline, arachide', 'asthme'),
(12, 'Dupont', 'Jean', '26482929', 'GEN', 'OUI', 1, 'jean@gmail.com', 'root', 2, 'STAFF2026', NULL, NULL, NULL, NULL, NULL),
(13, 'Docteur', 'Martin', NULL, 'Cardiologie', NULL, 1, NULL, '', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(15, 'dhaou', 'nahla', '29292525', NULL, NULL, 0, 'glmk.homeetcie@gmail.com', 'nahla123', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(16, 'dhaou', 'hedi', '26482929', NULL, NULL, 0, 'nadine.dhaou321@gmail.com', '', 1, NULL, '15027203', 'Feminin', '2004-01-10', '', ''),
(17, 'Patient_Test_1776088219', 'Test', NULL, NULL, NULL, 0, NULL, '', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(19, 'Patient_Test_1776088219_3', 'Test', NULL, NULL, NULL, 0, NULL, '', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(21, 'TestSansEmail', 'Sans_Email', NULL, NULL, NULL, 0, NULL, '', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(22, 'FormulaireFront', 'E2E_Test', NULL, NULL, NULL, 0, NULL, '', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(24, 'FormulaireFront', 'E2E_Test', NULL, NULL, NULL, 0, NULL, '', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(25, 'TestDiag', 'Diagnostic', '0612345678', NULL, NULL, 0, 'test@diagnostic.com', '', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(27, 'TestDiag', 'Diagnostic', '0612345678', NULL, NULL, 0, 'patient_425531@gestion-rdv.local', '', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(28, 'FinalTest', 'CompletFlow', '0612345678', NULL, NULL, 0, 'patient.final369263@test.com', '', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(29, 'fekih', 'zakaria', '51065096', NULL, NULL, 0, 'patient_803375@gestion-rdv.local', '', 1, NULL, '14523796', NULL, NULL, NULL, NULL),
(30, 'FormulaireFront', 'E2E_Test', NULL, NULL, NULL, 0, 'patient_105469@gestion-rdv.local', '', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(31, 'Check', 'Persist', NULL, NULL, NULL, 0, 'patient_510714@gestion-rdv.local', '', 1, NULL, NULL, NULL, NULL, NULL, NULL);

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `planning`
--
ALTER TABLE `planning`
  ADD PRIMARY KEY (`idPlanning`),
  ADD KEY `fk_planning_personnel` (`idPersonnel`);

--
-- Index pour la table `rdv`
--
ALTER TABLE `rdv`
  ADD PRIMARY KEY (`idRDV`),
  ADD KEY `fk_rdv_patient` (`idPatient`),
  ADD KEY `fk_rdv_personnel` (`idPersonnel`);

--
-- Index pour la table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_user_email` (`email`),
  ADD UNIQUE KEY `uq_user_access_code` (`access_code`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `planning`
--
ALTER TABLE `planning`
  MODIFY `idPlanning` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `rdv`
--
ALTER TABLE `rdv`
  MODIFY `idRDV` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=124;

--
-- AUTO_INCREMENT pour la table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `planning`
--
ALTER TABLE `planning`
  ADD CONSTRAINT `fk_planning_personnel` FOREIGN KEY (`idPersonnel`) REFERENCES `user` (`id`) ON UPDATE CASCADE;

--
-- Contraintes pour la table `rdv`
--
ALTER TABLE `rdv`
  ADD CONSTRAINT `fk_rdv_patient` FOREIGN KEY (`idPatient`) REFERENCES `user` (`id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_rdv_personnel` FOREIGN KEY (`idPersonnel`) REFERENCES `user` (`id`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
