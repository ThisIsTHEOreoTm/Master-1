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
        SELF.Statut := nouveauStatut;
    END changerNiveau;

    MEMBER FUNCTION afficherInfos RETURN VARCHAR2 IS
    BEGIN
        RETURN 'Etudiant: ' || SELF.Nom || ' ' || SELF.Prenom ||
               ', Statut=' || SELF.Statut ||
               ', Département=' || SELF.DepID;
    END afficherInfos;

    MEMBER PROCEDURE payerFrais(montant NUMBER) IS
    BEGIN
        DBMS_OUTPUT.PUT_LINE('Paiement de ' || montant || ' DA effectué pour ' || SELF.Nom);
    END payerFrais;

END;
/


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



--12.1 starting with fragmentation in the other database in the real machin
-- username: agent password: agent bddsid: agent


