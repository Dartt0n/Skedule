# DATABASE TABLES INFO
## MAIN TABLE
```mysql
CREATE TABLE lessons (
  id INT NOT NULL AUTO_INCREMENT,
  lesson_number TINYINT NOT NULL,
  day_of_week TINYINT NOT NULL,
  subject VARCHAR(100) NOT NULL,
  teacher VARCHAR(100) NULL,
  cabinet VARCHAR(50) NOT NULL,
  subclass VARCHAR(15) NOT NULL,
  PRIMARY KEY (id)
);
```
## TELEGRAM USERS TABLE
```mysql
CREATE TABLE users (
  id INT NOT NULL AUTO_INCREMENT,
  is_student BOOL NOT NULL,
  subclass VARCHAR(15) NULL,
  teacher_name VARCHAR(50) NULL,
  status TINYINT NOT NULL,
  requests_left TINYINT NOT NULL,
  last_payment_datetime DATETIME NOT NULL,
  subscription_until DATETIME NOT NULL,
  PRIMARY KEY (id)
)
```
