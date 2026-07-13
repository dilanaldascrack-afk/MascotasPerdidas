import os
import base64
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from config import Config
from models import db, Pet
from datetime import datetime, date

app = Flask(__name__)
app.config.from_object(Config)

# Init DB
db.init_app(app)

def process_photo(file):
    """Convert photo to Base64 string."""
    try:
        file_content = file.read()
        # Determine format based on filename
        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext == 'jpg': ext = 'jpeg'
        
        encoded = base64.b64encode(file_content).decode("utf-8")
        return f"data:image/{ext};base64,{encoded}"
    except Exception as e:
        print(f"Error encoding photo: {e}")
        return None


# ────────────────────────────────────────────────
# Routes
# ────────────────────────────────────────────────

@app.route("/")
def index():
    """Homepage with featured recent pets."""
    recent_lost = (
        Pet.query.filter_by(status="perdido", is_resolved=False)
        .order_by(Pet.created_at.desc())
        .limit(6)
        .all()
    )
    recent_found = (
        Pet.query.filter_by(status="encontrado", is_resolved=False)
        .order_by(Pet.created_at.desc())
        .limit(6)
        .all()
    )
    total_lost = Pet.query.filter_by(status="perdido", is_resolved=False).count()
    total_found = Pet.query.filter_by(status="encontrado", is_resolved=False).count()
    total_resolved = Pet.query.filter_by(is_resolved=True).count()

    return render_template(
        "index.html",
        recent_lost=recent_lost,
        recent_found=recent_found,
        total_lost=total_lost,
        total_found=total_found,
        total_resolved=total_resolved,
    )


@app.route("/buscar")
def search():
    """Search/filter pets."""
    # Filters from query params
    status = request.args.get("status", "")
    species = request.args.get("species", "")
    city = request.args.get("city", "")
    size = request.args.get("size", "")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    color = request.args.get("color", "")
    page = request.args.get("page", 1, type=int)

    query = Pet.query.filter_by(is_resolved=False)

    if status:
        query = query.filter(Pet.status == status)
    if species:
        query = query.filter(Pet.species == species)
    if city:
        query = query.filter(Pet.city.ilike(f"%{city}%"))
    if size:
        query = query.filter(Pet.size == size)
    if color:
        query = query.filter(Pet.color.ilike(f"%{color}%"))
    if date_from:
        try:
            dt_from = datetime.strptime(date_from, "%Y-%m-%d").date()
            query = query.filter(Pet.last_seen_date >= dt_from)
        except ValueError:
            pass
    if date_to:
        try:
            dt_to = datetime.strptime(date_to, "%Y-%m-%d").date()
            query = query.filter(Pet.last_seen_date <= dt_to)
        except ValueError:
            pass

    pets = query.order_by(Pet.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )

    # Get distinct cities for filter dropdown
    cities = (
        db.session.query(Pet.city).distinct().order_by(Pet.city).all()
    )
    cities = [c[0] for c in cities if c[0]]

    return render_template(
        "search.html",
        pets=pets,
        cities=cities,
        filters={
            "status": status,
            "species": species,
            "city": city,
            "size": size,
            "date_from": date_from,
            "date_to": date_to,
            "color": color,
        },
    )


@app.route("/mascota/<int:pet_id>")
def pet_detail(pet_id):
    """Pet detail page."""
    pet = Pet.query.get_or_404(pet_id)
    return render_template("pet_detail.html", pet=pet)


@app.route("/reportar", methods=["GET", "POST"])
def report():
    """Report a lost or found pet."""
    if request.method == "POST":
        # Get form data
        name = request.form.get("name", "").strip() or None
        species = request.form.get("species", "").strip()
        breed = request.form.get("breed", "").strip() or None
        color = request.form.get("color", "").strip() or None
        size = request.form.get("size", "").strip() or None
        age_estimate = request.form.get("age_estimate", "").strip() or None
        gender = request.form.get("gender", "").strip() or None
        status = request.form.get("status", "perdido").strip()
        city = request.form.get("city", "").strip()
        neighborhood = request.form.get("neighborhood", "").strip() or None
        last_seen_address = request.form.get("last_seen_address", "").strip() or None
        last_seen_date_str = request.form.get("last_seen_date", "").strip()
        description = request.form.get("description", "").strip() or None
        has_collar = bool(request.form.get("has_collar"))
        has_chip = bool(request.form.get("has_chip"))
        contact_name = request.form.get("contact_name", "").strip()
        contact_phone = request.form.get("contact_phone", "").strip()
        contact_email = request.form.get("contact_email", "").strip() or None
        reward = request.form.get("reward", "").strip() or None

        # Validation
        errors = []
        if not species:
            errors.append("La especie es requerida.")
        if not city:
            errors.append("La ciudad es requerida.")
        if not contact_name:
            errors.append("Tu nombre es requerido.")
        if not contact_phone:
            errors.append("Tu teléfono de contacto es requerido.")
        if not last_seen_date_str:
            errors.append("La fecha es requerida.")

        last_seen_date = None
        if last_seen_date_str:
            try:
                last_seen_date = datetime.strptime(last_seen_date_str, "%Y-%m-%d").date()
            except ValueError:
                errors.append("Formato de fecha inválido.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("report.html", form_data=request.form)

        # Upload photo
        photo_data = None
        photo_file = request.files.get("photo")
        if photo_file and photo_file.filename:
            allowed = {"png", "jpg", "jpeg", "gif", "webp"}
            ext = photo_file.filename.rsplit(".", 1)[-1].lower()
            if ext in allowed:
                photo_data = process_photo(photo_file)
            else:
                flash("Formato de imagen no válido. Usa PNG, JPG, GIF o WEBP.", "error")
                return render_template("report.html", form_data=request.form)

        # Create pet record
        pet = Pet(
            name=name,
            species=species,
            breed=breed,
            color=color,
            size=size,
            age_estimate=age_estimate,
            gender=gender,
            status=status,
            city=city,
            neighborhood=neighborhood,
            last_seen_address=last_seen_address,
            last_seen_date=last_seen_date,
            description=description,
            has_collar=has_collar,
            has_chip=has_chip,
            contact_name=contact_name,
            contact_phone=contact_phone,
            contact_email=contact_email,
            reward=reward,
            photo_data=photo_data,
        )
        db.session.add(pet)
        db.session.commit()

        flash("¡Reporte publicado exitosamente! Esperamos que encuentres a tu mascota pronto. 🐾", "success")
        return redirect(url_for("pet_detail", pet_id=pet.id))

    return render_template("report.html", form_data={})


@app.route("/mascota/<int:pet_id>/resolver", methods=["POST"])
def mark_resolved(pet_id):
    """Mark a pet as found/resolved."""
    pet = Pet.query.get_or_404(pet_id)
    pet.is_resolved = True
    db.session.commit()
    flash("¡Qué alegría! Marcaste este caso como resuelto. 🎉", "success")
    return redirect(url_for("index"))


@app.route("/api/stats")
def api_stats():
    """Simple stats API endpoint."""
    return jsonify({
        "total_lost": Pet.query.filter_by(status="perdido", is_resolved=False).count(),
        "total_found": Pet.query.filter_by(status="encontrado", is_resolved=False).count(),
        "total_resolved": Pet.query.filter_by(is_resolved=True).count(),
        "total": Pet.query.count(),
    })


# ────────────────────────────────────────────────
# Init DB tables on first request
# ────────────────────────────────────────────────
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=False)
