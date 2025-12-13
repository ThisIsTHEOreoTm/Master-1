--Machin global creation of tables plus methods and types
--username: admin password: etud sid: Etudiant
CREATE TYPE Personne_t AS OBJECT (
    Nom VARCHAR2(30),
    Prenom VARCHAR2(30),
    Datenais DATE,
    Villenais VARCHAR2(50),
    PrenomPere VARCHAR2(30),
    Mere VARCHAR2(30),
    Adr VARCHAR2(100),
    Tel VARCHAR2(20),
    Email VARCHAR2(50),
    Nss VARCHAR2(20) 
)NOT FINAL;
/

CREATE TYPE Enseignant_t UNDER Personne_t (
    EnsID NUMBER,
    TelEns VARCHAR2(20),
    MailEns VARCHAR2(50),
    EtatCivil VARCHAR2(20),
    DateRect DATE,
    Specialite VARCHAR2(50),
    Titre VARCHAR2(30),
    DepID NUMBER,

    
    MEMBER PROCEDURE ajouterSeance(scID NUMBER),
    MEMBER PROCEDURE modifierGrade(nouveauGrade VARCHAR2),
    MEMBER FUNCTION afficherPlanning RETURN VARCHAR2
);
/

CREATE TYPE Etudiant_t UNDER Personne_t (
    EtID NUMBER,
    DateInsc DATE,
    Bac NUMBER,      
    Statut VARCHAR2(20),
    Bourse NUMBER,
    DepID NUMBER,

    MEMBER PROCEDURE inscrire(scID NUMBER),
    MEMBER PROCEDURE changerNiveau(nouveauStatut VARCHAR2),
    MEMBER FUNCTION afficherInfos RETURN VARCHAR2,
    MEMBER PROCEDURE payerFrais(montant NUMBER)
);
/


CREATE TYPE Salle_t AS OBJECT (
    SID NUMBER,
    DepID NUMBER,
    SType VARCHAR2(20),
    SNom VARCHAR2(50),
    NBPlaces NUMBER,
    Etage NUMBER,
    Bloc VARCHAR2(10),

    
    MEMBER FUNCTION afficherOccupation RETURN VARCHAR2,
    MEMBER PROCEDURE ajouterReservation(seanceID NUMBER)
);
/

CREATE TYPE Seance_t AS OBJECT(
    EnsID NUMBER,
    EtID NUMBER,
    ScType VARCHAR2(10),
    ScJour VARCHAR2(10),
    ScCreneau VARCHAR2(20),
    Descrip VARCHAR2(100),
    SID NUMBER,
    DepID NUMBER,

    
    MEMBER PROCEDURE changerHoraire(nouveauCreneau VARCHAR2),
    MEMBER PROCEDURE ajouterEtudiant(etudiantID NUMBER),
    MEMBER FUNCTION afficherParticipants RETURN VARCHAR2
);
/


CREATE TYPE Departement_t AS OBJECT(
    DepID NUMBER,
    DepNom VARCHAR2(50),
    DepDesig VARCHAR2(50),
    EnsID NUMBER,

     MEMBER FUNCTION afficherMembres RETURN VARCHAR2,
    MEMBER PROCEDURE ajouterMembre(personneID NUMBER)
);
/


--methods implementations

CREATE TYPE BODY Etudiant_t AS

    MEMBER PROCEDURE inscrire(scID NUMBER) IS
    BEGIN
        INSERT INTO Seances(EnsID, EtID, SID)
        VALUES (NULL, SELF.EtID, scID);
    END inscrire;

    MEMBER PROCEDURE changerNiveau(nouveauStatut VARCHAR2) IS
    BEGIN
        UPDATE ETUDIANTS_TAB e
        SET e.Statut = nouveauStatut
        WHERE e.EtID = SELF.EtID;
    END changerNiveau;

    MEMBER FUNCTION afficherInfos RETURN VARCHAR2 IS
    BEGIN
        RETURN 'Etudiant: ' || SELF.Nom || ' ' || SELF.Prenom ||
               ', Statut=' || SELF.Statut ||
               ', Département=' || SELF.DepID;
    END afficherInfos;

    MEMBER PROCEDURE payerFrais(montant NUMBER) IS
    BEGIN
        DBMS_OUTPUT.PUT_LINE(
            'Paiement de ' || montant || ' DA effectué pour ' || SELF.Nom
        );
    END payerFrais;

END;
/

--fixing the same for Enseignant_t
DROP TYPE BODY Enseignant_t;

