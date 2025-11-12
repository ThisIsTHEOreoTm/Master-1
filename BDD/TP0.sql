-- Jeu de données sur des sorties randonnées 

-- Creation des trois tables 
CREATE TABLE Randonnee(idRando INT UNIQUE, nomRando VARCHAR(255), region VARCHAR(255), distance REAL, denivele INT, suiteRando INT);
CREATE TABLE Participant(idParticipant INT UNIQUE, nomParticipant VARCHAR(255), ville VARCHAR(255), age INT);
CREATE TABLE Sortie(idRando INT REFERENCES Randonnee(idRando), idParticipant INT REFERENCES Participant(idParticipant), dateSortie DATE, dureeSortie REAL, UNIQUE (idRando, idParticipant, dateSortie));

-- Insertions de tuples dans les tables
INSERT INTO Randonnee VALUES (1, 'Monts du Djurdjura', 'Tizi Ouzou', 35, 1000, NULL);
INSERT INTO Randonnee VALUES (2, 'Circuit de Misserghin', 'Oran', 25 , 514, NULL);
INSERT INTO Randonnee VALUES (3, 'Montagne de Murdjadju', 'Oran', 31, 1100, 2);
INSERT INTO Randonnee VALUES (4, 'Canastel', 'Oran', 18, 890, 3);
INSERT INTO Randonnee VALUES (5, 'Yama Gouraya', 'Bejaia', 19, 900, NULL);
INSERT INTO Randonnee VALUES (6, 'Sidi Makhlouf', 'Blida', 8, 165, 8);
INSERT INTO Randonnee VALUES (7, 'Tikjda', 'Tizi Ouzou', 10, 1900, NULL);
INSERT INTO Randonnee VALUES (8, 'Mechria', 'Naama', 14.18, 454, NULL);
INSERT INTO Randonnee VALUES (9, 'Chréa Azzazga', 'Tizi Ouzou', 6.23, 1548, 11);
INSERT INTO Randonnee VALUES (10, 'Bainem', 'Tipaza', 14.5, 1735, NULL);
INSERT INTO Randonnee VALUES (11, 'Couloir du Nador', 'Tizi Ouzou', 21, 1150, NULL);
INSERT INTO Randonnee VALUES (12, 'Miliana', 'Ain Dafla', 10.8, 1200, NULL);

BEGIN 
INSERT INTO Participant VALUES (1, 'Idir', 'Bejaia', 18);
INSERT INTO Participant VALUES (2, 'Mohamedi', 'Oran', 22);
INSERT INTO Participant VALUES (3, 'Naceri', 'Oran', 34);
INSERT INTO Participant VALUES (4, 'Benfeghoul', 'Alger', 45);
INSERT INTO Participant VALUES (5, 'Brahimi', 'Annaba', 59);
INSERT INTO Participant VALUES (6, 'Settouti', 'Tlemcen', 66);
INSERT INTO Participant VALUES (7, 'Ben Ahmed', 'Alger', 54);
INSERT INTO Participant VALUES (8, 'Ghali', 'Alger', 38);
INSERT INTO Participant VALUES (9, 'Ghazali', 'Tizi Ouzou', 29);
INSERT INTO Participant VALUES (10, 'Rbia', 'Tizi Ouzou', 21);

END;





INSERT INTO Sortie VALUES (1, 1, '21/07/2011', 6);
INSERT INTO Sortie VALUES (12, 7, '28/11/2011', 5.5);
INSERT INTO Sortie VALUES (2, 2, '01/01/2007', 6);
INSERT INTO Sortie VALUES (2, 5, '17/06/2012', 7.5);
INSERT INTO Sortie VALUES (8, 5, '21/07/2008', 6.5);
INSERT INTO Sortie VALUES (4, 5, '08/03/2011', 3.5);
INSERT INTO Sortie VALUES (7, 3, '19/05/2011', 11);
INSERT INTO Sortie VALUES (9, 2, '24/06/2014', 7);
INSERT INTO Sortie VALUES (10, 2, '25/06/2011', 8.5);
INSERT INTO Sortie VALUES (4, 8, '16/04/2010', 6);
INSERT INTO Sortie VALUES (5, 8, '17/04/2010', 4.5);
INSERT INTO Sortie VALUES (6, 8, '18/04/2010', 5);
INSERT INTO Sortie VALUES (11, 8, '23/08/2010', 6);
INSERT INTO Sortie VALUES (11, 2, '23/07/2012', 7);
INSERT INTO Sortie VALUES (11, 5, '23/07/2012', 7);
INSERT INTO Sortie VALUES (7, 2, '27/01/2006', 6);
INSERT INTO Sortie VALUES (9, 9, '17/05/2011', 6.5);
INSERT INTO Sortie VALUES (10, 9, '10/04/2008', 6);
INSERT INTO Sortie VALUES (10, 3, '24/02/2006', 2);
INSERT INTO Sortie VALUES (8, 10, '13/05/2012', 10.5);
INSERT INTO Sortie VALUES (5, 9, '01/09/2009', 3);
INSERT INTO Sortie VALUES (5, 1, '01/09/2009', 3);
INSERT INTO Sortie VALUES (8, 7, '14/06/2011', 6);
INSERT INTO Sortie VALUES (8, 7, '03/07/2012', 5);
INSERT INTO Sortie VALUES (8, 7, '19/05/2007', 5.5);




