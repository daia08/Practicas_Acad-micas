CREATE TABLE "DBA"."listas_oferta" (
	"barras" CHAR(13) NOT NULL,
	"precio" DECIMAL(12,2) NULL,
	"operador" CHAR(15) NULL,
	"fecha_inicio" DATE NOT NULL,
	"fecha_fin" DATE NULL,
	"observaciones" CHAR(35) NULL,
	"fecha" DATE NULL DEFAULT CURRENT DATE,
	"hora" TIME NULL DEFAULT CURRENT TIME,
	"vigente" CHAR(1) NOT NULL,
	"clase" INTEGER NOT NULL,
	PRIMARY KEY ( "barras" ASC, "fecha_inicio" ASC, "vigente" ASC, "clase" ASC )
) IN "system";
COMMENT ON COLUMN "DBA"."listas_oferta"."vigente" IS 'Novedad Activa';

CREATE TABLE "DBA"."fac_descuentos" (
	"codigo" INTEGER NOT NULL,
	"fecha_inicio" DATE NOT NULL,
	"fecha_fin" DATE NOT NULL,
	"porcentaje" NUMERIC(4,2) NOT NULL,
	"dias" INTEGER NOT NULL,
	"habilitada" CHAR(1) NOT NULL,
	"fecha_alta" DATE NOT NULL,
	"incluyendo_total_detalle" INTEGER NULL,
	"acumulativa" INTEGER NULL,
	PRIMARY KEY ( "codigo" ASC )
) IN "system";

CREATE TABLE "DBA"."fac_descuentos_conceptos" (
	"codigo" INTEGER NOT NULL,
	"descripcion" VARCHAR(50) NULL,
	"descri_corta" CHAR(5) NULL,
	PRIMARY KEY ( "codigo" ASC )
) IN "system";

CREATE TABLE "DBA"."fac_descuentos_detalle_aplicacion" (
	"codigo" INTEGER NOT NULL,
	"item" INTEGER NOT NULL,
	"seccion" NUMERIC(5,0) NULL,
	"departamento" NUMERIC(5,0) NULL,
	"grupo" NUMERIC(5,0) NULL,
	"marca" NUMERIC(5,0) NULL,
	"articulo" NUMERIC(6,0) NULL,
	"porcentaje" NUMERIC(5,2) NULL,
	PRIMARY KEY ( "codigo" ASC, "item" ASC )
) IN "system";

CREATE TABLE "DBA"."articulos" (
	"codigo" DECIMAL(6,0) NOT NULL DEFAULT 0,
	"barras" VARCHAR(13) NOT NULL,
	"enganchado" CHAR(1) NOT NULL DEFAULT '0',
	"descripcion" CHAR(50) NULL DEFAULT 'ARTICULO S/DESCRIPCION',
	"descripcion_corta" CHAR(35) NULL DEFAULT 'DESCRI CORTA',
	"margen_venta_porce" DECIMAL(4,2) NOT NULL DEFAULT 0,
	"impuesto_interno_porce" DECIMAL(4,2) NOT NULL DEFAULT 0,
	"habilitado_sn" CHAR(1) NOT NULL DEFAULT 'S',
	"modalidad_factura" CHAR(2) NOT NULL DEFAULT 'X',
	"imagen_articulo" CHAR(100) NOT NULL DEFAULT 'c:\\Sistemas\\Graficos\\Productos',
	"unidades" DECIMAL(12,2) NOT NULL DEFAULT 0,
	"id_iva" DECIMAL(1,0) NOT NULL DEFAULT 1,
	"id_marca" DECIMAL(6,0) NOT NULL DEFAULT 0,
	"id_seccion" DECIMAL(2,0) NOT NULL DEFAULT 0,
	"id_departamento" DECIMAL(5,0) NOT NULL DEFAULT 0,
	"id_rubro" DECIMAL(4,0) NOT NULL DEFAULT 0,
	"id_grupo" NUMERIC(5,0) NOT NULL DEFAULT 0,
	PRIMARY KEY ( "barras" ASC )
) IN "system";
COMMENT ON COLUMN "DBA"."articulos"."impuesto_interno_porce" IS '% impuesto interno';
COMMENT ON COLUMN "DBA"."articulos"."id_iva" IS '0 exento; 1- (21%); 2-(10.5%)';

CREATE TABLE "DBA"."secciones" (
	"codigo" NUMERIC(5,0) NOT NULL,
	"descripcion" CHAR(35) NULL,
	"rubro" NUMERIC(2,0) NOT NULL,
	"seccion_contab" NUMERIC(3,0) NULL,
	"habil" CHAR(1) NULL,
	"sucursal" INTEGER NULL,
	"es_viajante" CHAR(1) NOT NULL DEFAULT '0',
	PRIMARY KEY ( "codigo" ASC, "rubro" ASC )
) IN "system";

CREATE TABLE "DBA"."departamentos" (
	"codigo" NUMERIC(5,0) NOT NULL,
	"descripcion" CHAR(35) NULL,
	"seccion" NUMERIC(3,0) NOT NULL,
	"rubro" NUMERIC(2,0) NOT NULL,
	"habil" CHAR(1) NOT NULL,
	PRIMARY KEY ( "codigo" ASC, "seccion" ASC, "rubro" ASC )
) IN "system";

CREATE TABLE "DBA"."grupos" (
	"codigo" NUMERIC(5,0) NOT NULL,
	"descripcion" CHAR(35) NULL,
	"departamento" NUMERIC(4,0) NOT NULL,
	"seccion" NUMERIC(3,0) NOT NULL,
	"rubro" NUMERIC(2,0) NOT NULL,
	"habil" CHAR(1) NOT NULL DEFAULT 'N',
	PRIMARY KEY ( "codigo" ASC, "departamento" ASC, "seccion" ASC, "rubro" ASC )
) IN "system";

CREATE TABLE "DBA"."marcas" (
	"codigo" DECIMAL(6,0) NOT NULL,
	"descripcion" VARCHAR(30) NULL,
	"habil" CHAR(1) NULL,
	"rubro" INTEGER NOT NULL,
	"seccion" INTEGER NULL,
	PRIMARY KEY ( "codigo" ASC, "rubro" ASC )
) IN "system";
