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
def getPersonInfo(personId):
    conn = sqlite3.connect('test.db')
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    cursor.execute('select * from person where id=?' , (personId,))
    value = cursor.fetchone()

    cursor.execute('select seat_x , seat_z , seat_back_degree , '
                   'mirror_left_x_degree , mirror_left_y_degree , '
                   'mirror_right_x_degree , mirror_right_y_degree from person_seat_setting where person_id=?', (personId,))
    value2 = cursor.fetchone()

    cursor.execute('select headlight_degree from person_light_setting where person_id=?', (personId,))
    value3 = cursor.fetchone()

    # cursor.execute('select switch as air_condition_switch ,mode as air_condition_mode,temp ,air_speed'
    #                'in_out_cycle , clean_mode , air_outlet_position   from person_air_condition_setting where person_id=?', (personId,))
    # value4 = cursor.fetchone()
    #
    # cursor.execute('select switch as navigator_switch , mode as navigator_mode from person_navigator_setting where person_id=?', (personId,))
    # value5 = cursor.fetchone()

    # 关闭Cursor:
    cursor.close()
    # 关闭Connection:
    conn.close()

    # return merge(value5,merge(value4,merge(value3,merge(value, value2))))
    return merge(value3,merge(value, value2))

def updatePersonInfo(personId,name,mobile_phone,seatX,seatZ,seatBackDegree,mirrorLeftXDegree,mirrorLeftYDegree,mirrorRightXDegree,mirrorRightYDegree,headlightDegree):
    conn = sqlite3.connect('test.db')
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    cursor.execute('UPDATE person set name=? , mobile_phone=? where id=?', (name,mobile_phone,personId))

    cursor.execute('UPDATE person_seat_setting set seat_x=? , seat_z=? , seat_back_degree=? , '
                   'mirror_left_x_degree=? , mirror_left_y_degree=? , '
                   'mirror_right_x_degree=? , mirror_right_y_degree=? where person_id=?',
                   (seatX,seatZ,seatBackDegree,mirrorLeftXDegree,mirrorLeftYDegree,mirrorRightXDegree,mirrorRightYDegree,personId))

    cursor.execute('UPDATE person_light_setting SET headlight_degree =?  where person_id=?', (headlightDegree,personId,))

    conn.commit()
    # 关闭Cursor:
    cursor.close()
    # 关闭Connection:
    conn.close()