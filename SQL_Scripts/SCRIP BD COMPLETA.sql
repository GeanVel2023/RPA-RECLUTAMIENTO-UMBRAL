
USE RegionalDB;
GO

-------------------------------------------------------
-- TABLA: Candidato
-------------------------------------------------------
CREATE TABLE Candidato (
    idCandidato INT IDENTITY(1,1) PRIMARY KEY,
    DPI VARCHAR(20),
    NombreCompleto NVARCHAR(150) NOT NULL,
    Correo NVARCHAR(100),
    Telefono VARCHAR(20),
    Direccion NVARCHAR(200),
    FechaNacimiento DATE,
    FechaRegistro DATETIME DEFAULT GETDATE(),
    Nacionalidad NVARCHAR(50),
    Licencias NVARCHAR(50),
    EstadoCandidato VARCHAR(2) DEFAULT 'AC'
);
GO

-------------------------------------------------------
-- TABLA: PuestoTrabajo_enc (Encabezado de puestos)
-------------------------------------------------------
CREATE TABLE PuestoTrabajo_enc (
    idPuesto_enc INT IDENTITY(1,1) PRIMARY KEY,
    NombrePuesto NVARCHAR(100) NOT NULL,
    Departamento NVARCHAR(100),
    Descripcion NVARCHAR(250),
    SalarioMin DECIMAL(10,2),
    SalarioMax DECIMAL(10,2),
    Vigencia CHAR(1) DEFAULT 'S',  -- S=Sí, N=No
    NivelPuesto NVARCHAR(50)
);
GO

-------------------------------------------------------
-- TABLA: Puesto_det (Requisitos del puesto)
-------------------------------------------------------
CREATE TABLE Puesto_det (
    idPuesto_det INT IDENTITY(1,1) PRIMARY KEY,
    idPuesto_enc INT NOT NULL,
    Requisito NVARCHAR(200),
    FOREIGN KEY (idPuesto_enc) REFERENCES PuestoTrabajo_enc(idPuesto_enc)
        ON DELETE CASCADE ON UPDATE CASCADE
);
GO

-------------------------------------------------------
-- TABLA: Candidato_Puesto (Aplicaciones a puestos)
-------------------------------------------------------
CREATE TABLE Candidato_Puesto (
    idAplicacion INT IDENTITY(1,1) PRIMARY KEY,
    idCandidato INT NOT NULL,
    idPuesto_enc INT NOT NULL,
    FechaAplicacion DATETIME DEFAULT GETDATE(),
    PretensionSalarial DECIMAL(10,2),
    EstadoAplicacion VARCHAR(20) DEFAULT 'En revisión',
    FechaEvaluacion DATETIME NULL,
    PuntajeObtenido DECIMAL(5,2) NULL,
    FOREIGN KEY (idCandidato) REFERENCES Candidato(idCandidato)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idPuesto_enc) REFERENCES PuestoTrabajo_enc(idPuesto_enc)
        ON DELETE CASCADE ON UPDATE CASCADE
);
GO

-------------------------------------------------------
-- TABLAS: Experiencia Laboral
-------------------------------------------------------
CREATE TABLE ExperienciaLaboral_enc (
    idExperiencia_enc INT IDENTITY(1,1) PRIMARY KEY,
    idCandidato INT NOT NULL,
    Empresa NVARCHAR(150),
    AñosExperiencia DECIMAL(4,1),
    FOREIGN KEY (idCandidato) REFERENCES Candidato(idCandidato)
        ON DELETE CASCADE ON UPDATE CASCADE
);
GO

CREATE TABLE ExperienciaLaboral_det (
    idExperiencia_det INT IDENTITY(1,1) PRIMARY KEY,
    idExperiencia_enc INT NOT NULL,
    Cargo NVARCHAR(100),
    FechaInicio DATE,
    FechaFin DATE,
    Descripcion NVARCHAR(250),
    Funciones NVARCHAR(MAX),
    Logros NVARCHAR(MAX),
    FOREIGN KEY (idExperiencia_enc) REFERENCES ExperienciaLaboral_enc(idExperiencia_enc)
        ON DELETE CASCADE ON UPDATE CASCADE
);
GO

-------------------------------------------------------
-- TABLAS: Estudios Realizados
-------------------------------------------------------
CREATE TABLE EstudiosRealizados_enc (
    idEstudiosRealizados INT IDENTITY(1,1) PRIMARY KEY,
    idCandidato INT NOT NULL,
    NombreEstudio NVARCHAR(150),
    NivelEstudio NVARCHAR(50),
    Estado NVARCHAR(20),
    FOREIGN KEY (idCandidato) REFERENCES Candidato(idCandidato)
        ON DELETE CASCADE ON UPDATE CASCADE
);
GO

CREATE TABLE EstudiosRealizados_det (
    idEstudiosDet INT IDENTITY(1,1) PRIMARY KEY,
    idEstudiosRealizados_enc INT NOT NULL,
    Institucion NVARCHAR(150),
    DescripcionEstudio NVARCHAR(250),
    FechaInicio DATE,
    FechaFin DATE,
    EstadoEstudio NVARCHAR(50),
    FOREIGN KEY (idEstudiosRealizados_enc) REFERENCES EstudiosRealizados_enc(idEstudiosRealizados)
        ON DELETE CASCADE ON UPDATE CASCADE
);
GO

-------------------------------------------------------
-- TABLAS: Otros Conocimientos
-------------------------------------------------------
CREATE TABLE OtrosConocimientos_enc (
    idConocimientoEnc INT IDENTITY(1,1) PRIMARY KEY,
    idCandidato INT NOT NULL,
    Categoria NVARCHAR(100),
    Certificador NVARCHAR(100),
    TipoConocimiento NVARCHAR(50),
    FOREIGN KEY (idCandidato) REFERENCES Candidato(idCandidato)
        ON DELETE CASCADE ON UPDATE CASCADE
);
GO

CREATE TABLE OtrosConocimientos_det (
    idOtrosConDet INT IDENTITY(1,1) PRIMARY KEY,
    idConocimientoEnc INT NOT NULL,
    Nombre NVARCHAR(150),
    Descripcion NVARCHAR(250),
    Nivel NVARCHAR(50),
    AñosExperiencia DECIMAL(4,1),
    FOREIGN KEY (idConocimientoEnc) REFERENCES OtrosConocimientos_enc(idConocimientoEnc)
        ON DELETE CASCADE ON UPDATE CASCADE
);
GO
