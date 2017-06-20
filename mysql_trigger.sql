DELIMITER @@
 
CREATE TRIGGER Test_Trigger 
AFTER INSERT ON ticket 
FOR EACH ROW 
BEGIN
 DECLARE cmd CHAR(255);
 DECLARE result int(10);
 SET cmd=CONCAT('python /tmp/call_bot.py ', NEW.ref);
 SET result = sys_eval(cmd);
END;
@@
DELIMITER ;