CREATE TYPE BODY Enseignant_t AS

    MEMBER PROCEDURE ajouterSeance(scID NUMBER) IS
    BEGIN
        INSERT INTO Seances(EnsID, EtID, SID)
        VALUES (SELF.EnsID, NULL, scID);
    END ajouterSeance;

    MEMBER PROCEDURE modifierGrade(nouveauGrade VARCHAR2) IS
    BEGIN
        SELF.Titre := nouveauGrade;
    END modifierGrade;

    MEMBER FUNCTION afficherPlanning RETURN VARCHAR2 IS
        result VARCHAR2(4000) := 'Planning de ' || SELF.Nom || ' : ';
    BEGIN
        FOR x IN (SELECT ScJour, ScCreneau, SID
                  FROM Seances
                  WHERE EnsID = SELF.EnsID) LOOP
            result := result || CHR(10) ||
                      '- ' || x.ScJour || ' (' || x.ScCreneau ||
                      ') | Salle ' || x.SID;
        END LOOP;
        RETURN result;
    END afficherPlanning;

END;
/


CREATE TYPE BODY Seance_t AS

    MEMBER PROCEDURE changerHoraire(nouveauCreneau VARCHAR2) IS
    BEGIN
        SELF.ScCreneau := nouveauCreneau;
    END changerHoraire;

    MEMBER PROCEDURE ajouterEtudiant(etudiantID NUMBER) IS
    BEGIN
        UPDATE Seances
        SET EtID = etudiantID
        WHERE EnsID = SELF.EnsID
          AND SID   = SELF.SID;
    END ajouterEtudiant;

    MEMBER FUNCTION afficherParticipants RETURN VARCHAR2 IS
        res VARCHAR2(4000) := 'Participants: ';
    BEGIN
        FOR x IN (SELECT e.Nom, e.Prenom
                  FROM Etudiants e
                  WHERE e.EtID = SELF.EtID) LOOP
            res := res || CHR(10) ||
                   '- ' || x.Nom || ' ' || x.Prenom;
        END LOOP;

        RETURN res;
    END afficherParticipants;

END;
/


CREATE TYPE BODY Departement_t AS

    MEMBER FUNCTION afficherMembres RETURN VARCHAR2 IS
        res VARCHAR2(4000) := 'Membres du département ' || SELF.DepNom || ' : ';
    BEGIN
        -- Étudiants
        FOR e IN (SELECT Nom, Prenom FROM Etudiants WHERE DepID = SELF.DepID) LOOP
            res := res || CHR(10) || 'Etudiant : ' || e.Nom || ' ' || e.Prenom;
        END LOOP;

        -- Enseignants
        FOR ens IN (SELECT Nom, Prenom FROM Enseignants WHERE DepID = SELF.DepID) LOOP
            res := res || CHR(10) || 'Enseignant : ' || ens.Nom || ' ' || ens.Prenom;
        END LOOP;

        RETURN res;
    END afficherMembres;

    MEMBER PROCEDURE ajouterMembre(personneID NUMBER) IS
    BEGIN
        UPDATE Etudiants
        SET DepID = SELF.DepID
        WHERE EtID = personneID;

        UPDATE Enseignants
        SET DepID = SELF.DepID
        WHERE EnsID = personneID;
    END ajouterMembre;

END;
/

CREATE TYPE BODY Salle_t AS

    MEMBER FUNCTION afficherOccupation RETURN VARCHAR2 IS
        occ VARCHAR2(4000) := 'Occupation de la salle ' || SELF.SNom || ' :';
    BEGIN
        FOR x IN (SELECT ScJour, ScCreneau
                  FROM Seances
                  WHERE SID = SELF.SID) LOOP
            occ := occ || CHR(10) ||
                   '- ' || x.ScJour || ' (' || x.ScCreneau || ')';
        END LOOP;

        RETURN occ;
    END afficherOccupation;

    MEMBER PROCEDURE ajouterReservation(seanceID NUMBER) IS
    BEGIN
        UPDATE Seances
        SET SID = SELF.SID
        WHERE SID = seanceID;
    END ajouterReservation;

END;
/


--creation of tables
CREATE TABLE Etudiants OF Etudiant_t (
    PRIMARY KEY (EtID),
    UNIQUE (Nss)
);

CREATE TABLE Enseignants OF Enseignant_t (
    PRIMARY KEY (EnsID),
    UNIQUE (Nss)
);
CREATE TABLE Departements OF Departement_t
(
    DepID PRIMARY KEY
);

CREATE TABLE Salles OF Salle_t
(
    SID PRIMARY KEY
);
CREATE TABLE Seances OF Seance_t
(
    EnsID,
    EtID,
    SID,
    PRIMARY KEY (EnsID, EtID, SID)
);

