CREATE OR REPLACE FUNCTION factoriel(n NUMBER)
RETURN NUMBER
IS
  f NUMBER := 1;
BEGIN
  FOR i IN 1..n LOOP
    f := f * i;
  END LOOP;
  RETURN f;
END;
/
SHOW ERRORS;

-- Programme principal
DECLARE
  res NUMBER;
BEGIN
  res := factoriel(10);
  DBMS_OUTPUT.PUT_LINE('Le factoriel de 10 est : ' || res);
END;
/



















