from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Inicia sesión con tu acreditación para acceder a esta zona."
login_manager.login_message_category = "info"


class Corto(db.Model):
    __tablename__ = "cortos"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(db.String(100), nullable=False)
    codigo_ficha: Mapped[str] = mapped_column(db.String(20), unique=True, nullable=False)
    genero: Mapped[str] = mapped_column(db.String(50), nullable=False)
    duracion_min: Mapped[int] = mapped_column(db.Integer, nullable=False)
    votos: Mapped[int] = mapped_column(db.Integer, default=0, nullable=False)
    en_cartelera: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)
    cartel: Mapped[str | None] = mapped_column(db.String(200), nullable=True)

    def __repr__(self) -> str:
        return f"Corto {self.codigo_ficha}: {self.titulo} ({self.duracion_min} min)"


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    especialidad: Mapped[str] = mapped_column(db.String(40), default="General", nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(256), nullable=False)
    rol: Mapped[str] = mapped_column(db.String(20), default="jurado", nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def es_organizador(self) -> bool:
        return self.rol == "admin"

    def __repr__(self) -> str:
        return f"Usuario id={self.id}: {self.username} ({self.rol})"


@login_manager.user_loader
def cargar_usuario(user_id: str):
    return db.session.get(Usuario, int(user_id))