--add contraints
ALTER TABLE Etudiants
ADD CONSTRAINT fk_etud_dep
    FOREIGN KEY (DepID)
    REFERENCES Departements(DepID);

ALTER TABLE Enseignants
ADD CONSTRAINT fk_ens_dep
    FOREIGN KEY (DepID)
    REFERENCES Departements(DepID);

ALTER TABLE Salles
ADD CONSTRAINT fk_salle_dep
    FOREIGN KEY (DepID)
    REFERENCES Departements(DepID);

ALTER TABLE Seances
ADD CONSTRAINT fk_seance_dep
    FOREIGN KEY (DepID)
    REFERENCES Departements(DepID);

--insertion of 1000 line in the tables of Etudiants

BEGIN
    FOR i IN 1..1000 LOOP
        INSERT INTO Etudiants
        VALUES (
            Etudiant_t(
                'Nom' || i,
                'Prenom' || i,
                TO_DATE('2000-01-01','YYYY-MM-DD') + DBMS_RANDOM.VALUE(0, 365*20),
                'Ville' || MOD(i,10),
                'PrenomPere' || i,
                'Mere' || i,
                'Adresse' || i,
                '0123456789',
                'email' || i || '@etudiant.com',
                'NSS' || i,
                i, -- EtID
                SYSDATE,
                MOD(i,10)+10,
                CASE WHEN MOD(i,2)=0 THEN 'Licence' ELSE 'Master' END,
                CASE WHEN MOD(i,3)=0 THEN 1 ELSE 0 END,
                MOD(i,2)+1
            )
        );
    END LOOP;
    COMMIT;
END;
/


--insertion of 300 line in the tables of ensignants
--correct method
BEGIN
    FOR i IN 1..300 LOOP
        INSERT INTO Enseignants
        VALUES (
            Enseignant_t(
                'Nom' || i,
                'Prenom' || i,
                TO_DATE('1980-01-01','YYYY-MM-DD') + DBMS_RANDOM.VALUE(0, 365*20),
                'Ville' || MOD(i,10),
                'PrenomPere' || i,
                'Mere' || i,
                'Adresse' || i,
                '0987654321',
                'email' || i || '@enseignant.com',
                'NSS' || (i+1000),
                i, -- EnsID
                '0123456789',
                'ens' || i || '@univ.com',
                CASE WHEN MOD(i,2)=0 THEN 'Célibataire' ELSE 'Marié' END,
                SYSDATE - DBMS_RANDOM.VALUE(0, 365*5),
                'Spécialité' || MOD(i,5),
                CASE WHEN MOD(i,3)=0 THEN 'Professeur' WHEN MOD(i,3)=1 THEN 'Maître de Conférences' ELSE 'Chargé de Cours' END,
                MOD(i,2)+1
            )
        );
    END LOOP;
    COMMIT;
END;

--insertion of 2 line in the tables of Departements(math et info)

BEGIN
    INSERT INTO Departements (DepID, DepNom, DepDesig, EnsID)
    VALUES (1, 'Informatique', 'Département d''Informatique', 1);

    INSERT INTO Departements (DepID, DepNom, DepDesig, EnsID)
    VALUES (2, 'Mathématiques', 'Département de Mathématiques', 2);

    COMMIT;
END;

--insertion of 10 line in the tables of Salles
BEGIN
    FOR i IN 1..10 LOOP
        INSERT INTO Salles (
            SID, DepID, SType, SNom, NBPlaces, Etage, Bloc
        )
        VALUES (
            i,
            MOD(i,2)+1,
            CASE
                WHEN MOD(i,2)=0 THEN 'Amphithéâtre'
                ELSE 'Salle de TP'
            END,
            'Salle ' || i,
            MOD(i,100)+20,
            MOD(i,5)+1,
            CHR(64 + MOD(i,3)+1) -- Bloc A, B, C
        );
    END LOOP;

    COMMIT;
END;
--insertion of 50 line in the tables of Seances
BEGIN
    FOR i IN 1..50 LOOP
        INSERT INTO Seances (
            EnsID, EtID, ScType, ScJour, ScCreneau, Descrip, SID, DepID
        )
        VALUES (
            MOD(i,300)+1,
            MOD(i,1000)+1,
            CASE
                WHEN MOD(i,2)=0 THEN 'CM'
                ELSE 'TD'
            END,
            CASE
                WHEN MOD(i,5)=0 THEN 'Lundi'
                WHEN MOD(i,5)=1 THEN 'Mardi'
                WHEN MOD(i,5)=2 THEN 'Mercredi'
                WHEN MOD(i,5)=3 THEN 'Jeudi'
                ELSE 'Vendredi'
            END,
            CASE
                WHEN MOD(i,3)=0 THEN '08:00-10:00'
                WHEN MOD(i,3)=1 THEN '10:00-12:00'
                ELSE '14:00-16:00'
            END,
            'Description de la séance ' || i,
            MOD(i,10)+1,
            MOD(i,2)+1
        );
    END LOOP;

    COMMIT;
