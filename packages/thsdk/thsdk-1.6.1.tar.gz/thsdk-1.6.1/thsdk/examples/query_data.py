from thsdk import THS
import pandas as pd
import time

with THS() as ths:
    response = ths.query_data({
        "id": 201,
        "codelist": "300332,300750",
        "market": "USZA",
        "datatype": "5,10,8,9,55,69,70,25,31,127,7,13,14,19,1771976,3153,3541450,3475914,122,123,124,125,2947,592920,1149395,1378761,134152,2946",
        "service": "zhu",

    })
    print("A股:")
    print(pd.DataFrame(response.get_result()))
    time.sleep(1)

    response = ths.query_data({
        "id": 201,
        "codelist": "TSLA",
        "market": "UNQQ",
        "datatype": "5,10,8,9,55,69,70,25,31,127,7,13,14,19,1771976,3153,3541450,3475914,122,123,124,125,2947,592920,1149395,1378761,134152,2946",
        "service": "fu",

    })
    print("美股:")
    print(pd.DataFrame(response.get_result()))
    time.sleep(1)

    response = ths.query_data({
        "id": 201,
        "codelist": "123162,127070,128069,128030,128095,127043,128022,123046,123057,127030,127072,127037,123092,123025,128141,127040,128015",
        "market": "USZD",
        "datatype": "1322",
        "service": "zhu",

    })
    print("可转债:")
    print(pd.DataFrame(response.get_result()))
    time.sleep(1)

    response = ths.query_data({
        "id": 202,
        "codelist": "885754,885975,885982,885942,881161,885866,885893,885977,885843,881166,885459,885980,885923,885956,885897",
        "market": "URFI",
        "datatype": "199112,68285,592890,1771976",
        "service": "fu",

    })
    print("板块:")
    print(pd.DataFrame(response.get_result()))
    time.sleep(1)

    response = ths.query_data({
        "id": 202,
        "codelist": "123135,123038,123109,128044,127046,128041,123120,128121,127025,128037,123103,123104,127022,127006,127068,128142",
        "market": "USZD",
        "datatype": "199112,264648,55",
        "service": "fu",

    })
    print("可转债:")
    print(pd.DataFrame(response.get_result()))
    time.sleep(1)

    response = ths.query_data({
        "id": 200,
        "codelist": "001238",
        "market": "USZA",
        "datatype": "5,6,10,55,3153,330325,330329,69,61,64",
        "service": "fu",

    })
    print("股票:")
    print(pd.DataFrame(response.get_result()))
    time.sleep(1)

    response = ths.query_data({
        "id": 200,
        "codelist": "600821,600089,600386,601618,600642,601011,601678,603181,600482,600118,600308,600863,600273,600988,601918",
        "market": "USHA",
        "datatype": "6,7,8,9,10,13,223,224,225,226,227,228,229,230",
        "service": "zhu",

    })
    print("资金巨鲸数据:")
    print(pd.DataFrame(response.get_result()))
    time.sleep(1)
