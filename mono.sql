
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données :  `mono`
--

-- --------------------------------------------------------

--
-- Structure de la table `CONVERSATIONS_IPV4`
--

CREATE TABLE IF NOT EXISTS `CONVERSATIONS_IPV4` (
  `id_conversation_ipv4` int(11) NOT NULL AUTO_INCREMENT,
  `id_session` int(11) NOT NULL,
  `ip_a` varchar(100) NOT NULL,
  `ip_b` varchar(100) NOT NULL,
  `bytes` int(11) NOT NULL DEFAULT '0',
  `rel_start` double NOT NULL DEFAULT '0',
  `duration` double NOT NULL DEFAULT '0',
  `packets` int(11) NOT NULL DEFAULT '0',
  `packets_a_b` int(11) NOT NULL DEFAULT '0',
  `packets_b_a` int(11) DEFAULT '0',
  `bytes_a_b` int(11) NOT NULL DEFAULT '0',
  `bytes_b_a` int(11) NOT NULL DEFAULT '0',
  `selected` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_conversation_ipv4`),
  KEY `id_session` (`id_session`)
) ENGINE=InnoDB AUTO_INCREMENT=1504 DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `CONVERSATIONS_MITM`
--

CREATE TABLE IF NOT EXISTS `CONVERSATIONS_MITM` (
  `id_conversation_mitm` int(11) NOT NULL AUTO_INCREMENT,
  `id_session` int(11) NOT NULL,
  `ip_a` varchar(100) NOT NULL,
  `port_a` int(11) NOT NULL DEFAULT '0',
  `ip_b` varchar(100) NOT NULL,
  `port_b` int(11) NOT NULL DEFAULT '0',
  `bytes` int(11) NOT NULL DEFAULT '0',
  `rel_start` double NOT NULL DEFAULT '0',
  `duration` double NOT NULL DEFAULT '0',
  `packets` int(11) NOT NULL DEFAULT '0',
  `packets_a_b` int(11) NOT NULL DEFAULT '0',
  `packets_b_a` int(11) DEFAULT '0',
  `bytes_a_b` int(11) NOT NULL DEFAULT '0',
  `bytes_b_a` int(11) NOT NULL DEFAULT '0',
  `selected` int(11) NOT NULL DEFAULT '0',
  `decrypted` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_conversation_mitm`),
  KEY `id_session` (`id_session`)
) ENGINE=InnoDB AUTO_INCREMENT=2291 DEFAULT CHARSET=utf8mb4;



-- --------------------------------------------------------

--
-- Structure de la table `CONVERSATIONS_TCP`
--

CREATE TABLE IF NOT EXISTS `CONVERSATIONS_TCP` (
  `id_conversation_tcp` int(11) NOT NULL AUTO_INCREMENT,
  `id_session` int(11) NOT NULL,
  `ip_a` varchar(100) NOT NULL,
  `port_a` int(11) NOT NULL DEFAULT '0',
  `ip_b` varchar(100) NOT NULL,
  `port_b` int(11) NOT NULL DEFAULT '0',
  `bytes` int(11) NOT NULL DEFAULT '0',
  `rel_start` double NOT NULL DEFAULT '0',
  `duration` double NOT NULL DEFAULT '0',
  `packets` int(11) NOT NULL DEFAULT '0',
  `packets_a_b` int(11) NOT NULL DEFAULT '0',
  `packets_b_a` int(11) DEFAULT '0',
  `bytes_a_b` int(11) NOT NULL DEFAULT '0',
  `bytes_b_a` int(11) NOT NULL DEFAULT '0',
  `selected` int(11) NOT NULL DEFAULT '0',
  `decrypted` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_conversation_tcp`),
  KEY `id_session` (`id_session`)
) ENGINE=InnoDB AUTO_INCREMENT=3587 DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `CONVERSATIONS_UDP`
--

CREATE TABLE IF NOT EXISTS `CONVERSATIONS_UDP` (
  `id_conversation_udp` int(11) NOT NULL AUTO_INCREMENT,
  `id_session` int(11) NOT NULL,
  `ip_a` varchar(100) NOT NULL,
  `port_a` int(11) NOT NULL DEFAULT '0',
  `ip_b` varchar(100) NOT NULL,
  `port_b` int(11) NOT NULL DEFAULT '0',
  `bytes` int(11) NOT NULL DEFAULT '0',
  `rel_start` double NOT NULL DEFAULT '0',
  `duration` double NOT NULL DEFAULT '0',
  `packets` int(11) NOT NULL DEFAULT '0',
  `packets_a_b` int(11) NOT NULL DEFAULT '0',
  `packets_b_a` int(11) DEFAULT '0',
  `bytes_a_b` int(11) NOT NULL DEFAULT '0',
  `bytes_b_a` int(11) NOT NULL DEFAULT '0',
  `selected` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_conversation_udp`),
  KEY `id_session` (`id_session`)
) ENGINE=InnoDB AUTO_INCREMENT=2170 DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `PACKETS`
--

