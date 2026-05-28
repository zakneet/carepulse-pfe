-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le : jeu. 28 mai 2026 à 16:21
-- Version du serveur : 8.4.7
-- Version de PHP : 8.3.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `gestion_des_rendez-vous-3`
--

-- --------------------------------------------------------

--
-- Structure de la table `fiche_patient`
--

DROP TABLE IF EXISTS `fiche_patient`;
CREATE TABLE IF NOT EXISTS `fiche_patient` (
  `idfiche` int NOT NULL AUTO_INCREMENT,
  `idpatient` int NOT NULL,
  `idpersonnel` int DEFAULT NULL,
  `nom` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `prenom` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `age` int DEFAULT NULL,
  `etat_civil` varchar(120) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`idfiche`),
  UNIQUE KEY `idPatient` (`idpatient`),
  UNIQUE KEY `uq_dossier_patient` (`idpatient`),
  KEY `fk_dossier_personnel` (`idpersonnel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `patient`
--

DROP TABLE IF EXISTS `patient`;
CREATE TABLE IF NOT EXISTS `patient` (
  `id_patient` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `prenom` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `telephone` varchar(30) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id_patient`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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

DROP TABLE IF EXISTS `personnel_de_sante`;
CREATE TABLE IF NOT EXISTS `personnel_de_sante` (
  `id_personnel` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `specialite` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `disponibilite` tinyint(1) NOT NULL DEFAULT '1',
  `region` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id_personnel`)
) ENGINE=InnoDB AUTO_INCREMENT=202 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `personnel_de_sante`
--

INSERT INTO `personnel_de_sante` (`id_personnel`, `nom`, `prenom`, `specialite`, `disponibilite`, `region`) VALUES
(1, 'Labidi', 'Meher', 'Pediatre', 1, 'Ariana Ville'),
(2, 'Ben Ali', 'Ali', 'Cardiologie', 1, 'Kasserine'),
(3, 'Zitouni', 'Ali', 'Cardiologie', 1, 'El Hamma'),
(4, 'Ben Ali', 'Nadia', 'Dentaire', 1, 'Kerkennah'),
(5, 'Ayari', 'Amira', 'Médecine générale', 1, 'Manouba'),
(6, 'Cherif', 'Amira', 'Dentaire', 1, 'Sousse (Ryadh/Jawhara)'),
(7, 'Tlili', 'Mehdi', 'Dermatologie', 1, 'Carthage'),
(8, 'Zitouni', 'Anis', 'Cardiologie', 1, 'Djerba'),
(9, 'Zouari', 'Nadia', 'Cardiologie', 1, 'Carthage'),
(10, 'Ayari', 'Kamel', 'Psychiatrie', 1, 'Cité Attadhamon'),
(11, 'Ben Ali', 'Youssef', 'Dermatologie', 1, 'Hammam Lif'),
(12, 'Trabelsi', 'Amine', 'Neurologie', 1, 'Béja'),
(13, 'Baccouche', 'Ali', 'Psychiatrie', 1, 'El Hamma'),
(14, 'Ben Ali', 'Anis', 'Ophtalmologie', 1, 'Sousse (Ryadh/Jawhara)'),
(15, 'Miled', 'Mouna', 'Pédiatrie', 1, 'Gabès'),
(16, 'Zouari', 'Imen', 'Dentaire', 1, 'Béja'),
(17, 'Ayari', 'Ahmed', 'Neurologie', 1, 'Gafsa'),
(18, 'Khemiri', 'Imen', 'Dentaire', 1, 'Ksar Helal'),
(19, 'Oueslati', 'Rim', 'Orthopédie', 1, 'Djerba'),
(20, 'Baccouche', 'Asma', 'Neurologie', 1, 'Msaken'),
(21, 'Miled', 'Mohamed', 'Dermatologie', 1, 'Haffouz'),
(22, 'Ben Ammar', 'Mouna', 'Ophtalmologie', 1, 'Manouba'),
(23, 'Ayari', 'Amira', 'Dentaire', 1, 'Monastir'),
(24, 'Ben Ammar', 'Kamel', 'Psychiatrie', 1, 'Enfidha'),
(25, 'Touati', 'Anis', 'Gynécologie', 1, 'Bardo'),
(26, 'Jaziri', 'Safa', 'Cardiologie', 1, 'El Hamma'),
(27, 'Jemai', 'Leïla', 'Médecine générale', 1, 'Gafsa'),
(28, 'Riahi', 'Mehdi', 'Neurologie', 1, 'Mahrès'),
(29, 'Miled', 'Kamel', 'Médecine générale', 1, 'Ain Drahem'),
(30, 'Haddad', 'Mouna', 'Pédiatrie', 1, 'Mahrès'),
(31, 'Baccouche', 'Walid', 'Dermatologie', 1, 'Mahrès'),
(32, 'Amri', 'Nadia', 'Psychiatrie', 1, 'La Marsa'),
(33, 'Trabelsi', 'Karim', 'Psychiatrie', 1, 'Tebourba'),
(34, 'Trabelsi', 'Ali', 'Gynécologie', 1, 'Siliana'),
(35, 'Mansour', 'Sarra', 'Neurologie', 1, 'Carthage'),
(36, 'Gharbi', 'Yasmine', 'Cardiologie', 1, 'Sakiet Ezzit'),
(37, 'Riahi', 'Hichem', 'Cardiologie', 1, 'Raoued'),
(38, 'Zitouni', 'Ahmed', 'Dentaire', 1, 'Enfidha'),
(39, 'Ben Ammar', 'Rim', 'Neurologie', 1, 'Bardo'),
(40, 'Ayari', 'Ali', 'Psychiatrie', 1, 'La Marsa'),
(41, 'Khemiri', 'Rim', 'Gynécologie', 1, 'Moknine'),
(42, 'Riahi', 'Ahmed', 'Dermatologie', 1, 'Djerba'),
(43, 'Zitouni', 'Youssef', 'Dermatologie', 1, 'Msaken'),
(44, 'Oueslati', 'Mehdi', 'Cardiologie', 1, 'Gabès'),
(45, 'Jemai', 'Mohamed', 'Dentaire', 1, 'Enfidha'),
(46, 'Sassi', 'Amine', 'Dermatologie', 1, 'Métlaoui'),
(47, 'Jemai', 'Anis', 'Ophtalmologie', 1, 'Kasserine'),
(48, 'Khlifi', 'Leïla', 'Dermatologie', 1, 'Mahrès'),
(49, 'Ayari', 'Asma', 'Cardiologie', 1, 'Ain Drahem'),
(50, 'Bouazizi', 'Safa', 'Neurologie', 1, 'Ksar Helal'),
(51, 'Ben Ali', 'Kamel', 'Dermatologie', 1, 'Eljem'),
(52, 'Oueslati', 'Ahmed', 'Gynécologie', 1, 'Mahdia'),
(53, 'Ghannouchi', 'Kamel', 'Psychiatrie', 1, 'Zaghouan'),
(54, 'Zitouni', 'Anis', 'Médecine générale', 1, 'Manouba'),
(55, 'Miled', 'Amira', 'Dentaire', 1, 'Sakiet Ezzit'),
(56, 'Sassi', 'Karim', 'Gynécologie', 1, 'Sakiet Ezzit'),
(57, 'Gharbi', 'Rim', 'Gynécologie', 1, 'Hammamet'),
(58, 'Touati', 'Amira', 'Cardiologie', 1, 'Menzel Bourguiba'),
(59, 'Miled', 'Mehdi', 'Pédiatrie', 1, 'Djerba'),
(60, 'Ayari', 'Ali', 'Neurologie', 1, 'La Marsa'),
(61, 'Miled', 'Youssef', 'Pédiatrie', 1, 'Sakiet Ezzit'),
(62, 'Jaziri', 'Anis', 'Médecine générale', 1, 'Tebourba'),
(63, 'Mansour', 'Safa', 'Pédiatrie', 1, 'Raoued'),
(64, 'Zouari', 'Amira', 'Cardiologie', 1, 'Sousse (Ryadh/Jawhara)'),
(65, 'Sassi', 'Rim', 'Dermatologie', 1, 'Tozeur'),
(66, 'Sassi', 'Karim', 'Psychiatrie', 1, 'Sfax (Ville/Ouest/Sud)'),
(67, 'Ghannouchi', 'Nadia', 'Médecine générale', 1, 'Bizerte Nord'),
(68, 'Tlili', 'Safa', 'Psychiatrie', 1, 'Sousse (Ryadh/Jawhara)'),
(69, 'Khlifi', 'Mehdi', 'Dentaire', 1, 'Tozeur'),
(70, 'Cherif', 'Yasmine', 'Médecine générale', 1, 'Gafsa'),
(71, 'Zouari', 'Yasmine', 'Psychiatrie', 1, 'Sousse (Ryadh/Jawhara)'),
(72, 'Tlili', 'Safa', 'Cardiologie', 1, 'Makther'),
(73, 'Ben Ali', 'Leïla', 'Psychiatrie', 1, 'Msaken'),
(74, 'Oueslati', 'Sarra', 'Gynécologie', 1, 'Hammam Sousse'),
(75, 'Jaziri', 'Anis', 'Psychiatrie', 1, 'Sousse (Ryadh/Jawhara)'),
(76, 'Khemiri', 'Nizar', 'Dermatologie', 1, 'Enfidha'),
(77, 'Ben Ali', 'Sarra', 'Neurologie', 1, 'Sakiet Ezzit'),
(78, 'Mansour', 'Walid', 'Dentaire', 1, 'Enfidha'),
(79, 'Riahi', 'Youssef', 'Ophtalmologie', 1, 'Radès'),
(80, 'Mansour', 'Asma', 'Orthopédie', 1, 'Fahs'),
(81, 'Ben Ali', 'Nadia', 'Médecine générale', 1, 'Testour'),
(82, 'Khlifi', 'Amine', 'Cardiologie', 1, 'Eljem'),
(83, 'Touati', 'Anis', 'Gynécologie', 1, 'Kelibia'),
(84, 'Jemai', 'Fatma', 'Ophtalmologie', 1, 'El Hamma'),
(85, 'Amri', 'Safa', 'Orthopédie', 1, 'Hammam Sousse'),
(86, 'Mabrouk', 'Hichem', 'Psychiatrie', 1, 'Sakiet Ezzit'),
(87, 'Touati', 'Ali', 'Gynécologie', 1, 'Tataouine'),
(88, 'Ben Ali', 'Walid', 'Cardiologie', 1, 'Bardo'),
(89, 'Zitouni', 'Salma', 'Psychiatrie', 1, 'Haffouz'),
(90, 'Cherif', 'Mouna', 'Dentaire', 1, 'La Marsa'),
(91, 'Baccouche', 'Rim', 'Dermatologie', 1, 'Fahs'),
(92, 'Riahi', 'Mehdi', 'Orthopédie', 1, 'Zarzis'),
(93, 'Ben Ali', 'Fatma', 'Dentaire', 1, 'Gafsa'),
(94, 'Zouari', 'Anis', 'Ophtalmologie', 1, 'Kairouan'),
(95, 'Touati', 'Ahmed', 'Gynécologie', 1, 'Haffouz'),
(96, 'Khlifi', 'Mehdi', 'Cardiologie', 1, 'Zarzis'),
(97, 'Mansour', 'Amine', 'Dermatologie', 1, 'Moknine'),
(98, 'Riahi', 'Sarra', 'Médecine générale', 1, 'Jendouba'),
(99, 'Trabelsi', 'Mouna', 'Dermatologie', 1, 'Tebourba'),
(100, 'Ben Ali', 'Ali', 'Dentaire', 1, 'Manouba'),
(101, 'Khemiri', 'Kamel', 'Dentaire', 1, 'El Hamma'),
(102, 'Jaziri', 'Amine', 'Psychiatrie', 1, 'Zarzis'),
(103, 'Amri', 'Mehdi', 'Ophtalmologie', 1, 'Agareb'),
(104, 'Ben Ammar', 'Sami', 'Psychiatrie', 1, 'Tabarka'),
(105, 'Sassi', 'Rim', 'Ophtalmologie', 1, 'Thala'),
(106, 'Jaziri', 'Asma', 'Cardiologie', 1, 'Ain Drahem'),
(107, 'Khlifi', 'Sarra', 'Psychiatrie', 1, 'Radès'),
(108, 'Ben Ali', 'Safa', 'Neurologie', 1, 'Regueb'),
(109, 'Jemai', 'Sarra', 'Dentaire', 1, 'Hammam Sousse'),
(110, 'Cherif', 'Mouna', 'Dermatologie', 1, 'Tebourba'),
(111, 'Jaziri', 'Mehdi', 'Médecine générale', 1, 'Kelibia'),
(112, 'Jaziri', 'Youssef', 'Neurologie', 1, 'Tozeur'),
(113, 'Trabelsi', 'Ahmed', 'Neurologie', 1, 'Kef'),
(114, 'Ayari', 'Rim', 'Médecine générale', 1, 'La Marsa'),
(115, 'Mabrouk', 'Kamel', 'Neurologie', 1, 'Makther'),
(116, 'Haddad', 'Walid', 'Ophtalmologie', 1, 'Radès'),
(117, 'Haddad', 'Salma', 'Gynécologie', 1, 'Nabeul'),
(118, 'Miled', 'Ahmed', 'Gynécologie', 1, 'Sbitla'),
(119, 'Cherif', 'Fatma', 'Pédiatrie', 1, 'Moknine'),
(120, 'Mabrouk', 'Asma', 'Neurologie', 1, 'Monastir'),
(121, 'Sassi', 'Nizar', 'Neurologie', 1, 'Soukra'),
(122, 'Baccouche', 'Mohamed', 'Ophtalmologie', 1, 'Hammam Lif'),
(123, 'Baccouche', 'Kamel', 'Cardiologie', 1, 'Hammam Lif'),
(124, 'Gharbi', 'Fatma', 'Gynécologie', 1, 'Kerkennah'),
(125, 'Zouari', 'Ahmed', 'Psychiatrie', 1, 'Agareb'),
(126, 'Riahi', 'Amine', 'Gynécologie', 1, 'Nabeul'),
(127, 'Khlifi', 'Mohamed', 'Cardiologie', 1, 'Sakiet Ezzit'),
(128, 'Khemiri', 'Sami', 'Orthopédie', 1, 'Dahmani'),
(129, 'Ayari', 'Kamel', 'Cardiologie', 1, 'Kasserine'),
(130, 'Oueslati', 'Nizar', 'Neurologie', 1, 'Oued Ellil'),
(131, 'Zitouni', 'Karim', 'Psychiatrie', 1, 'Hammam Lif'),
(132, 'Trabelsi', 'Walid', 'Cardiologie', 1, 'Sousse (Ryadh/Jawhara)'),
(133, 'Ben Ali', 'Sami', 'Dermatologie', 1, 'Hammamet'),
(134, 'Amri', 'Sarra', 'Pédiatrie', 1, 'Dahmani'),
(135, 'Khlifi', 'Mohamed', 'Médecine générale', 1, 'Mornag'),
(136, 'Gharbi', 'Fatma', 'Cardiologie', 1, 'Hammam Lif'),
(137, 'Oueslati', 'Mohamed', 'Gynécologie', 1, 'Mahdia'),
(138, 'Jaziri', 'Mehdi', 'Pédiatrie', 1, 'Sbitla'),
(139, 'Zitouni', 'Amira', 'Dermatologie', 1, 'Raoued'),
(140, 'Oueslati', 'Ahmed', 'Ophtalmologie', 1, 'Fahs'),
(141, 'Oueslati', 'Nadia', 'Gynécologie', 1, 'Sbitla'),
(142, 'Mabrouk', 'Mohamed', 'Médecine générale', 1, 'Kerkennah'),
(143, 'Ben Ammar', 'Sami', 'Pédiatrie', 1, 'Ras Jebel'),
(144, 'Mabrouk', 'Karim', 'Dentaire', 1, 'Sbitla'),
(145, 'Trabelsi', 'Yasmine', 'Dentaire', 1, 'Bizerte Nord'),
(146, 'Zitouni', 'Rim', 'Gynécologie', 1, 'Msaken'),
(147, 'Jemai', 'Karim', 'Neurologie', 1, 'Djerba'),
(148, 'Ben Ali', 'Yasmine', 'Ophtalmologie', 1, 'Hammam Sousse'),
(149, 'Ayari', 'Hichem', 'Médecine générale', 1, 'Thala'),
(150, 'Riahi', 'Asma', 'Médecine générale', 1, 'Kef'),
(151, 'Haddad', 'Youssef', 'Neurologie', 1, 'Haffouz'),
(152, 'Bouazizi', 'Yasmine', 'Gynécologie', 1, 'Mahdia'),
(153, 'Gharbi', 'Kamel', 'Orthopédie', 1, 'Tataouine'),
(154, 'Ghannouchi', 'Rim', 'Pédiatrie', 1, 'Monastir'),
(155, 'Jemai', 'Salma', 'Cardiologie', 1, 'Tebourba'),
(156, 'Jaziri', 'Kamel', 'Gynécologie', 1, 'Ksar Helal'),
(157, 'Khemiri', 'Mouna', 'Ophtalmologie', 1, 'Kef'),
(158, 'Sassi', 'Rim', 'Dermatologie', 1, 'Enfidha'),
(159, 'Trabelsi', 'Ali', 'Médecine générale', 1, 'Regueb'),
(160, 'Jemai', 'Salma', 'Dermatologie', 1, 'Kasserine'),
(161, 'Jaziri', 'Leïla', 'Dermatologie', 1, 'Cité Attadhamon'),
(162, 'Cherif', 'Hichem', 'Orthopédie', 1, 'Cité Attadhamon'),
(163, 'Mansour', 'Sami', 'Cardiologie', 1, 'Msaken'),
(164, 'Ben Ali', 'Ali', 'Gynécologie', 1, 'Hammam Lif'),
(165, 'Mansour', 'Sarra', 'Cardiologie', 1, 'Tabarka'),
(166, 'Mansour', 'Asma', 'Dentaire', 1, 'Zarzis'),
(167, 'Gharbi', 'Salma', 'Dentaire', 1, 'Radès'),
(168, 'Ayari', 'Amine', 'Ophtalmologie', 1, 'Mahdia'),
(169, 'Mabrouk', 'Ahmed', 'Cardiologie', 1, 'El Hamma'),
(170, 'Gharbi', 'Yasmine', 'Cardiologie', 1, 'Tozeur'),
(171, 'Khemiri', 'Fatma', 'Neurologie', 1, 'Gabès'),
(172, 'Riahi', 'Salma', 'Dermatologie', 1, 'Gabès'),
(173, 'Cherif', 'Nadia', 'Médecine générale', 1, 'Moknine'),
(174, 'Jaziri', 'Mehdi', 'Médecine générale', 1, 'Thala'),
(175, 'Zitouni', 'Karim', 'Cardiologie', 1, 'Oued Ellil'),
(176, 'Sassi', 'Ali', 'Neurologie', 1, 'Manouba'),
(177, 'Khemiri', 'Nadia', 'Ophtalmologie', 1, 'Soukra'),
(178, 'Trabelsi', 'Sami', 'Orthopédie', 1, 'Monastir'),
(179, 'Mansour', 'Safa', 'Médecine générale', 1, 'Ain Drahem'),
(180, 'Oueslati', 'Rim', 'Pédiatrie', 1, 'Djerba'),
(181, 'Haddad', 'Amine', 'Orthopédie', 1, 'Kerkennah'),
(182, 'Oueslati', 'Amira', 'Médecine générale', 1, 'Dahmani'),
(183, 'Cherif', 'Amine', 'Ophtalmologie', 1, 'Djerba'),
(184, 'Jaziri', 'Sarra', 'Pédiatrie', 1, 'Sfax (Ville/Ouest/Sud)'),
(185, 'Ben Ali', 'Sarra', 'Cardiologie', 1, 'Zarzis'),
(186, 'Cherif', 'Walid', 'Médecine générale', 1, 'Kerkennah'),
(187, 'Mabrouk', 'Youssef', 'Psychiatrie', 1, 'Testour'),
(188, 'Jaziri', 'Nadia', 'Orthopédie', 1, 'Kairouan'),
(189, 'Zitouni', 'Hichem', 'Dentaire', 1, 'Nefta'),
(190, 'Riahi', 'Youssef', 'Pédiatrie', 1, 'Raoued'),
(191, 'Amri', 'Mohamed', 'Dentaire', 1, 'Tozeur'),
(192, 'Haddad', 'Hichem', 'Médecine générale', 1, 'Nabeul'),
(193, 'Oueslati', 'Mohamed', 'Dermatologie', 1, 'Médenine'),
(194, 'Jemai', 'Asma', 'Cardiologie', 1, 'Kébili'),
(195, 'Tlili', 'Mohamed', 'Neurologie', 1, 'Thala'),
(196, 'Ghannouchi', 'Mouna', 'Orthopédie', 1, 'Enfidha'),
(197, 'Ayari', 'Salma', 'Dermatologie', 1, 'Kef'),
(198, 'Oueslati', 'Nadia', 'Neurologie', 1, 'Dahmani'),
(199, 'Oueslati', 'Sami', 'Cardiologie', 1, 'La Marsa'),
(200, 'Jaziri', 'Karim', 'Dermatologie', 1, 'Sbitla'),
(201, 'Tlili', 'Salma', 'Orthopédie', 1, 'Zaghouan');

-- --------------------------------------------------------

--
-- Structure de la table `planning`
--

DROP TABLE IF EXISTS `planning`;
CREATE TABLE IF NOT EXISTS `planning` (
  `idPlanning` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `idPersonnel` int DEFAULT NULL,
  `heureDebut` time NOT NULL,
  `heureFin` time NOT NULL,
  `duree_creneau` int NOT NULL DEFAULT '30',
  PRIMARY KEY (`idPlanning`),
  KEY `fk_planning_personnel` (`idPersonnel`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `rdv`
--

DROP TABLE IF EXISTS `rdv`;
CREATE TABLE IF NOT EXISTS `rdv` (
  `idRDV` int NOT NULL AUTO_INCREMENT,
  `dateRDV` date NOT NULL,
  `heureDebut` time NOT NULL,
  `heureFin` time NOT NULL,
  `motifConsultation` text COLLATE utf8mb4_general_ci NOT NULL,
  `idPatient` int DEFAULT NULL,
  `idPersonnel` int DEFAULT NULL,
  `agePatient` int DEFAULT NULL,
  PRIMARY KEY (`idRDV`),
  KEY `fk_rdv_patient` (`idPatient`),
  KEY `fk_rdv_personnel` (`idPersonnel`)
) ENGINE=InnoDB AUTO_INCREMENT=400 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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

-- --------------------------------------------------------

--
-- Structure de la table `user`
--

DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telephone` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cin` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `specialite` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `disponibilite` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `access_code` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `access_code` (`access_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `fiche_patient`
--
ALTER TABLE `fiche_patient`
  ADD CONSTRAINT `fk_dossier_patient` FOREIGN KEY (`idpatient`) REFERENCES `patient` (`id_patient`) ON DELETE CASCADE ON UPDATE CASCADE,
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
