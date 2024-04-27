-- ADT Project - Restaurant Ratings Database
-- Code Owners - Sarfaraj, Jayanand Hiremath, & Rishikesh Kakde

-- Creating the database restaurant ratings
-- Code Author: Jayanand Hiremath

DROP DATABASE IF EXISTS restaurant_ratings;

CREATE DATABASE restaurant_ratings;

-- Selecting the database restaurant ratings
-- Code Author: Jayanand Hiremath

USE restaurant_ratings;

-- Creating restaurants table with compatible data types and required constraints
-- Code Author: Jayanand Hiremath

CREATE TABLE `restaurants` (
  `placeID` int(15) unsigned NOT NULL AUTO_INCREMENT,
  `name` text NOT NULL,
  `address` text NOT NULL,
  `city` text NOT NULL,
  `state` text NOT NULL,
  `country` text NOT NULL,
  PRIMARY KEY (`placeID`)
) ENGINE=InnoDB AUTO_INCREMENT=135109 DEFAULT CHARSET=utf8;

-- Creating restaurant_services table with compatible data types and required constraints
-- Code Author: Jayanand Hiremath

CREATE TABLE `restaurant_services` (
  `placeID` int(15) unsigned NOT NULL,
  `alcohol` text,
  `smoking_area` text,
  `dress_code` text,
  `accessibility` text,
  `price` text,
  `Rambience` text,
  `franchise` text,
  `area` text,
  `cuisines` text,
  PRIMARY KEY (`placeID`),
  CONSTRAINT `restaurant_services_ibfk_1` FOREIGN KEY (`placeID`) REFERENCES `restaurants` (`placeID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Creating users table with compatible data types and required constraints
-- Code Author: Jayanand Hiremath

CREATE TABLE `users` (
  `userID` int(15) unsigned NOT NULL AUTO_INCREMENT,
  `first_name` text NOT NULL,
  `last_name` text NOT NULL,
  `phone_number` varchar(10) NOT NULL,
  `email` text NOT NULL,
  `password` text NOT NULL,
  `marital_status` text NOT NULL,
  `hijos` text,
  `birth_year` int(4) NOT NULL,
  `personality` text,
  `religion` text,
  `color` text,
  `weight` int(11) DEFAULT NULL,
  `height` double DEFAULT NULL,
  PRIMARY KEY (`userID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Creating user_preferences table with compatible data types and required constraints
-- Code Author: Jayanand Hiremath

CREATE TABLE `user_preferences` (
  `userID` int(15) unsigned NOT NULL AUTO_INCREMENT,
  `smoker` text,
  `drink_level` text,
  `dress_preference` text,
  `ambience` text,
  `activity` text,
  `transport` text,
  `interest` text,
  `budget` text,
  PRIMARY KEY (`userID`),
  CONSTRAINT `user_preferences_ibfk_1` FOREIGN KEY (`userID`) REFERENCES `users` (`userID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Creating ratings table with compatible data types and required constraints
-- Code Author: Jayanand Hiremath

CREATE TABLE `ratings` (
  `ratingID` int AUTO_INCREMENT,
  `userID` int(15) unsigned NOT NULL,
  `placeID` int(15) unsigned NOT NULL,
  `rating` int(2) NOT NULL,
  `food_rating` int(2) NOT NULL,
  `service_rating` int(2) NOT NULL,
  `comments` text,
  PRIMARY KEY (`userID`,`placeID`),
  KEY `ratingID` (`ratingID`),
  CONSTRAINT `ratings_ibfk_1` FOREIGN KEY (`userID`) REFERENCES `users` (`userID`) ON DELETE CASCADE,
  CONSTRAINT `ratings_ibfk_2` FOREIGN KEY (`placeID`) REFERENCES `restaurants` (`placeID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Importing the data into the restaurants table created above
-- Code Author: Jayanand Hiremath

LOAD DATA LOCAL INFILE '/Users/sarfaraj/Desktop/IUB/ADT/Final Project/End Game/data/restaurants.csv' 
INTO TABLE restaurants
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Importing the data into the restaurant_services table created above
-- Code Author: Jayanand Hiremath

LOAD DATA LOCAL INFILE '/Users/sarfaraj/Desktop/IUB/ADT/Final Project/End Game/data/restaurant_services.csv' 
INTO TABLE restaurant_services
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Importing the data into the users table created above
-- Code Author: Jayanand Hiremath

LOAD DATA LOCAL INFILE '/Users/sarfaraj/Desktop/IUB/ADT/Final Project/End Game/data/users.csv' 
INTO TABLE users
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Importing the data into the user_preferences table created above
-- Code Author: Jayanand Hiremath

LOAD DATA LOCAL INFILE '/Users/sarfaraj/Desktop/IUB/ADT/Final Project/End Game/data/user_preferences.csv' 
INTO TABLE user_preferences
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Importing the data into the ratings table created above
-- Code Author: Jayanand Hiremath

LOAD DATA LOCAL INFILE '/Users/sarfaraj/Desktop/IUB/ADT/Final Project/End Game/data/ratings.csv' 
INTO TABLE ratings
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;



-- Queries relevant to the application functionality design

-- Query to display the restaurants' name and address on the main web page.
-- Code Author: Sarfaraj

SELECT name, address, city, state
FROM restaurants;


-- Query to display the details of a specific restaurant like alcohol service, smoking area availability and price category.
-- The placeID used to select the particular restaurant will be passed on from the web page when a user clicks on the chosen restaurant to know more about the offered services.
-- Code Author: Sarfaraj

SELECT name, city, alcohol, smoking_area, dress_code, price, Rambience, area
FROM restaurants NATURAL JOIN restaurant_services
WHERE placeID = 135085;


-- Query to show the preferences of a user which can be updated by the user as and when needed through the profile page.
-- The userID used to filter the users table for showing details of the currently logged in user will be passed from the web page's session variable information.
-- Code Author: Sarfaraj

SELECT hijos, personality, smoker, drink_level, ambience, activity, transport, budget
FROM users NATURAL JOIN user_preferences
WHERE userID = 'U1004';


-- Query to fetch the ratings given to a restaurant along with the individual characteristic details of the users while masking their personal information.
-- The placeID used to select the particular restaurant will be passed on from the web page when a user clicks on the chosen restaurant to analyze its ratings.
-- Code Author: Sarfaraj

SELECT name, address, city, rating, food_rating, service_rating, smoker, drink_level, interest
FROM restaurants NATURAL JOIN ratings NATURAL JOIN user_preferences
WHERE placeID = 135085;

-- Debugging and Enforcing Constraints: Rishikesh Kakde

