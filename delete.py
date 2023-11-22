if __name__ == '__main__':
    __package__ = 'recipeMe'
    
from recipeMe import app, db
from recipeMe.models import User  


with app.app_context():
    user_to_delete = User.query.filter_by(username='davud_kh').first()
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        print("User deleted")
    else:
        print("User not found")

