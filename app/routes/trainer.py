from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, abort, request, current_app
)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

from app import db
from app.models.user import User
from app.models.note import TrainerNote
from app.utils.decorators import role_required
from app.utils.logger import get_audit_logger

trainer_bp = Blueprint('trainer', __name__)
audit = get_audit_logger()


class NoteForm(FlaskForm):
    member_id = SelectField('Member', coerce=int, validators=[DataRequired()])
    category = SelectField(
        'Category',
        choices=[(c, c.title()) for c in TrainerNote.CATEGORY_CHOICES],
        validators=[DataRequired()]
    )
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=150)])
    body = TextAreaField('Details', validators=[DataRequired(), Length(min=2, max=5000)])
    submit = SubmitField('Save Note')


def _member_choices():
    members = (
        User.query
        .filter_by(role='member', is_active_account=True)
        .order_by(User.full_name.asc())
        .all()
    )
    return [(m.id, f'{m.full_name} ({m.email})') for m in members]


@trainer_bp.route('/notes')
@login_required
@role_required('trainer', 'admin')
def notes_list():
    member_id = request.args.get('member_id', type=int)

    q = TrainerNote.query
    if member_id:
        q = q.filter_by(member_id=member_id)
    notes = q.order_by(TrainerNote.created_at.desc()).limit(200).all()

    member = db.session.get(User, member_id) if member_id else None

    return render_template(
        'trainer/notes_list.html',
        notes=notes,
        member=member,
        member_choices=_member_choices(),
        member_id=member_id,
    )


@trainer_bp.route('/notes/new', methods=['GET', 'POST'])
@login_required
@role_required('trainer', 'admin')
def note_create():
    form = NoteForm()
    form.member_id.choices = _member_choices()

    preselect = request.args.get('member_id', type=int)
    if request.method == 'GET' and preselect:
        form.member_id.data = preselect

    if form.validate_on_submit():
        member = db.session.get(User, form.member_id.data)
        if member is None or member.role != 'member':
            abort(400)

        note = TrainerNote(
            member_id=member.id,
            author_id=current_user.id,
            category=form.category.data,
            title=form.title.data.strip(),
            body=form.body.data.strip(),
        )

        try:
            db.session.add(note)
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception('NOTE_CREATE_FAILED member_id=%s', member.id)
            flash('Could not save note.', 'danger')
            return render_template('trainer/note_form.html', form=form), 500

        audit.info('NOTE_CREATED note_id=%s member_id=%s by=%s',
                   note.id, member.id, current_user.email)
        flash('Note saved.', 'success')
        return redirect(url_for('trainer.notes_list', member_id=member.id))

    return render_template('trainer/note_form.html', form=form)


@trainer_bp.route('/notes/<int:note_id>', methods=['GET', 'POST'])
@login_required
@role_required('trainer', 'admin')
def note_edit(note_id: int):
    note = db.session.get(TrainerNote, note_id)
    if note is None:
        abort(404)

    form = NoteForm(obj=note)
    form.member_id.choices = _member_choices()

    if form.validate_on_submit():
        member = db.session.get(User, form.member_id.data)
        if member is None or member.role != 'member':
            abort(400)

        note.member_id = member.id
        note.category = form.category.data
        note.title = form.title.data.strip()
        note.body = form.body.data.strip()

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception('NOTE_UPDATE_FAILED note_id=%s', note.id)
            flash('Could not update note.', 'danger')
            return render_template('trainer/note_form.html', form=form, note=note), 500

        audit.info('NOTE_UPDATED note_id=%s member_id=%s by=%s',
                   note.id, member.id, current_user.email)
        flash('Note updated.', 'success')
        return redirect(url_for('trainer.notes_list', member_id=member.id))

    return render_template('trainer/note_form.html', form=form, note=note)


@trainer_bp.route('/notes/<int:note_id>/delete', methods=['POST'])
@login_required
@role_required('trainer', 'admin')
def note_delete(note_id: int):
    note = db.session.get(TrainerNote, note_id)
    if note is None:
        abort(404)

    member_id = note.member_id
    try:
        db.session.delete(note)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception('NOTE_DELETE_FAILED note_id=%s', note_id)
        flash('Could not delete note.', 'danger')
        return redirect(url_for('trainer.notes_list'))

    audit.info('NOTE_DELETED note_id=%s member_id=%s by=%s',
               note_id, member_id, current_user.email)
    flash('Note deleted.', 'info')
    return redirect(url_for('trainer.notes_list', member_id=member_id))