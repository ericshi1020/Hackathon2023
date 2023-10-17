from flask import render_template, Blueprint, request
from dao import user_dao , car_dao
import webbrowser
import matplotlib
from facerecognition_opencv import face_detection
import datetime
import pandas as pd
import time
import csv

matplotlib.use('Agg')

user = Blueprint("user", __name__, template_folder="templates")
webbrowser.get('chrome')


@user.route('/<personId>')
def index(personId):
    # currentPerson = getPersonInfo(personId)
    return render_template("index.html", data=personId)


@user.route('/get_person_info/<personId>', methods=['GET'])
def getPersonInfo(personId):
    currentPerson = user_dao.getPersonInfo(personId)
    return currentPerson

@user.route('/update_person_info', methods=['POST'])
def updatePersonInfo():

    #personId,name,mobile_phone,seatX,seatZ,seatBackDegree,mirrorLeftXDegree,mirrorLeftYDegree,mirrorRightXDegree,mirrorRightYDegree,headlightDegree
    user_dao.updatePersonInfo(request.form.get('personId'),request.form.get('personName'),request.form.get('mobile'),request.form.get('seatX'),request.form.get('seatY'),request.form.get('seatBackDegree'),
                                              request.form.get('mirrorLeftXDegree'),request.form.get('mirrorLeftYDegree'),request.form.get('mirrorRightXDegree'),request.form.get('mirrorRightYDegree'),request.form.get('headlightDegree'))
    return "success"

@user.route('/update_car_info', methods=['POST'])
def updateCarInfo():
    car_dao.updateCarInfo(request.form.get('carId'),request.form.get('runningMode'),
                              request.form.get('carLeftSeatX'),request.form.get('carLeftSeatY'),
                              request.form.get('carLeftSeatBackDegree'),request.form.get('carMirrorLeftXDegree'),
                              request.form.get('carMirrorLeftYDegree'),request.form.get('carMirrorRightXDegree'),
                              request.form.get('carMirrorRightYDegree'),request.form.get('leftSeatHeatingSwitch'),
                              request.form.get('headlightsSwitch'),request.form.get('headlightsDegree'),
                              request.form.get('fogLightSwitch'),request.form.get('airConditionSwitch'),
                              request.form.get('airConditionMode'),request.form.get('airConditionTemp'),
                              request.form.get('airSpeed'),request.form.get('inOutCycle'),
                              request.form.get('cleanMode'),request.form.get('airOutletPosition'),
                              request.form.get('navigatorSwitch'),request.form.get('navigatorMode'))
    return "success"

@user.route('/get_car_info_by_person_id/<personId>', methods=['GET'])
def getCarInfo(personId):
    carInfo = car_dao.getCarInfoByPersonId(personId)
    return carInfo


@user.route('/get_recent_person_id')
def getRecentPersonId():
    currentPersonId = face_detection.getRecent3sUser()
    return str(currentPersonId)

