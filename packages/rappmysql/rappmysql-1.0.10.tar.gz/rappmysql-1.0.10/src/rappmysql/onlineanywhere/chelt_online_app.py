from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, send_file, session
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import traceback
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import re
import os
import sys
import csv
from rappmysql.mysqlquerys import connect, mysql_rm
from rappmysql.cheltuieli import chelt_plan
from rappmysql.cheltuieli.chelt_plan import CheltuieliPlanificate
from rappmysql.mruser.myusers import Users
from rappmysql.masina.auto import Masina, AutoApp
from rappmysql.aeroclub.aeroclub import AeroclubSQL

try:
    compName = os.getenv('COMPUTERNAME')
    if compName == 'DESKTOP-5HHINGF':
        ini_file = r"D:\Python\MySQL\users.ini"
        ini_chelt = r"D:\Python\MySQL\cheltuieli.ini"
        ini_masina = r"D:\Python\MySQL\masina.ini"
        ini_aeroclub = r"D:\Python\MySQL\aeroclub.ini"
        report_dir = r"D:\Python\MySQL\onlineanywhere\static"
    else:
        ini_users = r"C:\_Development\Diverse\pypi\cfgm.ini"
        ini_chelt = r"C:\_Development\Diverse\pypi\cfgm.ini"
        ini_masina = r"C:\_Development\Diverse\pypi\cfgm.ini"
        # ini_file = r"C:\_Development\Diverse\pypi\cfgmRN.ini"
        report_dir = r"C:\_Development\Diverse\pypi\radu\masina\src\masina\static"
except:
    ini_users = '/home/radum/mysite/static/wdb.ini'

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = "my super secret"
login_manager = LoginManager()
login_manager.init_app(app)
# ini_file = '/home/radum/mysite/static/wdb.ini'
# ini_masina = '/home/radum/mysite/static/ini_masina.ini'
# ini_chelt = '/home/radum/mysite/static/ini_chelt.ini'
report = '/home/radum/mysite/static/report.csv'

conf = connect.Config(ini_file)


@login_manager.user_loader
def load_user(user_id):
    try:
        try:
            mat = int(user_id)
        except:
            mat = int(re.findall("\[(.+?)\]", user_id)[0])
        matches = ('id', mat)
        users_table = mysql_rm.Table(conf.credentials, 'users')
        name = users_table.returnCellsWhere('username', matches)[0]
        user = Users(name, ini_file)
        return user
    except:
        print(30*'*', str(traceback.format_exc()))


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        return render_template('index.html')
    except:
        myerr = 'definition {}\n{}'.format(sys._getframe().f_code.co_name, str(traceback.format_exc()))
        return render_template('err.html',
                               myerr=myerr)


@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            username = request.form['username']
            user = Users(username, ini_file)
            if user.verify_password(request.form['password']):
                login_user(user)
                return redirect(url_for("index"))
            else:
                return 'NOT LOGED IN'
        else:
            return render_template("login.html")
    except:
        myerr = 'definition {}\n{}'.format(sys._getframe().f_code.co_name, str(traceback.format_exc()))
        return render_template('err.html',
                               myerr=myerr)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    try:
        logout_user()
        return redirect(url_for('index'))
    except:
        myerr = 'definition {}\n{}'.format(sys._getframe().f_code.co_name, str(traceback.format_exc()))
        return render_template('err.html',
                               myerr=myerr)


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        conf = connect.Config(ini_file)
        users_table = mysql_rm.Table(conf.credentials, 'users')
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            cols = ('username', 'email', 'password')
            hash = generate_password_hash(password)
            vals = (username, email, hash)
            users_table.addNewRow(cols, vals)
        return render_template('register.html')
    except:
        myerr = 'definition {}\n{}'.format(sys._getframe().f_code.co_name, str(traceback.format_exc()))
        return render_template('err.html',
                               myerr=myerr)

