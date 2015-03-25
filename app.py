from flask import Flask, render_template, request, redirect,jsonify, url_for

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Companies, Models, User

from flask.ext.login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
from oauth import OAuthSignIn
from flask.ext.login import login_required


app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
#Facebook and twitter api keys
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '',
        'secret': ''
    },
    'twitter': {
        'id': '',
        'secret': ''
    }
}

lm = LoginManager(app)
lm.login_view = 'index'

engine = create_engine('sqlite:///bikecatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

### rauth, login setup

#load user
@lm.user_loader
def load_user(id):
    return session.query(User).filter_by(id=id).one()

#return main page ( login page )
@app.route('/')
def index():
    return render_template('index.html')

#logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#This route first ensures that the user is not logged in, 
#and then simply obtains the OAuthSignIn subclass
#and invoke its authorize() implementation for facebook/twitter.
@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

#The OAuth provider redirects back to the application 
#after the user authenticates and gives permission to share information
@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = session.query(User).filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        session.add(user)
        session.commit()
    login_user(user, True)
    return redirect(url_for('showCompanies'))
###

#List all companies
@app.route('/companies/')
def showCompanies():
	companies = session.query(Companies).all()
	return render_template('companies.html', companies = companies)
	

#Create a new company
@app.route('/companies/new/', methods=['GET','POST'])
@login_required
def newCompany():
	if request.method == 'POST':
		newcompany = Companies(name = request.form['name'])
		session.add(newcompany)
		session.commit()
		return redirect(url_for('showCompanies'))
	else:
		return render_template('newCompany.html')


#Edit a company
@app.route('/companies/<int:company_id>/edit/', methods = ['GET', 'POST'])
@login_required
def editCompany(company_id):
	company = session.query(Companies).filter_by(id = company_id).one()
	if request.method == 'POST':
		if request.form['name']:
			company.name = request.form['name']
			return redirect(url_for('showCompanies'))
	else:
		return render_template('editCompany.html', company=company)


#Delete a company
@app.route('/companies/<int:company_id>/delete/', methods = ['GET','POST'])
@login_required
def deleteCompany(company_id):
	companyDelete = session.query(Companies).filter_by(id = company_id).one()
	if request.method == 'POST':
		session.delete(companyDelete)
		session.commit()
		return redirect(url_for('showCompanies', company_id = company_id))
	else:
		return render_template('deleteCompany.html',company = companyDelete)


#Show models of a company
@app.route('/companies/<int:company_id>/')
@app.route('/companies/<int:company_id>/item/')
def showModels(company_id):
	companies = session.query(Companies).filter_by(id = company_id).one()
	models = session.query(Models).filter_by(company_id = company_id).all()
	return render_template('models.html', models=models, companies=companies)

#Create a new model
@app.route('/companies/<int:company_id>/menu/new/',methods=['GET','POST'])
@login_required
def newModel(company_id):
	if request.method == 'POST':
		newModel = Models(name = request.form['name'], description = request.form['description'], price = request.form['price'], wheel_size = request.form['wheel_size'], company_id = company_id)
		session.add(newModel)
		session.commit()
		
		return redirect(url_for('showModels', company_id = company_id))
	else:
		return render_template('newModel.html', company_id = company_id)

	return render_template('newModel.html', companies=companies)

#Edit a model
@app.route('/brands/<int:company_id>/menu/<int:model_id>/edit', methods=['GET','POST'])
@login_required
def editModel(company_id, model_id):
	Model = session.query(Models).filter_by(id = model_id).one()
	if request.method == 'POST':
		if request.form['name']:
			Model.name = request.form['name']
		if request.form['description']:
			Model.description = request.form['description']
		if request.form['price']:
			Model.price = request.form['price']
		if request.form['wheel_size']:
			Model.wheel_size = request.form['wheel_size']
		session.add(Model)
		session.commit() 
		return redirect(url_for('showModels', company_id=company_id))
	else:
		
		return render_template('editModel.html', company_id=company_id, model_id=model_id, item=Model)


#Delete a model
@app.route('/companies/<int:company_id>/menu/<int:model_id>/delete', methods = ['GET','POST'])
@login_required
def deleteModel(company_id,model_id):
	ModelDelete = session.query(Models).filter_by(id = model_id).one() 
	if request.method == 'POST':
		session.delete(ModelDelete)
		session.commit()
		return redirect(url_for('showModels', company_id = company_id))
	else:
		return render_template('deleteModel.html', model = ModelDelete, company_id=company_id)

# API return models of a company
@app.route('/companies/<int:company_id>/model/JSON')
def CompanyModelsJSON(company_id):
	companies = session.query(Companies).filter_by(id = company_id).one()
	models = session.query(Models).filter_by(company_id = company_id).all()
	return jsonify(MenuItems=[i.serialize for i in models])

# API return a single model
@app.route('/companies/<int:company_id>/model/<int:model_id>/JSON')
def modelJSON(company_id, model_id):
	model = session.query(Models).filter_by(id = model_id).one()
	return jsonify(model = model.serialize)

# API return company list
@app.route('/companies/JSON')
def companiesJSON():
	companies = session.query(Companies).all()
	return jsonify(companies= [r.serialize for r in companies])


if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
