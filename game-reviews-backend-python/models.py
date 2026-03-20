from database import db


class Estudio(db.Model):
    __tablename__ = "estudio"

    idestudio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)

    juegos = db.relationship("Juego", back_populates="estudio", cascade="all, delete")

    def to_dict(self):
        return {"idEstudio": self.idestudio, "nombre": self.nombre}


class Genero(db.Model):
    __tablename__ = "genero_juego"

    idgenero = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)

    juegos = db.relationship("Juego", back_populates="genero", cascade="all, delete")

    def to_dict(self):
        return {"idGenero": self.idgenero, "nombre": self.nombre}


class Plataforma(db.Model):
    __tablename__ = "plataforma"

    idplataforma = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)

    juegos = db.relationship("Juego", back_populates="plataforma", cascade="all, delete")

    def to_dict(self):
        return {"idPlataforma": self.idplataforma, "nombre": self.nombre}


class Juego(db.Model):
    __tablename__ = "juego"

    idjuego = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    fechalanzamiento = db.Column(db.Date)
    precio = db.Column(db.Numeric(10, 2))
    calificacionprom = db.Column(db.Numeric(3, 2))
    urlimagen = db.Column(db.Text)

    idestudio = db.Column(db.Integer, db.ForeignKey("estudio.idestudio"), nullable=False)
    idgenero = db.Column(db.Integer, db.ForeignKey("genero_juego.idgenero"), nullable=False)
    idplataforma = db.Column(db.Integer, db.ForeignKey("plataforma.idplataforma"), nullable=False)

    estudio = db.relationship("Estudio", back_populates="juegos")
    genero = db.relationship("Genero", back_populates="juegos")
    plataforma = db.relationship("Plataforma", back_populates="juegos")
    resenas = db.relationship("Resena", back_populates="juego", cascade="all, delete")

    def to_dict(self):
        return {
            "idJuego": self.idjuego,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "fechaLanzamiento": self.fechalanzamiento.isoformat() if self.fechalanzamiento else None,
            "precio": float(self.precio) if self.precio is not None else None,
            "calificacionProm": float(self.calificacionprom) if self.calificacionprom is not None else None,
            "urlImagen": self.urlimagen,
            "estudio": self.estudio.to_dict() if self.estudio else None,
            "genero": self.genero.to_dict() if self.genero else None,
            "plataforma": self.plataforma.to_dict() if self.plataforma else None,
            "resenas": [
                {"puntuacion": r.puntuacion, "comentario": r.comentario}
                for r in self.resenas
            ],
        }


class Usuario(db.Model):
    __tablename__ = "usuario"

    idusuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    contrasenahash = db.Column(db.String(255), nullable=False)
    cantidadresenas = db.Column(db.Integer, default=0)

    resenas = db.relationship("Resena", back_populates="usuario", cascade="all, delete")

    def to_dict(self):
        return {
            "idUsuario": self.idusuario,
            "nombre": self.nombre,
            "correo": self.correo,
            "cantidadResenas": self.cantidadresenas,
        }


class Resena(db.Model):
    __tablename__ = "resena"

    idresena = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comentario = db.Column(db.Text)
    puntuacion = db.Column(db.Integer, nullable=False)
    fecharesena = db.Column(db.Date)

    idusuario = db.Column(db.Integer, db.ForeignKey("usuario.idusuario"), nullable=False)
    idjuego = db.Column(db.Integer, db.ForeignKey("juego.idjuego"), nullable=False)

    usuario = db.relationship("Usuario", back_populates="resenas")
    juego = db.relationship("Juego", back_populates="resenas")

    def to_dict(self):
        return {
            "idResena": self.idresena,
            "comentario": self.comentario,
            "puntuacion": self.puntuacion,
            "fechaResena": self.fecharesena.isoformat() if self.fecharesena else None,
            "usuario": {
                "idUsuario": self.usuario.idusuario,
                "username": self.usuario.nombre,
                "avatar": None,
            } if self.usuario else None,
            "juego": {
                "idJuego": self.juego.idjuego,
                "titulo": self.juego.titulo,
                "urlImagen": self.juego.urlimagen,
            } if self.juego else None,
        }
