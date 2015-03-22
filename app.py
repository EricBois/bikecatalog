from flask import Flask, render_template, request, redirect,jsonify, url_for
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Companies, Models



engine = create_engine('sqlite:///bikecatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


#Show all brands
@app.route('/')
@app.route('/companies/')
def showCompanies():
	companies = session.query(Companies).all()
	return render_template('companies.html', companies = companies)
	

#Create a new brands
@app.route('/companies/new/', methods=['GET','POST'])
def newCompany():
	if request.method == 'POST':
		newcompany = Companies(name = request.form['name'])
		session.add(newcompany)
		session.commit()
		return redirect(url_for('showCompanies'))
	else:
		return render_template('newCompany.html')


#Edit a brands
@app.route('/companies/<int:company_id>/edit/', methods = ['GET', 'POST'])
def editCompany(company_id):
	company = session.query(Companies).filter_by(id = company_id).one()
	if request.method == 'POST':
		if request.form['name']:
			company.name = request.form['name']
			return redirect(url_for('showCompanies'))
	else:
		return render_template('editCompany.html', company=company)


#Delete a brands
@app.route('/companies/<int:company_id>/delete/', methods = ['GET','POST'])
def deleteCompany(company_id):
	companyDelete = session.query(Companies).filter_by(id = company_id).one()
	if request.method == 'POST':
		session.delete(companyDelete)
		session.commit()
		return redirect(url_for('showCompanies', company_id = company_id))
	else:
		return render_template('deleteCompany.html',company = companyDelete)


#Show a brands menu
@app.route('/companies/<int:company_id>/')
@app.route('/companies/<int:company_id>/item/')
def showModels(company_id):
	companies = session.query(Companies).filter_by(id = company_id).one()
	models = session.query(Models).filter_by(company_id = company_id).all()
	return render_template('models.html', models=models, companies=companies)

#Create a new menu item
@app.route('/companies/<int:company_id>/menu/new/',methods=['GET','POST'])
def newModel(company_id):
	if request.method == 'POST':
		newModel = Models(name = request.form['name'], description = request.form['description'], price = request.form['price'], wheel_size = request.form['wheel_size'], company_id = company_id)
		session.add(newModel)
		session.commit()
		
		return redirect(url_for('showModels', company_id = company_id))
	else:
		return render_template('newModel.html', company_id = company_id)

	return render_template('newModel.html', companies=companies)

#Edit a menu item
@app.route('/brands/<int:company_id>/menu/<int:model_id>/edit', methods=['GET','POST'])
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


#Delete a menu item
@app.route('/companies/<int:company_id>/menu/<int:model_id>/delete', methods = ['GET','POST'])
def deleteModel(company_id,model_id):
	ModelDelete = session.query(Models).filter_by(id = model_id).one() 
	if request.method == 'POST':
		session.delete(ModelDelete)
		session.commit()
		return redirect(url_for('showModels', company_id = company_id))
	else:
		return render_template('deleteModel.html', model = ModelDelete, company_id=company_id)


@app.route('/companies/<int:company_id>/menu/JSON')
def CompanyModelsJSON(company_id):
	companies = session.query(Companies).filter_by(id = company_id).one()
	models = session.query(Models).filter_by(company_id = company_id).all()
	return jsonify(MenuItems=[i.serialize for i in models])



@app.route('/companies/<int:company_id>/menu/<int:model_id>/JSON')
def modelJSON(company_id, model_id):
	model = session.query(Models).filter_by(id = model_id).one()
	return jsonify(model = model.serialize)

@app.route('/companies/JSON')
def companiesJSON():
	companies = session.query(Companies).all()
	return jsonify(companies= [r.serialize for r in companies])


if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