@user.route('/get_person_notify', methods=['POST'])
def getPersonalNotify():

     personId = request.form.get('person_id')
     recommendation = user_dao.getPersonInfo(personId)
     result = []
     carInfo = car_dao.getCarInfoByPersonId(personId)
     timestamp = time.time()

     data = []
     data.append(-1)
     data.append( timestamp)
     data.append(personId)
     data.append(-1)
     data.append(-1)
     data.append(request.form.get('brightness'))
     data.append(request.form.get('weather'))
     data.append(carInfo['navigator_switch'])
     data.append(-1)
     data.append(-1)
     data.append(-1)
     data.append(-1)
     data.append(request.form.get('temperature_inside'))
     data.append(request.form.get('temperature_outside'))
     data.append(request.form.get('air_quality'))
     data.append(carInfo['in_out_cycle'])
     data.append(request.form.get('traffic_condition'))
     data.append(-1)
     data.append(request.form.get('road_id'))
     data.append(carInfo['left_seat_heating_switch'])
     data.append(1)
     data.append(carInfo['headlights_switch'])
     data.append(carInfo['fog_light_switch'])
     data.append(1)
     data.append(1)
     data.append(carInfo['air_condition_switch'])
     data.append(carInfo['air_condition_mode'])
     insertOneRowIntoExcel(data)

      # air_circulation: air quality poor and air circulation is off
     if request.form.get('air_quality') == 1 and carInfo['in_out_cycle'] == 0:
         result.append(1)

     # air_clean: air quality poor and air clean is off
     if request.form.get('air_quality') == 1 and carInfo['clean_mode'] == 0:
         result.append(2)

     # seat heat
     if int(request.form.get('temperature_outside')) <= 18 and carInfo['left_seat_heating_switch'] == 0:
         result.append(3)

     # air_conditioner
     if int(request.form.get('temperature_outside')) <= 18 and carInfo['air_condition_switch'] == 0:
         result.append(4)

     # turn on the light
     if int(request.form.get('brightness')) == 1 and carInfo['headlights_switch'] == 0:
         result.append(5)

     # turn on the fog light
     if int(request.form.get('weather')) == 6 and carInfo['fog_light_switch'] == 0:
         result.append(6)

     if carInfo['left_seat_heating_on_time'] is not None :
         # seat off exceed 20 min - notify
         if carInfo['left_seat_heating_switch'] == 1 and is_seat_heating_overtime(carInfo['left_seat_heating_on_time']):
             result.append(7)


     # traffic
     if request.form.get('traffic_condition') == 2 and carInfo['navigator_switch'] == 0:
         result.append(8)

     # open navigation when work day
     if not is_off_work(timestamp) and is_weekday(timestamp) == 1 and carInfo['navigator_switch'] == 0:
         result.append(9)

     # open navigation when get off work
     if is_off_work(timestamp) and carInfo['navigator_switch'] == 0:
         result.append(10)

     # open detailed navigation
     csv_file = 'data_1.csv'
     if not has_visited_road(csv_file, personId, request.form.get('road_id')) and carInfo['navigator_switch'] == 0 and carInfo['navigator_mode'] == 0:
         result.append(11)

     # open detailed navigation
     # todo: how to define how far
     if not has_visited_road(csv_file, personId, request.form.get('road_id')) and carInfo['navigator_switch'] == 0 and carInfo['navigator_mode'] == 0:
         result.append(12)

     # electric
     # no related date
     # if person_details['weather'] == 6 and person_details['fog_light'] != 0:
     #    result.append[13]

     # adjust the temp
     temp_diff = abs(int(request.form.get('temperature_outside')) - int(request.form.get('temperature_inside')))
     if temp_diff >= 7:
         result.append(14)

     return result

@user.route('/voicedetect')
def voiceDetect():
    return render_template("VoiceDictation/index.html")


@user.route('/generateresult')
def generateresult():
    return render_template("generateVoice.html")

def is_weekday(timestamp):
    date = datetime.fromtimestamp(timestamp / 1000)
    weekday = date.weekday()
    if 0 <= weekday < 5:
        return 1
    else:
        return 0

def has_visited_road(csv_file, person_id, road_id):
    df = pd.read_csv(csv_file)
    visited = df[(df['driver_id'] == person_id) & (df['road_id'] == road_id)]
    if not visited.empty:
        return True
    else:
        return False

def is_seat_heating_overtime(left_seat_heating_on_time):
    current_time = datetime.datetime.now()
    heating_time = datetime.datetime.strptime(left_seat_heating_on_time, "%Y-%m-%d %H:%M:%S")
    time_difference = current_time - heating_time
    # 如果时间差超过20分钟，返回True，否则返回False
    return time_difference.total_seconds() > 1200

def is_off_work(timestamp):
    current_time = datetime.datetime.fromtimestamp(timestamp)
    off_work_time = current_time.replace(hour=17, minute=0, second=0, microsecond=0)
    return current_time >= off_work_time

def insertOneRowIntoExcel(data):
    with open("data_1.csv" ,"a",newline="") as demo1:
        # creating writer object
        csv_writer=csv.writer(demo1)
        # appending data
        csv_writer.writerow(data)