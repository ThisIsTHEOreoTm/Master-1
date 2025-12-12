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

--insertion of 1000 line in the tables of Etudiants

DECLARE
  v_nom      VARCHAR2(30);
  v_prenom   VARCHAR2(30);
  v_email    VARCHAR2(50);
    v_tel      VARCHAR2(20);
    v_nss      VARCHAR2(20);
    v_datenais DATE;
    v_villenais VARCHAR2(50);
    v_prenomPere VARCHAR2(30);
    v_mere     VARCHAR2(30);
    v_adr      VARCHAR2(100);
    v_bac      NUMBER;
    v_statut   VARCHAR2(20);
    v_bourse   NUMBER;
    v_depID    NUMBER;
BEGIN
    FOR i IN 1..1000 LOOP
        v_nom := 'Nom' || i;
        v_prenom := 'Prenom' || i;
        v_email := 'email' || i || '@example.com';
        v_tel := '0123456789';
        v_nss := 'NSS' || i;
        v_datenais := TO_DATE('2000-01-01', 'YYYY-MM-DD') + DBMS_RANDOM.VALUE(0, 365 * 20);
        v_villenais := 'Ville' || MOD(i, 10);
        v_prenomPere := 'PrenomPere' || i;
        v_mere := 'Mere' || i;
        v_adr := 'Adresse' || i;
        v_bac := MOD(i, 5) + 1; -- Bac entre 1 et 5
        v_statut := CASE WHEN MOD(i, 2) = 0 THEN 'Licence' ELSE 'Master' END;
        v_bourse := CASE WHEN MOD(i, 3) = 0 THEN 1 ELSE 0 END; -- Bourse ou pas
        v_depID := MOD(i, 10) + 1; -- Départements de 1 à 10

        INSERT INTO Etudiants (Nom, Prenom, Email, Tel, Nss, Datenais, Villenais,
                               PrenomPere, Mere, Adr, Bac, Statut, Bourse, DepID)
        VALUES (v_nom, v_prenom, v_email, v_tel, v_nss, v_datenais,
                v_villenais, v_prenomPere, v_mere, v_adr,
                v_bac, v_statut, v_bourse, v_depID);
    END LOOP;
    COMMIT;
END;
/
--insertion of 300 line in the tables of ensignants
DECLARE
    v_nom      VARCHAR2(30);
    v_prenom   VARCHAR2(30);
    v_email    VARCHAR2(50);
    v_tel      VARCHAR2(20);
    v_nss      VARCHAR2(20);
    v_datenais DATE;
    v_villenais VARCHAR2(50);
    v_prenomPere VARCHAR2(30);
    v_mere     VARCHAR2(30);
    v_adr      VARCHAR2(100);
    v_ensID    NUMBER;
    v_etatCivil VARCHAR2(20);
    v_dateRect DATE;
    v_specialite VARCHAR2(50);
    v_titre     VARCHAR2(30);
    v_depID     NUMBER;
BEGIN
    FOR i IN 1..300 LOOP
        v_nom := 'NomEns' || i;
        v_prenom := 'PrenomEns' || i;
        v_email := 'emailEns' || i || '@example.com';
        v_tel := '0123456789';
        v_nss := 'NSSEns' || i;
        v_datenais := TO_DATE('1980-01-01', 'YYYY-MM-DD') + DBMS_RANDOM.VALUE(0, 365 * 40);
        v_villenais := 'VilleEns' || MOD(i, 10);
        v_prenomPere := 'PrenomPereEns' || i;
        v_mere := 'MereEns' || i;
        v_adr := 'AdresseEns' || i;
        v_ensID := i;
        v_etatCivil := CASE WHEN MOD(i, 2) = 0 THEN 'Marié' ELSE 'Célibataire' END;
        v_dateRect := TO_DATE('2020-01-01', 'YYYY-MM-DD') + DBMS_RANDOM.VALUE(0, 365 * 3);
        v_specialite := 'Specialite' || MOD(i, 5);
        v_titre := CASE WHEN MOD(i, 2) = 0 THEN 'Professeur' ELSE 'Maître de Conférences' END;
        v_depID := MOD(i, 10) + 1; -- Départements de 1 à 10

        INSERT INTO Enseignants (Nom, Prenom, Email, Tel, Nss, Datenais,
                                 Villenais, PrenomPere, Mere, Adr,
                                 EnsID, EtatCivil, DateRect,
                                 Specialite, Titre, DepID)
        VALUES (v_nom, v_prenom, v_email, v_tel, v_nss,
                v_datenais, v_villenais,
                v_prenomPere, v_mere, v_adr,
                v_ensID, v_etatCivil,
                v_dateRect, v_specialite,
                v_titre, v_depID);
    END LOOP;
    COMMIT;
END;

/
--insertion of 2 line in the tables of Departements(math et info)

DECLARE
    v_depID NUMBER;
    v_nom VARCHAR2(50);
BEGIN
    v_depID := 1;
    v_nom := 'Mathématiques';
    INSERT INTO Departements (DepID, Nom) VALUES (v_depID, v_nom);

    v_depID := 2;
    v_nom := 'Informatique';
    INSERT INTO Departements (DepID, Nom) VALUES (v_depID, v_nom);
END;
/

--12.1 starting with fragmentation in the other database in the real machin
-- username: agent password: agent bddsid: agent


