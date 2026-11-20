from flask import Flask, render_template
from app.config import Config
from app.models import db, login_manager, Corto, Usuario
from flask_debugtoolbar import DebugToolbarExtension


def create_app(config_class=Config):
    """Factoría de aplicaciones de DAW-Fest."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    DebugToolbarExtension(app)

    from app.blueprints.public import public_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    @app.errorhandler(403)
    def acceso_prohibido(e):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def pagina_no_encontrada(e):
        return render_template("404.html"), 404

    with app.app_context():
        db.create_all()

        if not Corto.query.first():
            cortos_iniciales = [
                Corto(
                    titulo="El Último Fotograma",
                    codigo_ficha="FEST-01",
                    genero="Drama",
                    duracion_min=25,
                    votos=5,
                    en_cartelera=True,
                ),
                Corto(
                    titulo="Órbita Silenciosa",
                    codigo_ficha="FEST-02",
                    genero="Sci-Fi",
                    duracion_min=40,
                    votos=2,
                    en_cartelera=True,
                ),
                Corto(
                    titulo="Sombras de Papel",
                    codigo_ficha="FEST-03",
                    genero="Animación",
                    duracion_min=35,
                    votos=0,
                    en_cartelera=True,
                ),
                Corto(
                    titulo="Crónicas del Subsuelo",
                    codigo_ficha="FEST-04",
                    genero="Sci-Fi",
                    duracion_min=45,
                    votos=0,
                    en_cartelera=False,
                ),
            ]
            db.session.add_all(cortos_iniciales)
            db.session.commit()

        if not Usuario.query.first():
            organizador = Usuario(
                username="org_festival",
                email="organizador@dawfest.com",
                especialidad="Dirección Artística",
                rol="organizador",
            )
            organizador.set_password("org123")

            jurado = Usuario(
                username="jurado_elena",
                email="jurado@dawfest.com",
                especialidad="Guion y Montaje",
                rol="jurado",
            )
            jurado.set_password("jurado123")

            db.session.add_all([organizador, jurado])
            db.session.commit()

    return app
