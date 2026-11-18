from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    BooleanField,
    IntegerField,
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    ValidationError,
)
from app.models import Corto, Usuario


class LoginForm(FlaskForm):
    """Formulario de acceso para miembros del jurado y organizadores."""

    email = StringField(
        "Correo Electrónico",
        validators=[
            DataRequired(message="Introduce tu correo electrónico."),
            Email(message="Formato de correo no válido."),
        ],
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="Introduce tu contraseña.")],
    )
    remember = BooleanField("Mantener sesión iniciada")
    submit = SubmitField("Entrar al Festival")


class CortoForm(FlaskForm):
    """Formulario para registrar y editar cortometrajes."""

    titulo = StringField(
        "Título del Cortometraje",
        validators=[
            DataRequired(message="El título es obligatorio."),
            Length(min=3, max=100, message="Entre 3 y 100 caracteres."),
        ],
    )
    codigo_ficha = StringField(
        "Código de Ficha (ej. FEST-01)",
        validators=[
            DataRequired(message="El código de ficha es obligatorio."),
            Length(min=5, max=20, message="Entre 5 y 20 caracteres."),
        ],
    )
    genero = StringField(
        "Género Cinematográfico (ej. Drama, Sci-Fi, Animación)",
        validators=[
            DataRequired(message="El género es obligatorio."),
            Length(min=3, max=50, message="Entre 3 y 50 caracteres."),
        ],
    )
    duracion_min = IntegerField(
        "Duración (minutos)",
        default=20,
        validators=[
            DataRequired(message="Indica la duración en minutos."),
            NumberRange(min=1, max=90, message="La duración debe estar entre 1 y 90 minutos."),
        ],
    )
    en_cartelera = BooleanField("Proyección activa en cartelera", default=True)
    archivo_cartel = FileField(
        "Póster Oficial (JPG, PNG)",
        validators=[
            FileAllowed(["jpg", "jpeg", "png"], "Solo se permiten imágenes (JPG, PNG).")
        ],
    )
    submit = SubmitField("Guardar Cortometraje")


class RegistroForm(FlaskForm):
    """Formulario de acreditación para nuevos miembros del jurado."""

    username = StringField(
        "Nombre de Usuario",
        validators=[
            DataRequired(message="El nombre de usuario es obligatorio."),
            Length(min=3, max=50, message="Debe tener entre 3 y 50 caracteres."),
        ],
    )
    email = StringField(
        "Correo Electrónico",
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Introduce un correo válido."),
        ],
    )
    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(min=6, message="Mínimo 6 caracteres."),
        ],
    )
    confirm_password = PasswordField(
        "Confirmar Contraseña",
        validators=[
            DataRequired(message="Confirma tu contraseña."),
            EqualTo("password", message="Las contraseñas no coinciden."),
        ],
    )
    submit = SubmitField("Solicitar Acreditación de Jurado")

    def validate_username(self, field):
        if Usuario.query.filter_by(username=field.data).first():
            raise ValidationError("Ese nombre de usuario ya está acreditado.")

    def validate_email(self, field):
        if Usuario.query.filter_by(email=field.data).first():
            raise ValidationError("Ese correo electrónico ya está registrado.")