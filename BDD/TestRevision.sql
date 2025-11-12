
--1 Empêcher l’ajout d’une randonnée dont la distance est négative ou nulle.”
SET SERVEROUTPUT ON;
CREATE OR REPLACE TRIGGER verify_Distance_sortie
BEFORE INSERT OR UPDATE ON Randonnee
FOR EACH ROW 
BEGIN
  IF :NEW.distance <= 0 THEN
    RAISE_APPLICATION_ERROR(-20002, 'La distance doit être positive et non nulle.');
  END IF;
END; 

BEGIN
  INSERT INTO Randonnee (idRando, nomRando, region, distance, denivele, suiteRando)
  VALUES (13, 'Test Rando', 'Test Region', -5, 100, NULL);
END;
/

-- 2 Lorsqu'un participant  est ajoute,verifier que son age est>=16 ans sinon empeche l'insertion
SET SERVEROUTPUT ON;
CREATE OR REPLACE TRIGGER verify_Age_Participant 
BEFORE INSERT OR UPDATE ON participant
FOR EACH ROW
BEGIN
  IF :NEW.age < 16 THEN
    RAISE_APPLICATION_ERROR(-20002, 'ITS A MINOR');
  END IF;
END;

--3 Une sortie ne puet pas etre saise a l'avance
SET SERVEROUTPUT ON;
CREATE OR REPLACE TRIGGER verify_Date_Sortie
BEFORE INSERT OR UPDATE ON sortie
FOR EACH ROW
BEGIN
  IF :NEW.dateSortie > SYSDATE THEN
    RAISE_APPLICATION_ERROR(-20003, 'La date de la sortie ne peut pas être dans le futur.');
  END IF;
END;

--4 ON INTERDIT LE CHANGEMENT DE L'ADRESSE D'UN PARTICIPANT SI A EFFECTUE DES SORTIES
SET SERVEROUTPUT ON;
CREATE OR REPLACE TRIGGER prevent_Address_Change
BEFORE UPDATE OF ville ON participant
FOR EACH ROW
BEGIN
  IF EXISTS (SELECT * FROM sortie WHERE idParticipant = :OLD.idParticipant) THEN
    RAISE_APPLICATION_ERROR(-20004, 'Changement d''adresse interdit : le participant a déjà effectué des sorties.');
  END IF;
END;
--Number but this time using COUNT
CREATE OR REPLACE TRIGGER prevent_Address_Change
BEFORE UPDATE ON participant
FOR EACH ROW
DECLARE
  sortie_count NUMBER;
BEGIN
  SELECT COUNT(*) INTO sortie_count FROM sortie WHERE id_participant = :OLD.id;
  IF sortie_count > 0 THEN
    RAISE_APPLICATION_ERROR(-20004, 'Changement d''adresse interdit : le participant a déjà effectué des sorties.');
  END IF;
END;

-- 5 Apres une mise a jour sur la table participant, inserer dans la table (cree precedemment) history(data, type, user, ...)
CREATE TABLE history (
  data_modification TIMESTAMP,
  type_modification VARCHAR2(50),
  utilisateur VARCHAR2(50)
);

SET SERVEROUTPUT ON;
CREATE OR REPLACE TRIGGER log_Participant_Update
AFTER UPDATE ON participant
FOR EACH ROW
BEGIN
  INSERT INTO history (data_modification, type_modification, utilisateur)
  VALUES (CURRENT_TIMESTAMP, 'UPDATE PARTICIPANT', USER);
END;
--test with update
UPDATE participant SET nom = 'TestName' WHERE id = 1;

-- 6 participant ne peut pas effectuer une sortie dont la distance est superieure a 20km
SET SERVEROUTPUT ON;
CREATE OR REPLACE TRIGGER DISTANCE_CHECK 
BEFORE INSERT OR UPDATE ON sortie
FOR EACH ROW
BEGIN
  IF :NEW.distance > 20 THEN
    RAISE_APPLICATION_ERROR(-20005, 'La distance de la sortie doit être inférieure ou égale à 20km.');
  END IF;
END;

--7 Cree une table Log_Actions_Log pour journaliser toutes les operations de mise a jour 
CREATE TABLE Log_Actions_Log (
  action_participant_id NUMBER,
  table_name VARCHAR2(50),
  operation_type VARCHAR2(10),
  action_timestamp TIMESTAMP,
  utilisateur VARCHAR2(50)
);
SET SERVEROUTPUT ON;
CREATE OR REPLACE TRIGGER log_Update_Actions
AFTER UPDATE OR DELETE OR INSERT ON participant
FOR EACH ROW
BEGIN
  IF INSERTING THEN
    INSERT INTO Log_Actions_Log (table_name, operation_type, action_timestamp, utilisateur,action_participant_id  )
    VALUES ('PARTICIPANT', 'INSERT', CURRENT_TIMESTAMP, USER, :NEW.idParticipant);
  ELSIF UPDATING THEN
    INSERT INTO Log_Actions_Log (table_name, operation_type, action_timestamp, utilisateur,action_participant_id)
    VALUES ('PARTICIPANT', 'UPDATE', CURRENT_TIMESTAMP, USER, :NEW.idParticipant);
  ELSIF DELETING THEN
    INSERT INTO Log_Actions_Log (table_name, operation_type, action_timestamp, utilisateur,action_participant_id)
    VALUES ('PARTICIPANT', 'DELETE', CURRENT_TIMESTAMP, USER, :OLD.idParticipant);
  END IF;
