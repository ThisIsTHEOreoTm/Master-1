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

SELECT * FROM Randonnee;


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


UPDATE participant
SET nomParticipant = UPPER(nomParticipant);




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