###cheltuieli###################################################################################
@app.route('/cheltuieli', methods=['GET', 'POST'])
@login_required
def cheltuieli():
    try:
        chelt_app = CheltuieliPlanificate(ini_chelt)
        dataFrom, dataBis = chelt_plan.default_interval()
        conto = 'all'
        if request.method == 'POST':
            month = request.form['month']
            year = int(request.form['year'])
            conto = request.form['conto']
            dataFrom = request.form['dataFrom']
            dataBis = request.form['dataBis']
            if month != 'interval':
                dataFrom, dataBis = chelt_plan.get_monthly_interval(month, year)
            elif month == 'interval' and (dataFrom == '' or dataBis == ''):
                dataFrom, dataBis = chelt_plan.default_interval()
            else:
                try:
                    dataFrom = datetime.strptime(dataFrom, "%Y-%m-%d")
                    dataBis = datetime.strptime(dataBis, "%Y-%m-%d")
                    print(dataFrom.date(), dataBis.date())
                except:
                    return render_template('cheltuieli.html', tot_val_of_expenses_income=str(traceback.format_exc()))
        try:
            if isinstance(dataFrom, datetime):
                chelt_app.prepareTablePlan(conto, dataFrom.date(), dataBis.date(), True)
            elif isinstance(dataFrom, date):
                chelt_app.prepareTablePlan(conto, dataFrom, dataBis, True)
            return render_template('cheltuieli.html',
                                   expenses=chelt_app.expenses,
                                   tot_no_of_monthly_expenses=chelt_app.tot_no_of_monthly_expenses,
                                   tot_val_of_monthly_expenses=chelt_app.tot_val_of_monthly_expenses,
                                   tot_no_of_irregular_expenses=chelt_app.tot_no_of_irregular_expenses,
                                   tot_val_of_irregular_expenses=chelt_app.tot_val_of_irregular_expenses,
                                   tot_no_of_expenses=chelt_app.tot_no_of_expenses,
                                   tot_val_of_expenses=chelt_app.tot_val_of_expenses,
                                   summary_table=[''],
                                   tot_val_of_income='chelt_app.tot_val_of_income()',
                                   dataFrom=dataFrom,
                                   dataBis=dataBis
                                   )
        except:
            print(traceback.format_exc())
            return render_template('err.html', myerr=str(traceback.format_exc()))
    except:
        myerr = 'definition {}\n{}'.format(sys._getframe().f_code.co_name, str(traceback.format_exc()))
        return render_template('err.html',
                               myerr=myerr)


@app.route('/add_cheltuieli', methods=['GET', 'POST'])
@login_required
def add_cheltuieli():
    try:
        chelt_app = CheltuieliPlanificate(ini_chelt)

        if request.method == 'GET':
            return render_template('addchelt.html')
        if request.method == 'POST':
            if "add_one_time_chelt" in request.form:
                name = request.form['name']
                value = request.form['value']
                myconto = request.form['myconto']
                pay_day = request.form['pay_day']
                pay_day = datetime.strptime(pay_day, "%Y-%m-%d")
                chelt_app.add_one_time_transactions(name, value, myconto, pay_day)
                return redirect(url_for('cheltuieli'))

    except:
        myerr = 'definition {}\n{}'.format(sys._getframe().f_code.co_name, str(traceback.format_exc()))
        return render_template('err.html',
                               myerr=myerr)


###masina###################################################################################
@app.route('/masina', methods=['GET', 'POST'])
@login_required
def masina():
    try:
        current_user.init_app('auto', ini_masina)
        #id_all_cars = current_user.auto_app.get_id_all_cars('Hyundai_Ioniq')
        #return str(id_all_cars)
        return render_template('masina.html')
    except:
        myerr = 'definition {}\n{}'.format(sys._getframe().f_code.co_name,
                                                  str(traceback.format_exc()))
        return render_template('err.html', myerr=myerr)


@app.route('/summary/<id_car>/<table_name>', methods=['GET', 'POST'])
@login_required
def car_summary(id_car, table_name):
    try:
        session['id_car'] = id_car
        if request.method == 'GET':
            app_masina = Masina(ini_masina, current_user.id, id_car)
            return render_template('car_summary.html',
                                   table_name=table_name,
                                   tabel_alimentari=app_masina.table_alimentari,
                                   tabel_totals=app_masina.table_totals,
                                   last_records=app_masina.last_records
                                   )
        elif request.method == 'POST':
            if 'export_detail_table_as_sql' in request.form:
                output_sql_file = current_user.export_car_sql(id_car)
                # # return text_to_write
                # pth_to_sql = os.path.join(report_dir, 'aaa.sql')
                # # if os.path.exists(pth_to_sql):
                # #     os.remove(pth_to_sql)
                # # with open(pth_to_sql, 'w') as file:
                # #     for row in text_to_write:
                # #         file.write(row)
                return output_sql_file
            elif 'export_detail_table_with_files' in request.form:
                output_sql_file = current_user.export_car_sql(id_car, export_files=True)
                return output_sql_file

                # app_masina = Masina(conf.credentials, table_name=table_name.lower())
    except:
        myerr = 'definition {}\n{}'.format(sys._getframe().f_code.co_name, str(traceback.format_exc()))
        return render_template('err.html', myerr=myerr)


