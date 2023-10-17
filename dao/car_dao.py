import sqlite3
def dict_factory(cursor,row):
    d={}
    for idx,col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def merge(dict1, dict2):
    if dict1 is None and dict2 is None:
        return None
    if dict1 is None:
        return dict2
    if dict2 is None:
        return dict1
    res = {**dict1, **dict2}
    return res
def getCarInfoByPersonId(personId):
    conn = sqlite3.connect('test.db')
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    cursor.execute('select * from person_car_mapping where driving_flag = true and person_id=?' , (personId,))
    value = cursor.fetchone()

    # 关闭Cursor:
    cursor.close()
    # 关闭Connection:
    conn.close()

    return getCarInfoByCarId(value["car_id"])

def getCarInfoByCarId(carId):
    conn = sqlite3.connect('test.db')
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    cursor.execute('select * from car_info where car_id=?' , (carId,))
    value = cursor.fetchone()

    cursor.execute('select left_seat_x , left_seat_z ,right_seat_x , right_seat_z , left_seat_back_degree , right_seat_back_degree ,'
                   'mirror_left_x_degree , mirror_left_y_degree , mirror_right_x_degree , mirror_right_y_degree ,'
                   'left_seat_heating_switch , left_seat_heating_on_time ,'
                   'right_seat_heating_switch , right_seat_heating_on_time from car_seats_info where car_id=?', (carId,))
    value2 = cursor.fetchone()

    cursor.execute('select headlights_switch ,headlights_degree , fog_light_switch from car_lights_info where car_id=?', (carId,))
    value3 = cursor.fetchone()

    cursor.execute('select switch as air_condition_switch ,mode as air_condition_mode,temp ,air_speed,'
                   'in_out_cycle , clean_mode , air_outlet_position from car_air_condition_info where car_id=?', (carId,))
    value4 = cursor.fetchone()

    cursor.execute('select switch as navigator_switch , mode as navigator_mode from car_navigator_info where car_id=?', (carId,))
    value5 = cursor.fetchone()

    # 关闭Cursor:
    cursor.close()
    # 关闭Connection:
    conn.close()

    return merge(value5,merge(value4,merge(value3,merge(value, value2))))

def updateCarInfo(carId,runningMode,leftSeatX,leftSeatZ,leftSeatBackDegree,mirrorLeftXDegree,
                             mirrorLeftYDegree,mirrorRightXDegree,mirrorRightYDegree,
                             leftSeatHeatingSwitch,headlightsSwitch ,headlightsDegree , fogLightSwitch,
switch ,mode ,temp ,airSpeed,inOutCycle , cleanMode , airOutletPosition,navigatorSwitch,navigatorMode
                  ):
    conn = sqlite3.connect('test.db')
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    cursor.execute('update car_info set running_mode=? where car_id=?', (runningMode,carId,))

    cursor.execute(
        'update car_seats_info set left_seat_x=? , left_seat_z =? , left_seat_back_degree=?  ,'
        'mirror_left_x_degree=? , mirror_left_y_degree=? , mirror_right_x_degree=? , mirror_right_y_degree=? ,'
        'left_seat_heating_switch=?  '
        '  where car_id=?', (leftSeatX,leftSeatZ,leftSeatBackDegree,mirrorLeftXDegree,
                             mirrorLeftYDegree,mirrorRightXDegree,mirrorRightYDegree,
                             leftSeatHeatingSwitch,carId,))

    if leftSeatHeatingSwitch == 1:
        cursor.execute(
            "update car_seats_info set left_seat_heating_on_time=strftime('%s','now') where car_id=? "
            , (carId,))

    cursor.execute('update car_lights_info set headlights_switch=? ,headlights_degree=? , fog_light_switch=?  where car_id=?',
                   (headlightsSwitch ,headlightsDegree , fogLightSwitch,carId,))

    cursor.execute('update car_air_condition_info set switch=? ,mode=? ,temp=? ,air_speed=?,'
                   'in_out_cycle=? , clean_mode=? , air_outlet_position =? where car_id=?',
                   (switch ,mode ,temp ,airSpeed,inOutCycle , cleanMode , airOutletPosition,carId,))

    cursor.execute('update car_navigator_info SET switch =? , mode =?  where car_id=?',
                   (navigatorSwitch,navigatorMode,carId,))

    conn.commit()
    # 关闭Cursor:
    cursor.close()
    # 关闭Connection:
    conn.close()