from flask import (
    Blueprint,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_required
from app.models import db, Corto

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    return redirect(url_for("public.mostrar_cartelera"))


@public_bp.route("/cartelera")
def mostrar_cartelera():
    consulta = Corto.query
    busqueda = request.args.get("buscar", "").strip()

    if busqueda:
        consulta = consulta.filter(Corto.titulo.ilike(f"%{busqueda}%"))

    orden = request.cookies.get("orden_cartelera")

    cortos = consulta.all()

    return render_template(
        "catalogo.html",
        lista_cortos=cortos,
        busqueda=busqueda,
        orden_actual=orden,
    )


@public_bp.route("/corto/<int:corto_id>")
def ver_corto(corto_id):
    corto = db.get_or_404(Corto, corto_id)
    return render_template("corto_detalle.html", corto=corto)


@public_bp.route("/ordenar/<string:criterio>")
def guardar_orden(criterio):
    respuesta = make_response(redirect(url_for("public.mostrar_cartelera")))
    respuesta.set_cookie(
        "orden_cartelera",
        value=criterio,
        max_age=60 * 60 * 24 * 7,
        httponly=True,
        samesite="Lax",
    )
    return redirect(url_for("public.mostrar_cartelera"))


@public_bp.route("/limpiar-orden")
def limpiar_orden():
    respuesta = make_response(redirect(url_for("public.mostrar_cartelera")))
    respuesta.delete_cookie("orden_cartelera")
    return respuesta


@public_bp.route("/parrilla/anadir/<int:corto_id>", methods=["POST"])
@login_required
def anadir_a_parrilla(corto_id):
    corto = db.get_or_404(Corto, corto_id)
    session.permanent = True

    if "parrilla" not in session:
        session["parrilla"] = []

    session["parrilla"].append(corto.id)
    flash(f"Cortometraje '{corto.titulo}' añadido a tu parrilla.", "exito")
    return redirect(url_for("public.mostrar_cartelera"))


@public_bp.route("/parrilla")
@login_required
def ver_parrilla():
    ids_parrilla = session.get("parrilla", [])

    if ids_parrilla:
        cortos = Corto.query.filter(Corto.id.in_(ids_parrilla)).all()
    else:
        cortos = []

    minutos_totales = 0
    minutos_restantes = 90

    return render_template(
        "parrilla.html",
        cortos=cortos,
        minutos_totales=minutos_totales,
        minutos_restantes=minutos_restantes,
    )


@public_bp.route("/parrilla/quitar/<int:corto_id>", methods=["POST"])
@login_required
def quitar_de_parrilla(corto_id):
    parrilla = session.get("parrilla", [])

    if corto_id in parrilla:
        parrilla.remove(corto_id)
        session.modified = True
        flash("Cortometraje retirado de tu parrilla de visionado.", "info")

    return redirect(url_for("public.ver_parrilla"))


@public_bp.route("/parrilla/votar", methods=["POST"])
@login_required
def votar_parrilla():
    return redirect(url_for("public.mostrar_cartelera"))