@app.route('/details/<table_name>', methods=['GET', 'POST'])
def consumption_details(table_name):
    try:
        app_masina = Masina(ini_masina, id_users=current_user.id, id_car=session['id_car'])
        if request.method == 'GET':
            dataFrom, dataBis = app_masina.default_interval
            alim_type = None
            alimentari = app_masina.get_alimentari_for_interval_type(dataFrom, dataBis, alim_type)
            return render_template('car_detailed.html',
                                   table_name=table_name,
                                   id_car=session['id_car'],
                                   userDetails=alimentari,
                                   types_of_costs=app_masina.types_of_costs,
                                   dataFrom=dataFrom.date(),
                                   dataBis=dataBis.date(),
                                   )
        elif request.method == 'POST':
            # if 'export_detail_table_as_csv' in request.form:
            if 'export_detail_table_as_sql' in request.form:
                tables = {'all_cars': 'user_id',
                          table_name: 'id_users'}
                output_sql_file = current_user.export_car_sql(tables)
                # # return text_to_write
                # pth_to_sql = os.path.join(report_dir, 'aaa.sql')
                # # if os.path.exists(pth_to_sql):
                # #     os.remove(pth_to_sql)
                # # with open(pth_to_sql, 'w') as file:
                # #     for row in text_to_write:
                # #         file.write(row)
                return output_sql_file
            elif 'upload_file' in request.form:
                database = mysql_rm.DataBase(ini_masina)
                file = request.files['myfile']
                filename = secure_filename(file.filename)
                fl = os.path.join(report_dir, filename)
                file.save(fl)
                with open(fl) as f:
                    file_content = f.read()
                    print(file_content)
                database.run_sql_file(fl)
                return file_content

                # app_masina = Masina(conf.credentials, table_name=table_name.lower())
            elif "filter" in request.form:
                month = request.form['month']
                year = int(request.form['year'])
                alim_type = request.form['type']
                if alim_type == 'all':
                    alim_type = None
                dataFrom = request.form['dataFrom']
                dataBis = request.form['dataBis']

                if month != 'interval':
                    dataFrom, dataBis = app_masina.get_monthly_interval(month, year)
                elif month == 'interval' and (dataFrom == '' or dataBis == ''):
                    dataFrom, dataBis = app_masina.default_interval
                else:
                    try:
                        dataFrom = datetime.strptime(dataFrom, "%Y-%m-%d")
                        dataBis = datetime.strptime(dataBis, "%Y-%m-%d")
                    except:
                        print(traceback.format_exc())
                alimentari = app_masina.get_alimentari_for_interval_type(dataFrom, dataBis, alim_type)
                return render_template('car_detailed.html',
                                       table_name=table_name,
                                       userDetails=alimentari,
                                       types_of_costs=app_masina.types_of_costs,
                                       dataFrom=dataFrom.date(),
                                       dataBis=dataBis.date(),
                                       )
    except:
        myerr = 'definition {}\n{}'.format(sys._getframe().f_code.co_name, str(traceback.format_exc()))
        return render_template('err.html', myerr=myerr)


@app.route('/upload_file/<table_name>/<row_id>', methods=['GET', 'POST'])
def upload_file_to_row(table_name, row_id):
    # print('Module: {}, Def: {}, Caller: {}'.format(__name__, sys._getframe().f_code.co_name,
    #                                                sys._getframe().f_back.f_code.co_name))
    try:
        id_car = current_user.get_id_all_cars(table_name)
        app_masina = Masina(ini_masina, id_users=current_user.id, id_car=id_car)
        # app_masina = Masina(ini_masina, table_name=table_name.lower())
        file = request.files['myfile']
        filename = secure_filename(file.filename)
        fl = os.path.join(report_dir, filename)
        file.save(fl)
        app_masina.upload_file(fl, row_id)
        return 'done'
    except:
        myerr = 'definition {}\n{}'.format(sys._getframe().f_code.co_name, str(traceback.format_exc()))
        return render_template('err.html', myerr=myerr)


