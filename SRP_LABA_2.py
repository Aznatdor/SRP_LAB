import pandas as pd
import json
import numpy as np
import urllib3
from matplotlib import pyplot as plt
from datetime import datetime
from spyre import server
urllib3.disable_warnings()


def load_data_VHI(region_ID):  # downloads 'Area-Avegaed' and 'Percentage-Of-Area' data
    id_correction = [22, 24, 23, 25, 3, 4, 8, 19, 20, 21, 9, 26, 10, 11, 12, 13, 14, 15, 16, 27, 17, 18, 6, 1, 2, 7, 5]
    path = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={region_ID}&year1=1981&year2=2022&type=Mean"
    http = urllib3.PoolManager(cert_reqs = 'CERT_NONE')
    req = http.request("GET", path, preload_content=False)
    region_ID = id_correction[region_ID - 1]
    date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    filepath_VHI = f'vhi_id={region_ID}_{date}.csv'  # 'Area-Avegaed' data filepath
    out = open(filepath_VHI, 'wb')
    out.write(req.read())
    out.close()
    path = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={region_ID}&year1=1981&year2=2022&type=VHI_Parea"
    req = http.request("GET", path, preload_content=False)
    filepath_VHI_area = f'vhi_area_id={region_ID}_{date}.csv'
    out = open(filepath_VHI_area, 'wb')
    out.write(req.read())
    out.close()
    return filepath_VHI, filepath_VHI_area


def VHI_dataframe(filepath, *, only_VHI=False):
    df = pd.read_csv(filepath, index_col=False, header=1)  # 'Area-Avegaed' dataframe
    df.rename(columns={' SMN': 'SMN', ' VHI<br>': 'VHI'}, inplace=True)  # hardcode
    if only_VHI:  # if we interested only in VHI data with dates, of course
        return df.iloc[:, [0, 1, 6]]
    return df


def VHI_area_dataframe(filepath, *, all=False):
    name = ['year', 'week', '[0 5)', '[5 10)', '[10 15)', '[15 20)', '[20 25)', '[25 30)', '[30 35)', '[35 40)',
            '[40 45)', '[45 50)', '[50 55)', '[55 60)', '[60 65)', '[65 70)', '[70 75)', '[75 80)', '[80 85)',
            '[85 90)', '[90 95)', '[95, 100)', '[>=100]']
    df = pd.read_csv(filepath, index_col=False, on_bad_lines='skip', header=2, names=name)
    df.iloc[0, 0] = '1982'
    if not all:
        df = df.iloc[:, :9]  # 'Percentage-Of-Area' dataframe (for droughts)
    return df


class Data(server.App):
    title = 'NOAA visualization'

    inputs = [{'type': 'dropdown',
               'label': "NOAA data dropdown",
               'options': [{'label': 'VCI', 'value': 'VCI'},
                           {'label': 'TCI', 'value': 'TCI'},
                           {'label': 'VHI', 'value': "VHI"}
                           ],
               'key': 'ticker',
               },
              {
                'type': 'dropdown',
                'label': 'Area or Data',
                'options': [{'label': 'Area', 'value': 1},
                            {'label': 'Data', 'value': 0}],
                'key': 'type'
              },
              {'type': 'dropdown',
               'label': 'Choose region',
               'options': [{'label': 'Вінницька', 'value': 1},
                           {'label': 'Волинська', 'value': 2},
                           {'label': 'Дніпропетровська', 'value': 3},
                           {'label': 'Донецька', 'value': 4},
                           {'label': 'Житомирська', 'value': 5},
                           {'label': 'Закарпатська', 'value': 6},
                           {'label': 'Запорізька', 'value': 7},
                           {'label': 'Івано-Франківська', 'value': 8},
                           {'label': 'Київська', 'value': 9},
                           {'label': 'Кіровоградська', 'value': 10},
                           {'label': 'Луганська', 'value': 11},
                           {'label': 'Львівська', 'value': 12},
                           {'label': 'Миколаївська', 'value': 13},
                           {'label': 'Одеська', 'value': 14},
                           {'label': 'Полтавська', 'value': 15},
                           {'label': 'Рівенська', 'value': 16},
                           {'label': 'Сумська', 'value': 17},
                           {'label': 'Тернопільська', 'value': 18},
                           {'label': 'Харківська', 'value': 19},
                           {'label': 'Херсонська', 'value': 20},
                           {'label': 'Хмельницька', 'value': 21},
                           {'label': 'Черкаська', 'value': 22},
                           {'label': 'Чернівецька', 'value': 23},
                           {'label': 'Чернігівська', 'value': 24},
                           {'label': 'Республіка Крим', 'value': 25},
                           ],
               'key': 'region',
               },
              {'type': 'text',
               'label': 'Select weeks range',
               'key': 'range'
               },
              {'type': 'dropdown',
               'label': 'Select VHI range (for plot)',
               'options': [{'label': '[0 5)', 'value': '[0 5)'},
                           {'label': '[5 10)', 'value': '[5 10)'},
                           {'label': '[10 15)', 'value': '[10 15)'},
                           {'label': '[15 20)', 'value': '[15 20)'},
                           {'label': '[20 25)', 'value': '[20 25)'},
                           {'label': '[25 30)', 'value': '[25 30)'},
                           {'label': '[30 35)', 'value': '[30 35)'},
                           {'label': '[35 40)', 'value': '[35 40)'},
                           {'label': '[40 45)', 'value': '[40 45)'},
                           {'label': '[45 50)', 'value': '[45 50)'},
                           {'label': '[50 55)', 'value': '[50 55)'},
                           {'label': '[55 60)', 'value': '[55 60)'},
                           {'label': '[60 65)', 'value': '[60 65)'},
                           {'label': '[65 70)', 'value': '[65 70)'},
                           {'label': '[70 75)', 'value': '[70 75)'},
                           {'label': '[75 80)', 'value': '[75 80)'},
                           {'label': '[80 85)', 'value': '[80 85)'},
                           {'label': '[85 90)', 'value': '[85 90)'},
                           {'label': '[90 95)', 'value': '[90 95)'},
                           {'label': '[95 100)', 'value': '[95 100)'},
                           {'label': '[>=100]', 'value': '[>=100]'}],
               'key': 'VHI_range'
               }
              ]

    tabs = ['Data', 'Plot']

    controls = [{
        'type': 'button',
        'id': 'update_data',
        'label': "Show"
    }]

    outputs = [{
        'type': 'table',
        'id': 'table',
        'control_id': 'update_data',
        'tab': 'Data'
    },
        {
            'type': 'plot',
            'id': 'plot',
            'control_id': 'update_data',
            'tab': 'Plot'
        }
    ]

    def getData(self, params):
        ticker, num, range, type = params['ticker'], int(params['region']), params['range'], int(params['type'])
        r_from, r_to = map(int, range.split('-'))
        if type == 0:
            df = VHI_dataframe(load_data_VHI(num)[type])
            df = df[['year', 'week', ticker]]
        if type == 1:
            df = VHI_area_dataframe(load_data_VHI(num)[type], all=True)
        df.iloc[0, 0] = '1982'
        return df[(df['week'] >= r_from) & (df['week'] <= r_to)]

    def getPlot(self, params):
        ticker, type, VHI_range = params['ticker'], int(params['type']), params['VHI_range']
        df = self.getData(params)
        if type == 0:
            plt = df.plot(x='year', y=ticker)
        if type == 1:
            plt = df.plot(x='year', y=VHI_range)
        return plt.get_figure()

app = Data()
app.launch(port=1111)