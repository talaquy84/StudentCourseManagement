CREATE TRIGGER trigger_add_student ON STUDENT_TAKES_COURSE AFTER INSERT 
AS
BEGIN
	UPDATE COURSE_SECTION
	SET COURSE_SECTION.Occupied_Seats = COURSE_SECTION.Occupied_Seats + 1
	WHERE COURSE_SECTION.Course_ID in (select Course_ID from inserted) 
	AND COURSE_SECTION.Department_ID in (select Department_ID from inserted)
	AND COURSE_SECTION.Section_ID in (select Section_ID from inserted)
END;