END;

--8 Un junior(categorie) ne peut pas faire une sortie hors de sa ville
CREATE OR REPLACE TRIGGER sortie_auto 
BEFORE INSERT ON Sortie 
FOR EACH ROW
BEGIN
  FOR p in (SELECT * FROM Participant WHERE NEW.idParticipant = idParticipant) LOOP
   IF (p.categorie = 'Junior' AND (SELECT ville FROM Randonnee WHERE idRando = NEW.idRando) <> p.ville) THEN
     RAISE_APPLICATION_ERROR(-20006, 'Un participant junior ne peut pas faire une sortie hors de sa ville.');
   END IF;
  END LOOP;
END;

--USING COUNT
CREATE OR REPLACE TRIGGER sortie_auto
BEFORE INSERT ON Sortie
FOR EACH ROW
DECLARE
  participant_count NUMBER;
BEGIN
  SELECT COUNT(*) INTO participant_count
  FROM Participant p
    JOIN Randonnee r ON :NEW.idRando = r.idRando
    WHERE p.idParticipant = :NEW.idParticipant
        AND p.categorie = 'Junior'
        AND r.ville <> p.ville;

    IF participant_count > 0 THEN
        RAISE_APPLICATION_ERROR(-20006, 'Un participant junior ne peut pas faire une sortie hors de sa ville.');
        END IF;
END;

--9 un participant Junior ne peut pas faire des sorties de plus de 20 km
CREATE OR REPLACE TRIGGER junior_distance_check
BEFORE INSERT ON Sortie
FOR EACH ROW
BEGIN
  FOR p IN (SELECT * FROM Participant WHERE idParticipant = :NEW.idParticipant) LOOP
    IF p.categorie = 'Junior' THEN
      IF (SELECT distance FROM Randonnee WHERE idRando = :NEW.idRando) > 20 THEN
        RAISE_APPLICATION_ERROR(-20007, 'Un participant junior ne peut pas faire une sortie de plus de 20 km.');
      END IF;
    END IF;
  END LOOP;
END;

--10 un participant junior ne peut pas faire une sortie hors wilaya (another way to do it)
CREATE OR REPLACE TRIGGER junior_wilaya_check
BEFORE INSERT ON Sortie
FOR EACH ROW
BEGIN
  FOR p IN (SELECT * FROM Participant WHERE idParticipant = :NEW.idParticipant) LOOP
    IF p.categorie = 'Junior' THEN
      IF (SELECT wilaya FROM Randonnee WHERE idRando = :NEW.idRando) <> p.wilaya THEN
        RAISE_APPLICATION_ERROR(-20008, 'Un participant junior ne peut pas faire une sortie hors de sa wilaya.');
      END IF;
    END IF;
  END LOOP;
END;

--11 un participant Junior ne peut pas fair deux sortie dans la meme journee
CREATE OR REPLACE TRIGGER junior_unique_sortie_per_day
BEFORE INSERT ON Sortie
FOR EACH ROW
DECLARE
  sortie_count NUMBER;
BEGIN
  IF (SELECT COUNT(*) FROM Participant WHERE idParticipant = :NEW.idParticipant AND categorie = 'Junior') > 0 THEN
    SELECT COUNT(*)
    INTO sortie_count
    FROM Sortie
    WHERE idParticipant = :NEW.idParticipant
    AND TRUNC(dateSortie) = TRUNC(:NEW.dateSortie);
    
    --what TRUNC does is to ignore the time part of the date and compare only the date part

    IF sortie_count > 0 THEN
      RAISE_APPLICATION_ERROR(-20009, 'Un participant junior ne peut pas faire deux sorties dans la même journée.');
    END IF;
  END IF;
END;
/

--12 un participant age plus de 60 ans ne peut pas faire une sortie avec un denivel superieur a 1500
CREATE OR REPLACE TRIGGER senior_denivel_check
BEFORE INSERT ON Sortie
FOR EACH ROW
DECLARE
  participant_age NUMBER;
  rando_denivel NUMBER;
BEGIN
  SELECT age INTO participant_age
  FROM Participant
  WHERE idParticipant = :NEW.idParticipant;

  SELECT denivele INTO rando_denivel
  FROM Randonnee
  WHERE idRando = :NEW.idRando;

  IF participant_age > 60 AND rando_denivel > 1500 THEN
    RAISE_APPLICATION_ERROR(-20010, 'Un participant âgé de plus de 60 ans ne peut pas faire une sortie avec un dénivelé supérieur à 1500.');
  END IF;
END;
/

--13 empecher l'ajout d'une randonnee dont dont la distance est negative ou nulle
CREATE OR REPLACE TRIGGER check_randonnee_distance
BEFORE INSERT OR UPDATE ON Randonnee
FOR EACH ROW
BEGIN
  IF :NEW.distance <= 0 THEN
    RAISE_APPLICATION_ERROR(-20011, 'La distance de la randonnée doit être positive et non nulle.');
  END IF;
END;

