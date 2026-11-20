import os
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import current_user
from werkzeug.utils import secure_filename
from app.models import db, login_manager, Corto
from app.forms import CortoForm

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.before_request
def verificar_permisos_organizador():
    if not current_user.is_authenticated:
        return login_manager.unauthorized()
    if not current_user.es_organizador:
        abort(403)


@admin_bp.route("/corto/nuevo", methods=["GET", "POST"])
def crear_corto():
    form = CortoForm()

    if form.validate_on_submit():
        nombre_imagen = None

        if form.archivo_cartel.data:
            archivo = form.archivo_cartel.data
            nombre_imagen = secure_filename(
                form.codigo_ficha.data.upper() + "_" + archivo.filename
            )
            carpeta_subidas = current_app.config["UPLOAD_FOLDER"]
            os.makedirs(carpeta_subidas, exist_ok=True)
            archivo.save(os.path.join(carpeta_subidas, nombre_imagen))

        nuevo_corto = Corto(
            titulo=form.titulo.data,
            codigo_ficha=form.codigo_ficha.data,
            genero=form.genero.data,
            duracion_min=form.duracion_min.data,
            en_cartelera=form.en_cartelera.data,
            cartel=nombre_imagen,
        )

        db.session.add(nuevo_corto)
        db.session.commit()
        flash("Cortometraje registrado en la sección oficial.", "exito")
        return redirect(url_for("public.mostrar_cartelera"))

    return render_template(
        "corto_form.html",
        form=form,
        titulo="Registrar Nuevo Cortometraje",
    )


@admin_bp.route("/corto/<int:corto_id>/editar", methods=["GET", "POST"])
def editar_corto(corto_id):
    corto = db.get_or_404(Corto, corto_id)
    form = CortoForm(obj=corto)
    form.id_actual = corto.codigo_ficha

    if form.validate_on_submit():
        corto.titulo = form.titulo.data
        corto.codigo_ficha = form.codigo_ficha.data
        corto.genero = form.genero.data
        corto.en_cartelera = form.en_cartelera.data
        corto.duracion_min = form.duracion_min.data

        if form.archivo_cartel.data:
            archivo = form.archivo_cartel.data
            nombre_imagen = secure_filename(
                form.codigo_ficha.data.upper() + "_" + archivo.filename
            )
            carpeta_subidas = current_app.config["UPLOAD_FOLDER"]
            os.makedirs(carpeta_subidas, exist_ok=True)
            archivo.save(os.path.join(carpeta_subidas, nombre_imagen))

            if corto.cartel and corto.cartel != nombre_imagen:
                ruta_antigua = os.path.join(carpeta_subidas, corto.cartel)
                if os.path.exists(ruta_antigua):
                    os.remove(ruta_antigua)

            corto.cartel = nombre_imagen

        db.session.commit()
        flash("Ficha del cortometraje actualizada con éxito.", "exito")
        return redirect(url_for("public.mostrar_cartelera"))

    return render_template(
        "corto_form.html",
        form=form,
        titulo="Editar Cortometraje",
        corto=corto,
    )


@admin_bp.route("/corto/<int:corto_id>/eliminar", methods=["POST"])
def eliminar_corto(corto_id):
    corto = db.get_or_404(Corto, corto_id)
    if corto.votos > 0:
        flash("No se puede eliminar cortos con votos", "error")
        return redirect(url_for("public.mostrar_cartelera"))
    if corto.cartel:
        ruta = os.path.join(current_app.config["UPLOAD_FOLDER"], corto.cartel)
        if os.path.exists(ruta):
            os.remove(ruta)
    db.session.delete(corto)
    db.session.commit()
    flash(f"Cortometraje '{corto.titulo}' eliminado del catálogo.", "info")
    return redirect(url_for("public.mostrar_cartelera"))


@admin_bp.route("/admin/corto/<int:corto_id>/estado", methods=["POST"])
def alternarEstado(corto_id):
    corto = db.get_or_404(Corto, corto_id)
    if corto.en_cartelera:
        corto.en_cartelera = False
        flash("El corto paso a la cartelera.", "exito")
    else:
        corto.en_cartelera = True
        flash("El corto se retiró de la cartelera.", "exito")
    db.session.commit()
    return redirect(url_for("public.mostrar_cartelera"))