--Procédure: afficher nom + catégorie d’un participant
CREATE OR REPLACE PROCEDURE afficher_categorie IS
  CURSOR part IS SELECT nomParticipant, age FROM participant;
  cat VARCHAR(20);
  BEGIN
    FOR p IN part LOOP
      IF p.age < 18 THEN
        cat := 'Junior';
      ELSIF p.age > 50 THEN
        cat := 'Senior';
      ELSE
        cat := 'Middle';
      END IF;
      DBMS_OUTPUT.PUT_LINE(p.nomParticipant || ' → ' || cat);
    END LOOP;
  END;
/
BEGIN
  afficher_categorie;
END;



--Ecrire un bloc PL/SQL pour generer une exception lors d’une division par zero
SET SERVEROUTPUT ON;
DECLARE
  a NUMBER := &valeur;
  b NUMBER := &diviseur;
  c NUMBER;
BEGIN
  c := a / b;  -- division par zéro
  DBMS_OUTPUT.PUT_LINE('Résultat: ' || c);
  EXCEPTION
    WHEN ZERO_DIVIDE THEN
      DBMS_OUTPUT.PUT_LINE('Erreur: Division par zéro !');
END;
/



--Afficher les informations d’un participant a partir de son identifiant.
CREATE OR REPLACE FUNCTION participant_par_identifiant(n NUMBER)
RETURN VARCHAR2
IS
  v_nom VARCHAR2(100);
  v_ville VARCHAR2(100);
  v_age NUMBER;
BEGIN
  SELECT nomParticipant, ville, age
  INTO v_nom, v_ville, v_age
  FROM Participant
  WHERE idParticipant = n;

  RETURN 'Nom: ' || v_nom || ', Ville: ' || v_ville || ', Age: ' || v_age;
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    RETURN 'Aucun participant trouvé avec cet identifiant.';
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
--Ajouter dans la table participant les attributs KmParcourus, categorie et date de modification.
--L’attribut categorie devra contenir la catégorie du participant.
--L’attribut KmParcourus devra contenir le nombre total de Km déjà parcourus pour chaque participant.
--l’attribut date modification devra contenir la date et l’heure, chaque fois qu’une ligne du table participant est mise a jour

