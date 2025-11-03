CREATE OR REPLACE FUNCTION factoriel(n NUMBER)
RETURN NUMBER IS
  f NUMBER := 1;
BEGIN
  IF n < 0 THEN
    RETURN NULL;  -- pas de factoriel négatif
  END IF;
  
  FOR i IN 1..n LOOP
    f := f * i;
  END LOOP;
  
  RETURN f;
END;
/

--Programme pour afficher le factoriel(10)
SET SERVEROUTPUT ON;

DECLARE
  res NUMBER;
BEGIN
  res := factoriel(10);
  DBMS_OUTPUT.PUT_LINE('Factoriel(10) = ' || res);
END;
/


--Factorielle d’une valeur donnée par l’utilisateur
SET SERVEROUTPUT ON;

DECLARE
  n NUMBER;
  res NUMBER;
BEGIN
  n := &valeur; -- demande une valeur à l’utilisateur
  res := factoriel(n);
  DBMS_OUTPUT.PUT_LINE('Factoriel(' || n || ') = ' || res);
END;
/

--Vérifier si une date tombe le week-end (Vendredi / Samedi)
SET SERVEROUTPUT ON;

DECLARE
  d DATE := TO_DATE('&date', 'DD/MM/YYYY');
  jour VARCHAR2(20);
BEGIN
  jour := TO_CHAR(d, 'DAY', 'NLS_DATE_LANGUAGE=FRENCH');

  IF TRIM(jour) IN ('VENDREDI', 'SAMEDI') THEN
    DBMS_OUTPUT.PUT_LINE('C’est le week-end (' || jour || ')');
  ELSE
    DBMS_OUTPUT.PUT_LINE('Ce n’est pas le week-end (' || jour || ')');
  END IF;
END;
/

--Vérifier si un caractère est une lettre ou un chiffre
SET SERVEROUTPUT ON;

DECLARE
  c CHAR(1) := '&car';
BEGIN
  IF c BETWEEN '0' AND '9' THEN
    DBMS_OUTPUT.PUT_LINE('C’est un chiffre.');
  ELSIF UPPER(c) BETWEEN 'A' AND 'Z' THEN
    DBMS_OUTPUT.PUT_LINE('C’est une lettre.');
  ELSE
    DBMS_OUTPUT.PUT_LINE('Ni lettre ni chiffre.');
  END IF;
END;
/


--Générer une exception division par zéro
SET SERVEROUTPUT ON;

DECLARE
  a NUMBER := 10;
  b NUMBER := 0;
  c NUMBER;
BEGIN
  c := a / b;  -- division par zéro
  DBMS_OUTPUT.PUT_LINE('Résultat: ' || c);
EXCEPTION
  WHEN ZERO_DIVIDE THEN
    DBMS_OUTPUT.PUT_LINE('Erreur: Division par zéro !');
END;
/

--Procédure: afficher nom + catégorie d’un participant
CREATE TABLE participant (
  id NUMBER,
  nom VARCHAR2(50),
  age NUMBER
);

CREATE OR REPLACE PROCEDURE afficher_categorie IS
  CURSOR c_part IS SELECT nom, age FROM participant;
  cat VARCHAR2(20);
BEGIN
  FOR p IN c_part LOOP
    IF p.age < 18 THEN
      cat := 'Junior';
    ELSIF p.age > 50 THEN
      cat := 'Senior';
    ELSE
      cat := 'Middle';
    END IF;
    DBMS_OUTPUT.PUT_LINE(p.nom || ' → ' || cat);
  END LOOP;
END;
/

BEGIN
  afficher_categorie;
END;
/
--Afficher infos d’un participant par identifiant
SET SERVEROUTPUT ON;

DECLARE
  v_id NUMBER := &id;
  v_nom participant.nom%TYPE;
  v_age participant.age%TYPE;
BEGIN
  SELECT nom, age INTO v_nom, v_age
  FROM participant
  WHERE id = v_id;

  DBMS_OUTPUT.PUT_LINE('Nom: ' || v_nom || ', Âge: ' || v_age);
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    DBMS_OUTPUT.PUT_LINE('Aucun participant trouvé.');
END;
/
--using the function participant_par_identifiant
SET SERVEROUT ON;
DECLARE 
 p NUMBER;
 res VARCHAR2(200);
BEGIN 
 p := &valeur;
 res := participant_par_identifiant(p);
 DBMS_OUTPUT.PUT_LINE('THE RESULT :' || res );
 END;
 /
   
--Ecrire un trigger qui se déclenche avant la suppression d’un participant. Le trigger devra supprimer toutes les sorties de ce participant. Faire le test avec la suppression du participant ’Mohamedi’.
CREATE OR REPLACE TRIGGER suppression_de_participant 
BEFORE DELETE ON participant
FOR EACH ROW
BEGIN
  DELETE FROM sortie WHERE idParticipant = :OLD.idParticipant;
  DBMS_OUTPUT.PUT_LINE('Toutes les sorties du participant avec ID ' || :OLD.idParticipant || ' ont été supprimées.');
END;
/
--test the trigger
SET SERVEROUTPUT ON;
BEGIN
  DELETE FROM participant WHERE nomParticipant = 'Mohamedi';
END;
/




ALTER TABLE participant
ADD (
  KmParcourus NUMBER DEFAULT 0,
  categorie VARCHAR2(20),
  date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--Créer un trigger qui permet par l’insertion d’une sortie de modifier la valeur de l’attribut KmParcourus du participant faisant la sortie. La mise a jour consistera ` a ajouter la distance de la randonnee aux kilom ´ etres d ` ej´ a parcourus par le participant

CREATE OR REPLACE TRIGGER mise_a_jour_km
AFTER INSERT ON sortie
FOR EACH ROW
BEGIN
  UPDATE participant
  --but sortie does not have distance column, we need to join with randonnee table to get the distance
  SET KmParcourus = KmParcourus + (SELECT distance FROM randonnee WHERE idRando = :NEW.idRando),
      date_modification = CURRENT_TIMESTAMP
  WHERE idParticipant = :NEW.idParticipant;
END;
/
  
--Créer un trigger qui permet de s’assurer qu’à l’insertion ou à la mise à jour d’une randonnée, celle-ci ne peut être la suite de celle même.
CREATE OR REPLACE TRIGGER verif_suite_rando
BEFORE INSERT OR UPDATE ON randonnee
FOR EACH ROW
BEGIN
  IF :NEW.suiteRando = :NEW.idRando THEN
    RAISE_APPLICATION_ERROR(-20001, 'Une randonnée ne peut pas être sa propre suite.');
  END IF;
END;
/