CREATE TABLE IF NOT EXISTS `PACKETS` (
  `id_packet` int(11) NOT NULL AUTO_INCREMENT,
  `packet` mediumblob NOT NULL,
  `time` double NOT NULL DEFAULT '0',
  `class_name` varchar(1000) CHARACTER SET utf8 COLLATE utf8_estonian_ci NOT NULL,
  `module_name` varchar(1000) CHARACTER SET utf8 COLLATE utf8_estonian_ci NOT NULL,
  `id_session` int(11) NOT NULL DEFAULT '0',
  `ip_src` varchar(100) NOT NULL DEFAULT '0.0.0.0',
  `ip_dst` varchar(100) NOT NULL DEFAULT '0.0.0.0',
  `port_src` int(11) NOT NULL DEFAULT '0',
  `port_dst` int(11) NOT NULL DEFAULT '0',
  `l4_proto_number` int(11) NOT NULL DEFAULT '0',
  `l4_proto` varchar(100) NOT NULL DEFAULT '?',
  `packet_length` int(11) DEFAULT '0',
  `l5_proto` varchar(100) NOT NULL DEFAULT '?',
  `selected` int(11) NOT NULL DEFAULT '0',
  `domain` varchar(1000) NOT NULL DEFAULT '?',
  `decrypted` int(11) NOT NULL DEFAULT '0',
  `constructor` text NOT NULL,
  PRIMARY KEY (`id_packet`),
  KEY `id_session` (`id_session`)
) ENGINE=InnoDB AUTO_INCREMENT=103988 DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `PACKETS_CONVERSATIONS`
--

CREATE TABLE IF NOT EXISTS `PACKETS_CONVERSATIONS` (
  `id_pc` int(11) NOT NULL AUTO_INCREMENT,
  `id_packet` int(11) NOT NULL,
  `id_conversation` int(11) NOT NULL,
  `conversation_type` int(11) NOT NULL,
  `id_session` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_pc`),
  KEY `id_packet` (`id_packet`),
  KEY `id_conversation` (`id_conversation`)
) ENGINE=InnoDB AUTO_INCREMENT=179250 DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `PARAMS`
--

CREATE TABLE IF NOT EXISTS `PARAMS` (
  `id_param` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL DEFAULT '',
  `value_int` int(11) NOT NULL,
  `value_str` varchar(1000) NOT NULL,
  PRIMARY KEY (`id_param`),
  KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;

--
-- Contenu de la table `PARAMS`
--

INSERT INTO `PARAMS` (`id_param`, `name`, `value_int`, `value_str`) VALUES
(1, 'decrypting', 0, ''),
(2, 'recording', 0, ''),
(3, 'id_session', 0, '');

-- --------------------------------------------------------

--
-- Structure de la table `SESSIONS`
--

CREATE TABLE IF NOT EXISTS `SESSIONS` (
  `id_session` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(10000) CHARACTER SET utf8 COLLATE utf8_estonian_ci NOT NULL DEFAULT 'Session',
  `iface` varchar(100) CHARACTER SET utf8 COLLATE utf8_estonian_ci NOT NULL DEFAULT 'None',
  `date` varchar(200) CHARACTER SET utf8 COLLATE utf8_estonian_ci NOT NULL,
  PRIMARY KEY (`id_session`)
) ENGINE=InnoDB AUTO_INCREMENT=239 DEFAULT CHARSET=utf8mb4;