ALTER TABLE participant
ADD (
  KmParcourus NUMBER DEFAULT 0,
  categorie VARCHAR2(20),
  date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--Creer un trigger qui permet apr ´ es l’insertion d’une sortie, de modifier la valeur de l’attribut KmParcourus du participant faisant la sortie. La mise a jour consistera ` a ajouter la distance de la randonnee aux kilom ´ etres d ` ej´ a parcourus par le participant

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

--test du trigger
INSERT INTO sortie (idRando, idParticipant, dateSortie, dureeSortie)
VALUES (1, 1, SYSDATE, 5);

--Creer un trigger qui permet de s’assurer qu’ ´ a l’insertion ou ` a la mise ` a jour d’une randonnee, que celle ci ne peut etre la suite d’elle m ˆ eme.
CREATE OR REPLACE TRIGGER verif_suite_rando
BEFORE INSERT OR UPDATE ON randonnee
FOR EACH ROW
BEGIN
  IF :NEW.suiteRando = :NEW.idRando THEN
    RAISE_APPLICATION_ERROR(-20001, 'Une randonnée ne peut pas être sa propre suite.');
  END IF;
END;
/


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
--using count 
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
  FOR p in (SELECT 1 FROM Participant WHERE NEW.idParticipant = idParticipant) LOOP
  --is SELECT 1 valid here?: yes cause we just need to check existence
   IF (p.categorie = "Junior" AND (SELECT ville FROM Randonnee WHERE idRando = NEW.idRando) <> p.ville) THEN
     RAISE_APPLICATION_ERROR(-20006, 'Un participant junior ne peut pas faire une sortie hors de sa ville.');
   END IF;
  END LOOP;
END;
--using three variables
CREATE OR REPLACE TRIGGER sortie_auto
BEFORE INSERT ON Sortie
FOR EACH ROW
DECLARE
  participant_categorie VARCHAR2(20);
  rando_ville VARCHAR2(100);
  participant_ville VARCHAR2(100);
BEGIN
  SELECT categorie INTO participant_categorie
  FROM Participant
  WHERE idParticipant = :NEW.idParticipant;

  SELECT ville INTO rando_ville
  FROM Randonnee
  WHERE idRando = :NEW.idRando;

  SELECT ville INTO participant_ville
  FROM Participant
  WHERE idParticipant = :NEW.idParticipant;

  IF participant_categorie = 'Junior' AND rando_ville <> participant_ville THEN
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
--using two variables
CREATE OR REPLACE TRIGGER junior_distance_check
BEFORE INSERT ON Sortie
FOR EACH ROW
DECLARE
  participant_categorie VARCHAR2(20);
  rando_distance NUMBER;
BEGIN
  SELECT categorie INTO participant_categorie
  FROM Participant
  WHERE idParticipant = :NEW.idParticipant;
  SELECT distance INTO rando_distance
  FROM Randonnee
  WHERE idRando = :NEW.idRando;
  IF participant_categorie = 'Junior' AND rando_distance > 20 THEN
    RAISE_APPLICATION_ERROR(-20007, 'Un participant junior ne peut pas faire une sortie de plus de 20 km.');
  END IF;
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
--using variables
CREATE OR REPLACE TRIGGER junior_wilaya_check
BEFORE INSERT ON Sortie
FOR EACH ROW
DECLARE
  participant_categorie VARCHAR2(20);
  participant_wilaya VARCHAR2(100);
  rando_wilaya VARCHAR2(100);
BEGIN
  SELECT categorie, wilaya INTO participant_categorie, participant_wilaya
  FROM Participant
  WHERE idParticipant = :NEW.idParticipant;

  SELECT wilaya INTO rando_wilaya
  FROM Randonnee
  WHERE idRando = :NEW.idRando;

  IF participant_categorie = 'Junior' AND rando_wilaya <> participant_wilaya THEN
    RAISE_APPLICATION_ERROR(-20008, 'Un participant junior ne peut pas faire une sortie hors de sa wilaya.');
  END IF;
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
--using variables
CREATE OR REPLACE TRIGGER junior_unique_sortie_per_day
BEFORE INSERT ON Sortie
FOR EACH ROW
DECLARE
  participant_categorie VARCHAR2(20);
  sortie_count NUMBER;
BEGIN
  SELECT categorie INTO participant_categorie
  FROM Participant
  WHERE idParticipant = :NEW.idParticipant;
  IF participant_categorie = 'Junior' THEN
    SELECT COUNT(*)
    INTO sortie_count
    FROM Sortie
    WHERE idParticipant = :NEW.idParticipant
    AND TRUNC(dateSortie) = TRUNC(:NEW.dateSortie);

    IF sortie_count > 0 THEN
      RAISE_APPLICATION_ERROR(-20009, 'Un participant junior ne peut pas faire deux sorties dans la même journée.');
    END IF;
  END IF;
END;

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









--replit categorie dans participant 
SET SERVEROUTPUT ON;

CREATE OR REPLACE PROCEDURE UPDATE_CATEGORIE_PARTICIPANT IS
BEGIN
  UPDATE participant
  SET categorie = CASE
    WHEN age < 18 THEN 'Junior'
    WHEN age > 50 THEN 'Senior'
    ELSE 'Middle'
  END;

  DBMS_OUTPUT.PUT_LINE('Catégories mises à jour avec succès.');
END;
/
--insert a Junior participant to test in the end of the table

INSERT INTO participant (idParticipant, nomParticipant, ville, age) VALUES (11, 'Petite', 'Test City', 16);

BEGIN
  UPDATE_CATEGORIE_PARTICIPANT;
END;





















SELECT * FROM Randonnee;
-- view all the Tables in the database in oracle Oracle(only the name of each Table without details all the tables name)
SELECT table_name
FROM user_tables;
--view all function in Oracle
SELECT object_name
FROM user_objects
WHERE object_type = 'FUNCTION';




-- view all user in the database in oracle Oracle
SELECT username
FROM all_users;

SELECT idRando, nomRando
FROM Randonnee
WHERE distance > 20;

SELECT *
FROM Participant
WHERE age BETWEEN 35 AND 50;

SELECT *
FROM Randonnee
WHERE suiteRando IS NOT NULL;

SELECT r1.idRando AS id_randonnee,
       r1.nomRando AS nom_randonnee,
       r2.idRando AS id_suivante,
       r2.nomRando AS nom_suivante
FROM Randonnee r1
JOIN Randonnee r2 ON r1.suiteRando = r2.idRando;


SELECT p.idParticipant, p.nomParticipant, s.idRando, s.dateSortie, s.dureeSortie
FROM Participant p
LEFT JOIN Sortie s ON p.idParticipant = s.idParticipant
WHERE p.age < 50;


SELECT DISTINCT p.idParticipant, p.nomParticipant
FROM Participant p
JOIN Sortie s ON p.idParticipant = s.idParticipant
JOIN Randonnee r ON s.idRando = r.idRando
WHERE r.denivele > 1000;

-------------------------------------------------------
SELECT DISTINCT nomParticipant
FROM Participant
WHERE idParticipant IN (
  SELECT s.idParticipant
  FROM Sortie s
  JOIN Randonnee r ON s.idRando = r.idRando
  WHERE r.denivele > 1000
);



SELECT nomParticipant
FROM Participant
WHERE idParticipant NOT IN (
  SELECT idParticipant FROM Sortie
);



SELECT DISTINCT nomParticipant
FROM Participant
WHERE LOWER(ville) LIKE '%an%'
AND idParticipant IN (
  SELECT idParticipant FROM Sortie
);



SELECT nomRando
FROM Randonnee
WHERE idRando NOT IN (
  SELECT idRando FROM Sortie
);


SELECT *
FROM Participant
WHERE age = (SELECT MAX(age) FROM Participant);



SELECT *
FROM Sortie
WHERE dureeSortie = (SELECT MAX(dureeSortie) FROM Sortie);




SELECT nomParticipant
FROM Participant
WHERE idParticipant IN (
  SELECT idParticipant FROM Sortie
  WHERE EXTRACT(YEAR FROM dateSortie) = 2011
)
AND idParticipant IN (
  SELECT idParticipant FROM Sortie
  WHERE EXTRACT(YEAR FROM dateSortie) = 2012
);




SELECT DISTINCT nomParticipant
FROM Participant
WHERE idParticipant IN (
  SELECT idParticipant FROM Sortie
  WHERE EXTRACT(YEAR FROM dateSortie) IN (2011, 2012)
);






SELECT COUNT(*) AS nbParticipants
FROM participant;



SELECT AVG(age) AS ageMoyen
FROM participant;


SELECT MAX(distance) AS distanceMax
FROM randonnee;


SELECT COUNT(*) AS nbRandoBlida
FROM randonnee
WHERE region = 'Blida';


SELECT region, COUNT(*) AS nbRandos
FROM randonnee
GROUP BY region;

SELECT *
FROM sortie
WHERE dateSortie = (SELECT MAX(dateSortie) FROM sortie);




SELECT dateSortie, COUNT(*) AS nbSorties
FROM sortie
GROUP BY dateSortie;


SELECT YEAR(dateSortie) AS annee, COUNT(*) AS nbSorties
FROM sortie
GROUP BY YEAR(dateSortie);



SELECT idParticipant, COUNT(idRando) AS nbRandos
FROM sortie
GROUP BY idParticipant;


SELECT idParticipant
FROM sortie
GROUP BY idParticipant
HAVING COUNT(idRando) = 1;



SELECT p.idParticipant, p.nomParticipant, SUM(r.distance) AS distanceTotale
FROM participant p
JOIN sortie s ON p.idParticipant = s.idParticipant
JOIN randonnee r ON s.idRando = r.idRando
GROUP BY p.idParticipant, p.nomParticipant
ORDER BY distanceTotale DESC;



SELECT p.ville,
       ROUND(COUNT(s.idRando) * 100.0 / (SELECT COUNT(*) FROM sortie), 2) AS pourcentage
FROM participant p
JOIN sortie s ON p.idParticipant = s.idParticipant
GROUP BY p.ville
ORDER BY pourcentage ASC;



SELECT r.idRando, r.nomRando, COUNT(r2.idRando) AS nbRandoSuivantes
FROM randonnee r
LEFT JOIN randonnee r2 ON r.idRando = r2.suiteRando
GROUP BY r.idRando, r.nomRando;


UPDATE participant SET nomParticipant = UPPER(nomParticipant);




UPDATE participant
SET ville = 'Tlemcen'
WHERE nomParticipant = 'GHAZALI';




UPDATE randonnee
SET suiteRando = 0
WHERE suiteRando IS NULL;


ALTER TABLE randonnee ADD pays VARCHAR(50);
UPDATE randonnee SET pays = 'ALGERIE';



ALTER TABLE sortie
ADD CONSTRAINT chk_duree CHECK (dureeSortie > 0);

ALTER TABLE participant
ADD CONSTRAINT chk_age CHECK (age > 0);



CREATE VIEW jeunes_participants AS
SELECT *
FROM participant
WHERE age < 50;



CREATE VIEW jeunes_tizi AS
SELECT jp.nomParticipant
FROM jeunes_participants jp
JOIN sortie s ON jp.idParticipant = s.idParticipant
JOIN randonnee r ON s.idRando = r.idRando
WHERE r.region = 'Tizi Ouzou';


