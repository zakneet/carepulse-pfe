-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : jeu. 28 mai 2026 à 13:52
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

--
-- Déchargement des données de la table `patient`
--

INSERT INTO `patient` (`id_patient`, `nom`, `prenom`, `telephone`) VALUES
(1, 'Test', 'Patient', NULL),
(2, 'Test', 'User', '0600000000'),
(3, 'Phone', 'Patient', '0612345678'),
(4, 'Pwd', 'Patient', '0700000001'),
(5, 'jean', 'dupont', '29292525'),
(6, 'fekih', 'zak', '24960458'),
(7, 'jean', 'dupont', '0655443322'),
(8, 'Med', 'Staff', '0600000000'),
(9, 'NomTestSave', 'PrenomTestSave', '0611111111'),
(10, 'Dupont', 'Jean', '26482929'),
(11, 'Docteur', 'Martin', NULL),
(12, 'TestPatient', 'Pat', '0700000000'),
(13, 'Docteur', 'Martin', NULL),
(16, 'Test', 'User', '0600000000'),
(17, 'Login', 'Check', '0600000001'),
(18, 'fekih ', 'zakaria', '51065096'),
(19, 'Testeur', 'Patient', '0123456789'),
(20, 'fekih ', 'zak', '24960458'),
(21, 'fekih', 'zakzouka', '51065096'),
(22, 'Med', 'Staff', '0600000000'),
(23, 'Docteur', 'Martin', NULL),
(24, 'dhaou', 'nahla', '29292525'),
(25, 'dhaou', 'nadine', '24960458'),
(26, 'Patient_Test_1776088219', 'Test', NULL),
(27, 'Patient_Test_1776088219_3', 'Test', NULL),
(28, 'TestSansEmail', 'Sans_Email', NULL),
(29, 'FormulaireFront', 'E2E_Test', NULL),
(30, 'FormulaireFront', 'E2E_Test', NULL),
(31, 'TestDiag', 'Diagnostic', '0612345678'),
(32, 'TestDiag', 'Diagnostic', '0612345678'),
(33, 'FinalTest', 'CompletFlow', '0612345678'),
(34, 'jean', 'hedi', '23456123'),
(35, 'FormulaireFront', 'E2E_Test', NULL),
(36, 'Check', 'Persist', NULL),
(37, 'FormulaireFront', 'E2E_Test', NULL),
(38, 'NewPat', 'Test', '0600000001'),
(39, 'dhaou', 'nadine', ''),
(40, 'dhaou', 'nadine', '12345678'),
(41, 'eya', 'dhaou', '98765432'),
(42, 'dhaou', 'nadine', ''),
(43, 'dhaou', 'yasmine', ''),
(44, 'dhaou', 'nadine', ''),
(45, 'dhaou', 'nadine', ''),
(46, 'dhaou', 'nadine', '24960458'),
(47, 'UrgentTest', 'SansCin', '0600000000'),
(48, 'dhaou', 'hanine', '56347234'),
(49, 'dhaou', 'hanine', '32786456'),
(50, 'dhaou', 'hanine', '23674985'),
(51, 'Test', 'Urgent', '12345678');

-- --------------------------------------------------------

--
-- Structure de la table `personnel_de_sante`
--

