__author__ = 'piotr'
from .models import *
from httplib import NOT_FOUND, BAD_REQUEST
from flask import render_template, request, Blueprint, jsonify, redirect, flash, g
from .forms import *
from flask.ext.login import login_user, logout_user, current_user, login_required
from auth import *
from app import app

blueprint_catalog = Blueprint('catalog', __name__, url_prefix="/catalog")
blueprint_api = Blueprint('api', __name__, url_prefix='/api')
category_schema = CategorySchema()
item_schema = ItemSchema()

# API

@blueprint_api.route('/categories.json')
def get_all_categories():
    pass

@blueprint_api.route('/category/<category_id>')
def get_category(category_id):
    print request.path
    _category = CatalogDAO.category_with_id(category_id)
    if _category is None:
        return jsonify({
            "error": "Category could not be found."
        }), NOT_FOUND

    return jsonify(category_schema.dump(_category).data)

@blueprint_api.route('/item/<item_id>')
def get_item(item_id):
    print request.path
    _item = Item.query.get(item_id)
    if _item is None:
        return jsonify({
            "error": "Item could not be found."
        }), NOT_FOUND

    return jsonify(item_schema.dump(_item).data)


# WEB
@blueprint_catalog.before_request
def before_request():
    g.user = current_user

@blueprint_catalog.context_processor
def utility_processor():
    return dict(
        categories=CatalogDAO.all_categories()
    )


@blueprint_catalog.route('/')
def home():
    return render_template(
        'index.html',
        items=CatalogDAO.latest_items()
    )


@blueprint_catalog.route('/category/<category_id>')
def category(category_id):
    cat = CatalogDAO.category_with_id(category_id, True)
    items = cat.get_all_items()
    return render_template(
        'category.html',
        category=cat,
        items=items,
        number_of_items=len(items)
    )


@blueprint_catalog.route('/item/<item_id>')
def item(item_id):
    return render_template(
        'item.html',
        item=CatalogDAO.item_with_id(item_id)
    )

@blueprint_catalog.route('/item', methods=['GET', 'POST'])
def add_item():
    form = AddItemForm()

    if form.validate_on_submit():
        form_category = CatalogDAO.category_with_id(form.category_id.data)
        form_item = Item(form.name.data, form.description.data)
        form_category.add_item(form_item)
        return redirect(url_for('catalog.home'))

    return render_template('add_item.html', form=form, action="Add")

@blueprint_catalog.route('/item/<item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    form_item = CatalogDAO.item_with_id(item_id)
    form = AddItemForm(obj=form_item)

    if form.validate_on_submit():
        print form
        form.populate_obj(form_item)
        session_commit()
        return redirect(url_for('.item', item_id=item_id))

    return render_template('add_item.html', form=form, action="Edit")

@blueprint_catalog.route('/item/<item_id>/delete',  methods=['GET', 'POST'])
def delete_item(item_id):
    delete_form = DeleteItemForm()
    delete_form.id = item_id
    delete_form.name = CatalogDAO.item_with_id(item_id).name

    if delete_form.is_submitted():
        CatalogDAO.delete_item(item_id)
        return redirect(url_for('catalog.home'))

    return render_template('delete_item.html', form=delete_form)

@blueprint_catalog.route('/category', methods=['GET', 'POST'])
def add_category():
    form = AddCategoryForm()

    if form.validate_on_submit():
        form_category = Category(form.name.data)
        try:
            CatalogDAO.add_category(form_category)
        except ValueError, e:
            flash('Category with the same name already exists!')
        return redirect(url_for('catalog.home'))

    return render_template('add_category.html', form=form, action="Add")

@blueprint_catalog.route('/delete_category', methods=['GET', 'POST'])
def delete_category():
    form = DeleteCategoryForm()

    if form.is_submitted():
        CatalogDAO.delete_category_with_id(form.category.data)
        return redirect(url_for('catalog.home'))

    return render_template('delete_category.html', form=form)

@blueprint_catalog.route('/login')
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('.home'))
    return render_template('login.html')

@blueprint_catalog.route('/authorize/<provider>')
def oauth_authorize(provider):
    # Flask-Login function
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    username, email = oauth.callback()
    if email is None:
        # I need a valid email address for my user identification
        flash('Authentication failed.')
        return redirect(url_for('index'))
    # Look if the user already exists
    user=User.query.filter_by(email=email).first()
    if not user:
        # Create the user. Try and use their name returned by Google,
        # but if it is not set, split the email address at the @.
        nickname = username
        if nickname is None or nickname == "":
            nickname = email.split('@')[0]

        # We can do more work here to ensure a unique nickname, if you
        # require that.
        user=User(nickname=nickname, email=email)
        db.session.add(user)
        db.session.commit()
    # Log in the user, by default remembering them for their next visit
    # unless they log out.
    login_user(user, remember=True)
    return redirect(url_for('index'))