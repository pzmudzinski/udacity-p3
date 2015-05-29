__author__ = 'piotr'
from .models import *
from httplib import NOT_FOUND, BAD_REQUEST
from flask import render_template, request, Blueprint, jsonify, redirect, flash
from .forms import *

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
    category = CatalogDAO.category_with_id(category_id)
    if category is None:
        return jsonify({
            "error": "Category could not be found."
        }), NOT_FOUND

    return jsonify(category_schema.dump(category).data)

@blueprint_api.route('/item/<item_id>')
def get_item(item_id):
    print request.path
    item = Item.query.get(item_id)
    if item is None:
        return jsonify({
            "error": "Item could not be found."
        }), NOT_FOUND

    return jsonify(item_schema.dump(item).data)


# WEB
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
        form_category = CatalogDAO.category_with_id(form.category.data)
        form_item = Item(form.name.data, form.description.data)
        form_category.add_item(form_item)
        return redirect(url_for('catalog.home'))

    return render_template('add_item.html', form=form, action="Add")

@blueprint_catalog.route('/item/<item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    form_item = CatalogDAO.item_with_id(item_id)
    form = AddItemForm()
    form.name = form_item.name
    form.category.data = form_item.category.name
    form.description = form.description

    if form.is_submitted():
        session_commit()

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