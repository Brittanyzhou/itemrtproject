DELIMITER $$

DROP TRIGGER IF EXISTS `longquestion_updates`$$
CREATE
	TRIGGER `longquestion_updates` After insert
	ON `itemrtdb_longquestion`
	FOR EACH ROW BEGIN

		SET @changesummary = CONCAT('LongQuestion ', NEW.id);
    
		INSERT INTO changes (data) VALUES (@changesummary);		
    END$
DELIMITER ;


DELIMITER $$


DROP TRIGGER IF EXISTS `solution1_updates`$$
CREATE
	TRIGGER `solution1_updates` After insert
	ON `itemrtdb_solution1`
	FOR EACH ROW BEGIN

		SET @changesummary = CONCAT('Solution1 for question ', NEW.question_id);
    
		INSERT INTO changes (data) VALUES (@changesummary);		
    END$$

DELIMITER ;


DELIMITER $$

DROP TRIGGER IF EXISTS `programcase_updates`$$
CREATE
	TRIGGER `programcase_updates` After insert
	ON `itemrtdb_programcase`
	FOR EACH ROW BEGIN

		SET @changesummary = CONCAT('programcase for question ', NEW.question_id);
    
		INSERT INTO changes (data) VALUES (@changesummary);		
    END$$

DELIMITER ;