CREATE TABLE `personnel_de_sante` (
  `id_personnel` int(11) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `specialite` varchar(120) DEFAULT NULL,
  `disponibilite` tinyint(1) NOT NULL DEFAULT 1,
  `region` varchar(120) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `personnel_de_sante`
--

INSERT INTO `personnel_de_sante` (`id_personnel`, `nom`, `prenom`, `specialite`, `disponibilite`, `region`) VALUES
(1, 'Labidi', 'Meher', 'Pediatre', 1, 'Tunis (Ville)'),
(2, 'Gharbi', 'Ahmed', 'Ophtalmologie', 1, 'Sidi Hassine'),
(3, 'Mabrouk', 'Karim', 'Cardiologie', 1, 'Ezzouhour'),
(4, 'Sassi', 'Youssef', 'Orthopédie', 1, 'Cité El Khadhra'),
(5, 'Ben Ali', 'Ahmed', 'Cardiologie', 1, 'La Marsa'),
(6, 'Mabrouk', 'Asma', 'Orthopédie', 1, 'Tunis (Ville)'),
(7, 'Sassi', 'Nizar', 'Dentaire', 1, 'Cité El Khadhra'),
(8, 'Mabrouk', 'Fatma', 'Orthopédie', 1, 'La Médina'),
(9, 'Trabelsi', 'Walid', 'Neurologie', 1, 'Bab Souika'),
(10, 'Mansour', 'Karim', 'Pédiatrie', 1, 'Bab Souika'),
(11, 'Gharbi', 'Youssef', 'Neurologie', 1, 'La Goulette'),
(12, 'Riahi', 'Leïla', 'Orthopédie', 1, 'La Médina'),
(13, 'Ben Ali', 'Fatma', 'Dentaire', 1, 'La Goulette'),
(14, 'Khlifi', 'Youssef', 'Dentaire', 1, 'Bab El Bhar'),
(15, 'Zouari', 'Leïla', 'Orthopédie', 1, 'La Marsa'),
(16, 'Ben Ammar', 'Mohamed', 'Pédiatrie', 1, 'Bab El Bhar'),
(17, 'Ben Ammar', 'Mehdi', 'Cardiologie', 1, 'El Menzah'),
(18, 'Mansour', 'Fatma', 'Gynécologie', 1, 'Sidi Bou Saïd'),
(19, 'Riahi', 'Leïla', 'Pédiatrie', 1, 'Ezzouhour'),
(20, 'Mansour', 'Youssef', 'Orthopédie', 1, 'Séjoumi'),
(21, 'Bouazizi', 'Rim', 'Pédiatrie', 1, 'Sidi Bou Saïd'),
(22, 'Amri', 'Nadia', 'Ophtalmologie', 1, 'Séjoumi'),
(23, 'Sassi', 'Mehdi', 'Gynécologie', 1, 'Le Bardo'),
(24, 'Mabrouk', 'Mohamed', 'Gynécologie', 1, 'El Menzah'),
(25, 'Mansour', 'Youssef', 'Pédiatrie', 1, 'El Ouardia'),
(26, 'Ayari', 'Nizar', 'Psychiatrie', 1, 'El Menzah'),
(27, 'Amri', 'Karim', 'Ophtalmologie', 1, 'Carthage'),
(28, 'Mabrouk', 'Rim', 'Dentaire', 1, 'La Médina'),
(29, 'Touati', 'Sarra', 'Orthopédie', 1, 'El Menzah'),
(30, 'Riahi', 'Mehdi', 'Dermatologie', 1, 'Ettahrir'),
(31, 'Baccouche', 'Youssef', 'Médecine générale', 1, 'La Goulette'),
(32, 'Cherif', 'Walid', 'Neurologie', 1, 'El Kabaria'),
(33, 'Ben Ammar', 'Nadia', 'Neurologie', 1, 'El Kabaria'),
(34, 'Amri', 'Asma', 'Ophtalmologie', 1, 'Djebel Djelloud'),
(35, 'Trabelsi', 'Sami', 'Dentaire', 1, 'La Médina'),
(36, 'Ayari', 'Sami', 'Ophtalmologie', 1, 'Cité El Khadhra'),
(37, 'Bouazizi', 'Fatma', 'Médecine générale', 1, 'La Médina'),
(38, 'Miled', 'Walid', 'Dentaire', 1, 'La Goulette'),
(39, 'Haddad', 'Asma', 'Orthopédie', 1, 'La Marsa'),
(40, 'Cherif', 'Leïla', 'Dermatologie', 1, 'Djebel Djelloud'),
(41, 'Miled', 'Ahmed', 'Orthopédie', 1, 'Bab Souika'),
(42, 'Baccouche', 'Ahmed', 'Cardiologie', 1, 'Sidi El Béchir'),
(43, 'Haddad', 'Mehdi', 'Médecine générale', 1, 'Sidi Hassine'),
(44, 'Touati', 'Youssef', 'Cardiologie', 1, 'El Omrane Supérieur'),
(45, 'Ben Ammar', 'Rim', 'Dermatologie', 1, 'Carthage'),
(46, 'Baccouche', 'Rim', 'Dermatologie', 1, 'La Médina'),
(47, 'Miled', 'Yasmine', 'Neurologie', 1, 'La Marsa'),
(48, 'Sassi', 'Nizar', 'Ophtalmologie', 1, 'El Menzah'),
(49, 'Riahi', 'Fatma', 'Dentaire', 1, 'El Omrane'),
(50, 'Gharbi', 'Mehdi', 'Pédiatrie', 1, 'Le Kram'),
(51, 'Ayari', 'Ahmed', 'Orthopédie', 1, 'Djebel Djelloud'),
(52, 'Mabrouk', 'Safa', 'Pédiatrie', 1, 'Tunis (Ville)'),
(53, 'Ben Ammar', 'Mohamed', 'Pédiatrie', 1, 'Le Kram'),
(54, 'Ben Ali', 'Amira', 'Cardiologie', 1, 'Ettahrir'),
(55, 'Mabrouk', 'Ali', 'Psychiatrie', 1, 'La Marsa'),
(56, 'Sassi', 'Karim', 'Orthopédie', 1, 'El Ouardia'),
(57, 'Baccouche', 'Mehdi', 'Psychiatrie', 1, 'Cité El Khadhra'),
(58, 'Jaziri', 'Sami', 'Cardiologie', 1, 'Ezzouhour'),
(59, 'Zitouni', 'Leïla', 'Neurologie', 1, 'Cité El Khadhra'),
(60, 'Amri', 'Mohamed', 'Cardiologie', 1, 'Le Bardo'),
(61, 'Khlifi', 'Amira', 'Cardiologie', 1, 'Sidi Hassine'),
(62, 'Jaziri', 'Nizar', 'Dentaire', 1, 'El Omrane'),
(63, 'Cherif', 'Sarra', 'Dermatologie', 1, 'La Médina'),
(64, 'Amri', 'Mehdi', 'Cardiologie', 1, 'El Omrane'),
(65, 'Sassi', 'Sami', 'Médecine générale', 1, 'Séjoumi'),
(66, 'Sassi', 'Ahmed', 'Cardiologie', 1, 'Sidi Hassine'),
(67, 'Bouazizi', 'Sarra', 'Psychiatrie', 1, 'El Omrane Supérieur'),
(68, 'Jaziri', 'Nadia', 'Médecine générale', 1, 'Sidi Bou Saïd'),
(69, 'Khlifi', 'Ahmed', 'Neurologie', 1, 'La Médina'),
(70, 'Amri', 'Amine', 'Neurologie', 1, 'El Hrairia'),
(71, 'Sassi', 'Mouna', 'Dermatologie', 1, 'La Marsa'),
(72, 'Haddad', 'Nizar', 'Médecine générale', 1, 'El Ouardia'),
(73, 'Sassi', 'Mohamed', 'Gynécologie', 1, 'Le Bardo'),
(74, 'Ben Ali', 'Safa', 'Psychiatrie', 1, 'Ettahrir'),
(75, 'Miled', 'Walid', 'Médecine générale', 1, 'Ettahrir'),
(76, 'Ben Ammar', 'Walid', 'Cardiologie', 1, 'El Kabaria'),
(77, 'Ben Ammar', 'Mehdi', 'Neurologie', 1, 'La Goulette'),
(78, 'Touati', 'Mehdi', 'Orthopédie', 1, 'El Kabaria'),
(79, 'Ben Ali', 'Yasmine', 'Cardiologie', 1, 'Cité El Khadhra'),
(80, 'Touati', 'Safa', 'Dentaire', 1, 'Bab Souika'),
(81, 'Mansour', 'Nizar', 'Gynécologie', 1, 'Sidi Hassine'),
(82, 'Mansour', 'Nadia', 'Dermatologie', 1, 'Ezzouhour'),
(83, 'Haddad', 'Fatma', 'Gynécologie', 1, 'Le Kram'),
(84, 'Trabelsi', 'Fatma', 'Orthopédie', 1, 'El Ouardia'),
(85, 'Gharbi', 'Youssef', 'Dentaire', 1, 'La Marsa'),
(86, 'Miled', 'Ali', 'Dermatologie', 1, 'Sidi El Béchir'),
(87, 'Ben Ammar', 'Mehdi', 'Gynécologie', 1, 'Bab El Bhar'),
(88, 'Bouazizi', 'Fatma', 'Dentaire', 1, 'El Hrairia'),
(89, 'Haddad', 'Yasmine', 'Dentaire', 1, 'Tunis (Ville)'),
(90, 'Sassi', 'Amine', 'Cardiologie', 1, 'Carthage'),
(91, 'Mansour', 'Sami', 'Cardiologie', 1, 'Djebel Djelloud'),
(92, 'Cherif', 'Ali', 'Ophtalmologie', 1, 'El Kabaria'),
(93, 'Jaziri', 'Amira', 'Pédiatrie', 1, 'Ezzouhour'),
(94, 'Mansour', 'Asma', 'Psychiatrie', 1, 'La Médina'),
(95, 'Ben Ali', 'Youssef', 'Neurologie', 1, 'La Médina'),
(96, 'Ben Ali', 'Ahmed', 'Gynécologie', 1, 'Carthage'),
(97, 'Mansour', 'Walid', 'Psychiatrie', 1, 'Djebel Djelloud'),
(98, 'Zitouni', 'Rim', 'Médecine générale', 1, 'La Goulette'),
(99, 'Ben Ammar', 'Karim', 'Dentaire', 1, 'Le Bardo'),
(100, 'Riahi', 'Safa', 'Dentaire', 1, 'Carthage'),
(101, 'Zitouni', 'Karim', 'Médecine générale', 1, 'Bab El Bhar');

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
  `agePatient` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `rdv`
--

INSERT INTO `rdv` (`idRDV`, `dateRDV`, `heureDebut`, `heureFin`, `motifConsultation`, `idPatient`, `idPersonnel`, `agePatient`) VALUES
(182, '2026-05-13', '09:00:00', '09:30:00', 'consultation', 6, 37, NULL),
(183, '2026-05-13', '09:00:00', '09:30:00', 'consultation', 39, 39, NULL),
(184, '2026-05-13', '09:00:00', '09:30:00', 'consultation', 6, 12, NULL),
(185, '2026-05-12', '19:00:00', '19:30:00', 'TEST CABINET TODAY', 1, 1, NULL),
(186, '2026-05-12', '19:00:00', '19:30:00', 'TEST CABINET NADINE', 40, 1, NULL),
(187, '2026-05-19', '09:00:00', '09:30:00', 'TEST - Consultation 1', 1, 1, NULL),
(188, '2026-05-19', '16:30:00', '17:00:00', 'TEST - Consultation 2', 1, 1, NULL),
(189, '2026-05-19', '15:30:00', '16:00:00', 'TEST - Consultation 3', 1, 1, NULL),
(190, '2026-05-19', '15:00:00', '15:30:00', 'TEST - Consultation 4', 1, 1, NULL),
(191, '2026-05-21', '09:00:00', '09:30:00', 'TEST - Consultation 1', 1, 1, NULL),
(192, '2026-05-21', '09:30:00', '10:00:00', 'TEST - Consultation 2', 1, 1, NULL),
(193, '2026-05-21', '10:00:00', '10:30:00', 'TEST - Consultation 3', 1, 1, NULL),
(194, '2026-05-21', '10:30:00', '11:00:00', 'TEST - Consultation 4', 1, 1, NULL),
(195, '2026-05-22', '09:30:00', '10:00:00', 'consultation', 40, 37, NULL),
(196, '2026-05-22', '10:00:00', '10:30:00', 'consultation', 40, 37, NULL),
(197, '2026-05-21', '10:00:00', '10:30:00', 'consultation', 40, 12, NULL),
(198, '2026-05-21', '11:00:00', '11:30:00', 'consultation', 40, 37, NULL),
(199, '2026-05-21', '16:00:00', '16:30:00', 'consultation', 40, 2, NULL),
(200, '2026-05-21', '13:00:00', '08:30:00', 'consultation', 42, 1, NULL),
(201, '2026-05-21', '11:30:00', '12:00:00', 'consultation', 40, 1, NULL),
(202, '2026-05-22', '10:00:00', '10:30:00', 'consultation', 1, 1, NULL),
(203, '2026-05-22', '12:00:00', '12:30:00', 'consultation', 44, 1, NULL),
(204, '2026-05-22', '12:30:00', '13:00:00', 'TEST - Consultation 1', 1, 1, NULL),
(205, '2026-05-22', '13:00:00', '13:30:00', 'TEST - Consultation 2', 1, 1, NULL),
(206, '2026-05-22', '13:30:00', '14:00:00', 'TEST - Consultation 3', 1, 1, NULL),
(207, '2026-05-22', '14:00:00', '14:30:00', 'TEST - Consultation 4', 1, 1, NULL),
(212, '2026-05-22', '16:00:00', '16:30:00', 'TEST - Consultation 1', 1, 12, NULL),
(213, '2026-05-22', '16:30:00', '17:00:00', 'TEST - Consultation 2', 1, 12, NULL),
(214, '2026-05-22', '16:00:00', '16:30:00', 'TEST - Consultation 3', 1, 12, NULL),
(215, '2026-05-22', '16:30:00', '17:00:00', 'TEST - Consultation 4', 1, 12, NULL),
(216, '2026-05-23', '10:00:00', '10:30:00', 'TEST - Consultation 1', 1, 12, NULL),
(217, '2026-05-23', '10:30:00', '11:00:00', 'TEST - Consultation 2', 1, 12, NULL),
(218, '2026-05-23', '11:00:00', '11:30:00', 'TEST - Consultation 3', 1, 12, NULL),
(219, '2026-05-23', '11:30:00', '12:00:00', 'TEST - Consultation 4', 1, 12, NULL),
(220, '2026-05-23', '12:00:00', '12:30:00', 'TEST - Consultation 5', 1, 12, NULL),
(222, '2026-05-24', '13:30:00', '14:00:00', 'TEST - Consultation 1', 1, 12, NULL),
(223, '2026-05-24', '15:00:00', '15:30:00', 'TEST - Consultation 2', 1, 12, NULL),
(224, '2026-05-24', '15:30:00', '16:00:00', 'TEST - Consultation 3', 1, 12, NULL),
(225, '2026-05-24', '19:00:00', '19:30:00', 'TEST - Consultation 4', 1, 12, NULL),
(226, '2026-05-24', '19:30:00', '20:00:00', 'TEST - Consultation 5', 1, 12, NULL),
(228, '2026-05-26', '10:00:00', '10:30:00', 'consultation', 45, 1, NULL),
(290, '2026-05-26', '08:00:00', '08:30:00', 'TEST - Remplissage planning - 2026-05-26', 23, 12, NULL),
(291, '2026-05-26', '08:30:00', '09:00:00', 'TEST - Remplissage planning - 2026-05-26', 24, 12, NULL),
(292, '2026-05-26', '09:00:00', '09:30:00', 'TEST - Remplissage planning - 2026-05-26', 25, 12, NULL),
(293, '2026-05-26', '09:30:00', '10:00:00', 'TEST - Remplissage planning - 2026-05-26', 26, 12, NULL),
(294, '2026-05-26', '10:00:00', '10:30:00', 'TEST - Remplissage planning - 2026-05-26', 27, 12, NULL),
(310, '2026-05-27', '08:00:00', '08:30:00', 'TEST - Remplissage planning - 2026-05-27', 43, 12, NULL),
(311, '2026-05-27', '08:30:00', '09:00:00', 'TEST - Remplissage planning - 2026-05-27', 44, 12, NULL),
(312, '2026-05-27', '09:00:00', '09:30:00', 'TEST - Remplissage planning - 2026-05-27', 45, 12, NULL),
(313, '2026-05-27', '09:30:00', '10:00:00', 'TEST - Remplissage planning - 2026-05-27', 46, 12, NULL),
(314, '2026-05-27', '10:00:00', '10:30:00', 'TEST - Remplissage planning - 2026-05-27', 1, 12, NULL),
(330, '2026-05-28', '08:00:00', '08:30:00', 'TEST - Remplissage planning - 2026-05-28', 19, 12, NULL),
(331, '2026-05-28', '08:30:00', '09:00:00', 'TEST - Remplissage planning - 2026-05-28', 20, 12, NULL),
(332, '2026-05-28', '09:00:00', '09:30:00', 'TEST - Remplissage planning - 2026-05-28', 21, 12, NULL),
(333, '2026-05-28', '09:30:00', '10:00:00', 'TEST - Remplissage planning - 2026-05-28', 22, 12, NULL),
(334, '2026-05-28', '10:00:00', '10:30:00', 'TEST - Remplissage planning - 2026-05-28', 23, 12, NULL),
(350, '2026-05-29', '08:00:00', '08:30:00', 'TEST - Remplissage planning - 2026-05-29', 39, 12, NULL),
(351, '2026-05-29', '08:30:00', '09:00:00', 'TEST - Remplissage planning - 2026-05-29', 40, 12, NULL),
(352, '2026-05-29', '09:00:00', '09:30:00', 'TEST - Remplissage planning - 2026-05-29', 41, 12, NULL),
(353, '2026-05-29', '09:30:00', '10:00:00', 'TEST - Remplissage planning - 2026-05-29', 42, 12, NULL),
(354, '2026-05-29', '10:00:00', '10:30:00', 'TEST - Remplissage planning - 2026-05-29', 43, 12, NULL),
(370, '2026-05-30', '08:00:00', '08:30:00', 'TEST - Remplissage planning - 2026-05-30', 13, 12, NULL),
(371, '2026-05-30', '08:30:00', '09:00:00', 'TEST - Remplissage planning - 2026-05-30', 16, 12, NULL),
(372, '2026-05-30', '09:00:00', '09:30:00', 'TEST - Remplissage planning - 2026-05-30', 17, 12, NULL),
(373, '2026-05-30', '09:30:00', '10:00:00', 'TEST - Remplissage planning - 2026-05-30', 18, 12, NULL),
(374, '2026-05-30', '10:00:00', '10:30:00', 'TEST - Remplissage planning - 2026-05-30', 19, 12, NULL),
(395, '2026-05-25', '13:00:00', '13:30:00', 'TEST - Consultation 1', 1, 12, NULL),
(396, '2026-05-25', '13:30:00', '14:00:00', 'TEST - Consultation 2', 1, 12, NULL),
(397, '2026-05-25', '14:00:00', '14:30:00', 'TEST - Consultation 3', 1, 12, NULL),
(398, '2026-05-25', '14:30:00', '15:00:00', 'TEST - Consultation 4', 1, 12, NULL),
(399, '2026-05-25', '15:00:00', '15:30:00', 'TEST - Consultation 5', 1, 12, NULL);

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `fiche_patient`
--
ALTER TABLE `fiche_patient`
  ADD PRIMARY KEY (`idfiche`),
  ADD UNIQUE KEY `idPatient` (`idpatient`),
  ADD UNIQUE KEY `uq_dossier_patient` (`idpatient`),
  ADD KEY `fk_dossier_personnel` (`idpersonnel`);

--
-- Index pour la table `patient`
--
ALTER TABLE `patient`
  ADD PRIMARY KEY (`id_patient`);

--
-- Index pour la table `personnel_de_sante`
--
ALTER TABLE `personnel_de_sante`
  ADD PRIMARY KEY (`id_personnel`);

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
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `fiche_patient`
--
ALTER TABLE `fiche_patient`
  MODIFY `idfiche` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `patient`
--
ALTER TABLE `patient`
  MODIFY `id_patient` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=52;

--
-- AUTO_INCREMENT pour la table `personnel_de_sante`
--
ALTER TABLE `personnel_de_sante`
  MODIFY `id_personnel` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=40;

--
-- AUTO_INCREMENT pour la table `planning`
--
ALTER TABLE `planning`
  MODIFY `idPlanning` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- AUTO_INCREMENT pour la table `rdv`
--
ALTER TABLE `rdv`
  MODIFY `idRDV` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=400;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `fiche_patient`
--
ALTER TABLE `fiche_patient`
  ADD CONSTRAINT `fk_dossier_patient` FOREIGN KEY (`idPatient`) REFERENCES `patient` (`id_patient`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_dossier_personnel` FOREIGN KEY (`idpersonnel`) REFERENCES `personnel_de_sante` (`id_personnel`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Contraintes pour la table `planning`
--
ALTER TABLE `planning`
  ADD CONSTRAINT `fk_planning_personnel` FOREIGN KEY (`idPersonnel`) REFERENCES `personnel_de_sante` (`id_personnel`) ON UPDATE CASCADE;

--
-- Contraintes pour la table `rdv`
--
ALTER TABLE `rdv`
  ADD CONSTRAINT `fk_rdv_patient` FOREIGN KEY (`idPatient`) REFERENCES `patient` (`id_patient`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_rdv_personnel` FOREIGN KEY (`idPersonnel`) REFERENCES `personnel_de_sante` (`id_personnel`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
