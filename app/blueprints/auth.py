from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app.models import db, Usuario
from app.forms import LoginForm, RegistroForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.mostrar_cartelera"))

    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and usuario.check_password(form.password.data):
            login_user(usuario, remember=form.remember.data)
            flash(f"¡Bienvenido al festival, {usuario.username}!", "exito")

            siguiente_pagina = request.args.get("next")
            if siguiente_pagina and siguiente_pagina.startswith("/"):
                return redirect(siguiente_pagina)
            return redirect(url_for("public.mostrar_cartelera"))
        else:
            flash("Correo electrónico o contraseña incorrectos.", "error")

    return render_template("login.html", form=form)


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for("public.mostrar_cartelera"))

    form = RegistroForm()
    if form.validate_on_submit():
        nuevo_jurado = Usuario(
            username=form.username.data,
            email=form.email.data,
            rol="jurado",
            especialidad=form.especialidad.data,
        )
        nuevo_jurado.set_password(form.password.data)

        db.session.add(nuevo_jurado)
        db.session.commit()
        flash("Acreditación registrada con éxito. Ya puedes iniciar sesión.", "exito")
        return redirect(url_for("auth.login"))

    return render_template("registro.html", form=form)


@auth_bp.route("/perfil")
@login_required
def perfil():
    return render_template("perfil.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop("parilla", None)
    flash("Has cerrado tu sesión en el festival.", "info")
    return redirect(url_for("public.mostrar_cartelera"))