@app.route('/add_masina', methods=['GET', 'POST'])
def add_masina():
    try:
        current_user.init_app('auto', ini_masina)
        print(sys._getframe().f_code.co_name, request.method)
        if request.method == 'POST':
            if 'create_user_car' in request.form:
                brand = request.form['brand']
                model = request.form['model']
                car_type = request.form['car_type']
                current_user.auto_app.add_car(brand, model, car_type)
            elif 'import_car_sql' in request.form:
                file = request.files['myfile']
                filename = secure_filename(file.filename)
                fl = os.path.join(report_dir, filename)
                file.save(fl)
                # with open(fl) as f:
                #     file_content = f.read()
                #     print(file_content)
                current_user.run_sql_query(fl)
                os.remove(fl)
                return redirect(url_for('index'))
            elif 'import_car_with_files' in request.form:
                file = request.files['zip_file']
                filename = secure_filename(file.filename)
                fl = os.path.join(report_dir, filename)
                file.save(fl)
                # with open(fl) as f:
                #     file_content = f.read()
                #     print(file_content)
                current_user.import_car_with_files(fl, import_files=True)
                os.remove(fl)
                return redirect(url_for('index'))
            elif 'import_car_without_files' in request.form:
                file = request.files['zip_file']
                filename = secure_filename(file.filename)
                fl = os.path.join(report_dir, filename)
                file.save(fl)
                # with open(fl) as f:
                #     file_content = f.read()
                #     print(file_content)
                current_user.import_car_with_files(fl)
                os.remove(fl)
                return redirect(url_for('index'))
            return redirect(url_for('index'))
        return render_template('addcar.html')
    except:
        myerr = 'a_{}_a definition {}\n{}'.format(current_user.id, sys._getframe().f_code.co_name,
                                                  str(traceback.format_exc()))
        return render_template('err.html',
                               myerr=myerr)


@app.route('/addalim/<table_name>', methods=['GET', 'POST'])
def addalim(table_name):
    try:
        current_user.init_app('auto', ini_masina)
        id_car = session['id_car']
        app_masina = Masina(ini_masina, id_users=current_user.id, id_car=id_car)
        if request.method == 'GET':
            return render_template('addalim.html',
                                   table_name=table_name,
                                   types_of_costs=app_masina.types_of_costs)
        if request.method == 'POST':
            if "add_alim" in request.form:
                date = request.form['data']
                alim_type = request.form['type']
                eprov = request.form['eprov']
                brutto = request.form['brutto']
                amount = request.form['amount']
                km = request.form['km']
                # ppu = round(float(brutto)/float(amount), 3)
                # columns = ['data', 'type', 'eProvider', 'brutto', 'amount', 'ppu', 'km']
                # values = [date, alim_type, eprov, brutto, amount, ppu, km]

                # app_masina.insert_new_alim(columns, values)
                id_car = current_user.auto_app.get_id_all_cars(table_name)
                app_masina.insert_new_alim(current_id_users=current_user.id, id_all_cars=id_car, data=date,
                                           alim_type=alim_type, brutto=brutto, amount=amount, refuel=None, other=None,
                                           recharges=None, km=km, comment=None, file=None, provider=eprov)
                return redirect(url_for('car_summary', id_car=id_car, table_name=table_name))
    except:
        myerr = 'a_{}_a definition {}\n{}'.format(current_user.id, sys._getframe().f_code.co_name,
                                                  str(traceback.format_exc()))
        return render_template('err.html',
                               myerr=myerr)


@app.route('/deleterow/<table_name>/<index>', methods=['GET', 'POST'])
def deleterow(table_name, index):
    try:
        # print(sys._getframe().f_code.co_name, request.method)
        # return index
        id_car = current_user.get_id_all_cars(table_name)
        app_masina = Masina(ini_masina, id_users=current_user.id, id_car=id_car)
        app_masina.delete_row(index)
        return redirect(url_for('consumption_details', table_name=table_name))
    except:
        myerr = 'a_{}_a definition {}\n{}'.format(current_user.id, sys._getframe().f_code.co_name,
                                                  str(traceback.format_exc()))
        return render_template('err.html',
                               myerr=myerr)


@app.route('/delete_masina/<id_car>/<table_name>', methods=['GET', 'POST'])
def delete_masina(id_car, table_name):
    try:
        current_user.init_app('auto', ini_masina)
        current_user.auto_app.delete_auto(table_name)
        return redirect(url_for('index'))
    except:
        myerr = 'a_{}_a definition {}\n{}'.format(current_user.id, sys._getframe().f_code.co_name,
                                                  str(traceback.format_exc()))
        return render_template('err.html',
                               myerr=myerr)


########################################################################
@app.route('/aeroclub', methods=['GET', 'POST'])
def aeroclub():
    try:
        app_aeroclub = AeroclubSQL(ini_aeroclub)
        print('app_masina.total_unpaid_flights', app_aeroclub.total_unpaid_flights)
        if request.method == 'POST':
            return redirect(url_for('index'))
        return render_template('aeroclub.html',
                               total_unpaid_flights=app_aeroclub.total_unpaid_flights,
                               flight_time_this_year=app_aeroclub.flight_time_this_year,
                               total_flight_time=app_aeroclub.total_flight_time
                               )
    except:
        myerr = 'a_{}_a definition {}\n{}'.format(current_user.id, sys._getframe().f_code.co_name,
                                                  str(traceback.format_exc()))
        return render_template('err.html',
                               myerr=myerr)


if __name__ == "__main__":
    app.run(debug=True)