END;


--12.1 starting with fragmentation in the other database in the real machin
-- username: agent password: agent bddsid: skibidi toilet
--dans la deuxieme agent

--etudiant fragment for agent

CREATE TABLE Etudiants_agent AS
SELECT *
FROM Etudiants@link_real1;

--enseignant fragment for agent
CREATE TABLE Enseignants_agent AS
SELECT *
FROM Enseignants@link_real1 en;

--departement fragment for agent
CREATE TABLE Departements_agent AS
SELECT *
FROM Departements@link_to_global d;

-------------------------------------------------
--VM1 de frpartment informatique

-- Fragmentation horizontale des étudiants du département informatique
CREATE TABLE Etudiant AS
SELECT EtID, Nom, Prenom, Datenais, Villenais, Adr, Email, DateInsc, Bac, Statut , DepID
FROM Etudiants@link_to_etud
WHERE DepID = 1;

-- Fragmentation horizontale des enseignants du département informatique
CREATE TABLE Enseignant AS
SELECT EnsID, Nom, Prenom, Datenais, Villenais, Adr, Email, DateRect, Specialite, Titre, DepID
FROM Enseignants@link_to_etud
WHERE DepID = 1;

-- Fragmentation locale des salles
CREATE TABLE Salle AS
SELECT *
FROM Salles@link_to_etud
WHERE DepID = 1;

-- Fragmentation locale des séances
CREATE TABLE Seance AS
SELECT *
FROM Seances@link_to_etud
WHERE DepID = 1;

-- Fragmentation département
CREATE TABLE Departement AS
SELECT *
FROM Departements@link_to_etud
WHERE DepID = 1;

-------------------------------------------------
--VM2 de frpartment mathématiques
CREATE TABLE Etudiant AS
--SELECT EtID, EtNom, EtPrenom, EtDatenais,EtVillenais, EtAdr, Etemail, EtDateInsc, EtBac, EtStatut , DepID
SELECT EtID, Nom, Prenom, Datenais, Villenais, Adr, Email, DateInsc, Bac, Statut , DepID    
FROM Etudiants@link_to_etud
WHERE DepID = 2;

-- Fragmentation horizontale des enseignants du département informatique
CREATE TABLE Enseignant AS
SELECT EnsID, Nom, Prenom, Datenais, Villenais, Adr, Email, DateRect, Specialite, Titre, DepID
FROM Enseignants@link_to_etud
WHERE DepID = 2;

-- Fragmentation locale des salles
CREATE TABLE Salle AS
SELECT *
FROM Salles@link_to_etud
WHERE DepID = 2;

-- Fragmentation locale des séances
CREATE TABLE Seance AS
SELECT *
FROM Seances@link_to_etud
WHERE DepID = 2;

-- Fragmentation département
CREATE TABLE Departement AS
SELECT *
FROM Departements@link_to_etud
WHERE DepID = 2;




------vue all in admin
--global ETUDIANT view
CREATE OR REPLACE VIEW Etudiant_Global AS
SELECT *
FROM Etudiant_Info@link_vm1
UNION ALL
SELECT *
FROM Etudiant_Math@link_vm2;
--global ENSEIGNANT view
CREATE OR REPLACE VIEW Enseignant_Global AS
SELECT *
FROM Enseignant_Info@link_vm1
UNION ALL
SELECT *
FROM Enseignant_Math@link_vm2;
--global salle view
CREATE OR REPLACE VIEW Salle_Global AS
SELECT *
FROM Salle_Info@link_vm1
UNION ALL
SELECT *
FROM Salle_Math@link_vm2;

--Views WITH UPDATE
CREATE OR REPLACE TRIGGER trg_insert_etudiant_global
INSTEAD OF INSERT ON Etudiants
FOR EACH ROW
BEGIN
  IF :NEW.DepID = 1 THEN
    INSERT INTO Etudiant@link_vm1 VALUES (:NEW);
  ELSIF :NEW.DepID = 2 THEN
    INSERT INTO Etudiant@link_vm2 VALUES (:NEW);
  END IF;
END;
/



--test
SELECT COUNT(*) FROM Etudiant_Global;
--compare with:
-- SELECT COUNT(*) FROM Etudiant_Info@link_info
--      + COUNT(*) FROM Etudiant_Math@link_math;





