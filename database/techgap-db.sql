-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: techgap
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `courses` (
  `course_id` int NOT NULL AUTO_INCREMENT,
  `course_code` varchar(20) NOT NULL,
  `course_name` varchar(100) NOT NULL,
  `description` text,
  `department` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

LOCK TABLES `courses` WRITE;
/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courseskills`
--

DROP TABLE IF EXISTS `courseskills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `courseskills` (
  `course_id` int NOT NULL,
  `skill_id` int NOT NULL,
  `relevance_level` tinyint DEFAULT NULL,
  PRIMARY KEY (`course_id`,`skill_id`),
  KEY `skill_id` (`skill_id`),
  CONSTRAINT `courseskills_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE,
  CONSTRAINT `courseskills_ibfk_2` FOREIGN KEY (`skill_id`) REFERENCES `skills` (`skill_id`) ON DELETE CASCADE,
  CONSTRAINT `courseskills_chk_1` CHECK ((`relevance_level` between 1 and 5))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courseskills`
--

LOCK TABLES `courseskills` WRITE;
/*!40000 ALTER TABLE `courseskills` DISABLE KEYS */;
/*!40000 ALTER TABLE `courseskills` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gapanalysis`
--

DROP TABLE IF EXISTS `gapanalysis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gapanalysis` (
  `report_id` int NOT NULL AUTO_INCREMENT,
  `course_id` int DEFAULT NULL,
  `missing_skill_id` int DEFAULT NULL,
  `recommendation` text,
  `date_generated` date DEFAULT (curdate()),
  PRIMARY KEY (`report_id`),
  KEY `course_id` (`course_id`),
  KEY `missing_skill_id` (`missing_skill_id`),
  CONSTRAINT `gapanalysis_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE,
  CONSTRAINT `gapanalysis_ibfk_2` FOREIGN KEY (`missing_skill_id`) REFERENCES `skills` (`skill_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gapanalysis`
--

LOCK TABLES `gapanalysis` WRITE;
/*!40000 ALTER TABLE `gapanalysis` DISABLE KEYS */;
/*!40000 ALTER TABLE `gapanalysis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jobpostings`
--

DROP TABLE IF EXISTS `jobpostings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jobpostings` (
  `job_id` int NOT NULL AUTO_INCREMENT,
  `job_title` varchar(100) NOT NULL,
  `company` varchar(100) DEFAULT NULL,
  `description` text NOT NULL,
  `source` varchar(50) DEFAULT NULL,
  `date_posted` date DEFAULT NULL,
  PRIMARY KEY (`job_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jobpostings`
--

LOCK TABLES `jobpostings` WRITE;
/*!40000 ALTER TABLE `jobpostings` DISABLE KEYS */;
/*!40000 ALTER TABLE `jobpostings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jobskills`
--

DROP TABLE IF EXISTS `jobskills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jobskills` (
  `job_id` int NOT NULL,
  `skill_id` int NOT NULL,
  `importance_level` tinyint DEFAULT NULL,
  PRIMARY KEY (`job_id`,`skill_id`),
  KEY `skill_id` (`skill_id`),
  CONSTRAINT `jobskills_ibfk_1` FOREIGN KEY (`job_id`) REFERENCES `jobpostings` (`job_id`) ON DELETE CASCADE,
  CONSTRAINT `jobskills_ibfk_2` FOREIGN KEY (`skill_id`) REFERENCES `skills` (`skill_id`) ON DELETE CASCADE,
  CONSTRAINT `jobskills_chk_1` CHECK ((`importance_level` between 1 and 5))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jobskills`
--

LOCK TABLES `jobskills` WRITE;
/*!40000 ALTER TABLE `jobskills` DISABLE KEYS */;
/*!40000 ALTER TABLE `jobskills` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `skills`
--

DROP TABLE IF EXISTS `skills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `skills` (
  `skill_id` int NOT NULL AUTO_INCREMENT,
  `skill_name` varchar(100) NOT NULL,
  `category` varchar(50) NOT NULL,
  PRIMARY KEY (`skill_id`),
  UNIQUE KEY `skill_name` (`skill_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `skills`
--

LOCK TABLES `skills` WRITE;
/*!40000 ALTER TABLE `skills` DISABLE KEYS */;
/*!40000 ALTER TABLE `skills` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-23 19:17:04
