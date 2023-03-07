from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
import requests
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db

views = Blueprint("views", __name__)

url = "https://api.spoonacular.com/"
apiKey = "85445ed7ce8649f380d8c0fae8e3d4c0"

headers = {
    'Content-Type': "application/json",
    'x-api-key': apiKey
}

random_joke = "food/jokes/random"
find = "recipes/findByIngredients"
randomFind = "recipes/random"
getNutrients = "recipes/guessNutrition"


@views.route("/")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)


@views.route("/all-recipes")
@login_required
def all_recipes():
    posts = Post.query.all()
    return render_template("all_recipes.html", user=current_user, posts=posts)


@views.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')
        title = request.form.get('title')
        ingredients = request.form.get('ingredients')

        if not text or not title:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text, author=current_user.id,
                        title=title, ingredients=ingredients)
            db.session.add(post)
            db.session.commit()
            flash('Post created', category='success')
            return redirect("/")
    return render_template("create_post.html", user=current_user)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect('/')


@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect("/")

    posts = Post.query.filter_by(author=user.id).all()
    return render_template("user_posts.html", user=current_user, posts=posts, username=username)


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect("/all-recipes")


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect("/")


@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})


@views.route("/recipe/<post_id>", methods=['GET'])
@login_required
def recipe(post_id):
    post = Post.query.filter_by(id=post_id).first()
    title = post.title
    text = post.text
    ingredients = post.ingredients

    if not post:
        flash('Post does not exist.', category='error')
    else:
        return render_template('recipe1.html', title=title, text=text, ingredients=ingredients, user=current_user, post=post)


@views.route('/search-ingredients')
@login_required
def search_ingredients():
    return render_template('search_ingredients.html', user=current_user)


@views.route('/nutrition')
@login_required
def find_nutrition():
    return render_template('nutritional_info.html', user=current_user)


@views.route('/recipes')
@login_required
def get_recipes():
    if (str(request.args['ingridients']).strip() != ""):
        # If there is a list of ingridients -> list
        querystring = {"number": "10", "ranking": "1",
                       "ignorePantry": "false", "ingredients": request.args['ingridients']}
        response = requests.request(
            "GET", url + find, headers=headers, params=querystring).json()
        return render_template('search_ingredients.html', recipes=response, user=current_user)
    else:
        # Random recipes
        querystring = {"number": "5"}
        response = requests.request(
            "GET", url + randomFind, headers=headers, params=querystring).json()
        # print(response)
        return render_template('search_ingredients.html', recipes=response['recipes'], user=current_user)


@views.route('/recipe')
@login_required
def get_recipe():
    recipe_id = request.args['id']
    recipe_info_endpoint = "recipes/{0}/information".format(recipe_id)
    ingedientsWidget = "recipes/{0}/ingredientWidget".format(recipe_id)
    equipmentWidget = "recipes/{0}/equipmentWidget".format(recipe_id)

    recipe_info = requests.request(
        "GET", url + recipe_info_endpoint, headers=headers).json()

    querystring = {"defaultCss": "true", "showBacklink": "false"}

    recipe_info['inregdientsWidget'] = requests.request(
        "GET", url + ingedientsWidget, headers=headers, params=querystring).text
    recipe_info['equipmentWidget'] = requests.request(
        "GET", url + equipmentWidget, headers=headers, params=querystring).text

    return render_template('recipe2.html', recipe=recipe_info, user=current_user)


@views.route('/get-nutrients')
@login_required
def get_nutrients():
    title = request.args['nutrients']
    params = {'title': title}

    if not title:
        flash('Search cannot be empty.', category='error')
    else:
        response = requests.request(
            "GET", url + getNutrients, headers=headers, params=params).json()
        # print(response)
        return render_template("nutritional_info.html", nutrition=response, title=title, user=current_user)
