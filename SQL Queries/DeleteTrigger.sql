CREATE TRIGGER trigger_delete_student ON STUDENT_TAKES_COURSE AFTER DELETE 
AS
BEGIN
	UPDATE COURSE_SECTION
	SET COURSE_SECTION.Occupied_Seats = COURSE_SECTION.Occupied_Seats - 1
	WHERE COURSE_SECTION.Course_ID in (select Course_ID from deleted) 
	AND COURSE_SECTION.Department_ID in (select Department_ID from deleted)
	AND COURSE_SECTION.Section_ID in (select Section_ID from deleted)
END;

