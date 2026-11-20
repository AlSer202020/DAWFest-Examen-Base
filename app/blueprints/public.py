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
    busqueda = request.args.get("q", "").strip()

    if busqueda:
        consulta = consulta.filter(Corto.titulo.ilike(f"%{busqueda}%"))

    orden = request.cookies.get("orden_cartelera")

    if orden == "duracion":
        cortos = consulta.order_by(Corto.duracion_min.desc()).all()
    elif orden == "votos":
        cortos = consulta.order_by(Corto.votos.desc()).all()
    else:
        cortos = consulta.all()

    return render_template(
        "cartelera.html",
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
        criterio,
        max_age=60 * 60 * 24 * 7,
        httponly=True,
        samesite="Lax",
    )
    return respuesta


@public_bp.route("/limpiar-orden")
def limpiar_orden():
    respuesta = make_response(redirect(url_for("public.mostrar_cartelera")))
    respuesta.delete_cookie("orden_cartelera")
    return respuesta


@public_bp.route("/parrilla/anadir/<int:corto_id>", methods=["POST"])
@login_required
def anadir_a_parrilla(corto_id):
    corto = db.get_or_404(Corto, corto_id)
    if corto.en_cartelera == False:
        flash(
            "El cortometraje debe estar en la cartelera para añadirlo a la parrilla",
            "error",
        )
        return redirect(url_for("public.mostrar_cartelera"))

    session.permanent = True
    parrilla = session.get("parrilla", [])
    cortos = Corto.query.filter(Corto.id.in_(parrilla)).all()
    duracion_total = 0
    for corto_parrilla in cortos:
        duracion_total += corto_parrilla.duracion_min

    if duracion_total + corto.duracion_min > 90:
        flash("La duración de los cortos no puede superar 90 minutos", "error")
        return redirect(url_for("public.mostrar_cartelera"))

    if corto.id in parrilla:
        flash("Este cortometraje ya está en la parrilla", "error")
        return redirect(url_for("public.mostrar_cartelera"))

    parrilla.append(corto.id)
    session["parrilla"] = parrilla
    session.modified = True
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

    cortos = Corto.query.filter(Corto.id.in_(ids_parrilla)).all()
    for corto_parrilla in cortos:
        minutos_totales += corto_parrilla.duracion_min

    minutos_restantes -= minutos_totales

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
    ids_parrilla = session.get("parrilla", [])
    cortos = Corto.query.filter(Corto.id.in_(ids_parrilla)).all()
    for corto in cortos:
        corto.votos += 1
        db.session.commit()
    session.pop("parrilla", None)
    return redirect(url_for("public.mostrar_cartelera"))
