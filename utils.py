import requests
import csv
import datetime
import folium
from folium import plugins
import pandas as pd
import matplotlib


def get_update_time_from_web(url):
    rsp_dict = dict(requests.head(url).headers)
    # Fri, 14 Oct 2022 11:10:59 GMT
    return rsp_dict['Last-Modified']


def get_update_time(file_path):
    with open(file_path, mode='r') as f:
        r = f.readlines()
        f.close()
        return r[0]


def write_update_time(file_path, content):
    with open(file_path, mode="r+") as f:
        f.seek(0, 0)
        f.writelines(content + '\n')
        f.close()


def download(file_path, url):
    try:
        print('Data needs download, downloading...')
        url_data = requests.get(url).text.encode()
        with open(file_path, mode="wb") as f:
            f.write(url_data)
            f.close()
    except Exception:
        print('[ERROR] Please check your net connection or access')
        return


def transfer2csv(file_path):
    with open(file_path, mode='r') as f, open("data.csv", 'w', newline='', encoding='utf-8') as csvFile:
        writer = csv.writer(csvFile)
        for line in f.readlines()[9:]:
            csv_row = line.split(',')
            writer.writerow(csv_row)
        csvFile.close()
        f.close()


def get_update_data(df):
    time = datetime.datetime.now()
    time_today = str(int(time.year * 10e3 + time.month * 10e1 + time.day))
    update = df[df['date_update\n'].astype(str).str.contains(r'^' + time_today)]
    return update


def add_site(df):
    def file2site(_df):
        file_name = _df['file'].split('/')[0]
        site_name = str(file_name)
        return site_name

    site = df.apply(file2site, axis=1)
    df.insert(1, 'site', site)
    df.to_csv('data.csv')


def report(update_df):
    update_df.groupby('site', as_index=False)
    update_count = update_df.groupby('site')['site'].count().sort_values(ascending=True)
    print('[   Daily Report   ]')
    if update_df.empty:
        print('No update today.')
    else:
        print(str(len(update_df)) + ' items was updated today.')
        print(str(update_count.shape[0]) + ' sites update their data today.')
    fig_col = update_count.plot(x='site name', y='update number',title = 'Daily Update', figsize=(7, 7), kind='bar')

    fig_col.figure.savefig('col.png')

    # 104°E-125°E，4°N-26°N


def add_title(name, _map):
    title_html = '''
                 <h3 align="center" style="font-size:16px"><b>{}</b></h3>
                 '''.format(name)
    _map.get_root().html.add_child(folium.Element(title_html))


def draw_update(df):
    df = df.dropna()
    _map = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=3,
                      control_scale=True)
    marker_cluster = plugins.MarkerCluster().add_to(_map)

    for name, row in df.iterrows():
        folium.Marker(location=[row["latitude"], row["longitude"]]).add_to(marker_cluster)
    add_title('Daily update from ARGO', _map)
    _map.save('daily_update.html')
    print('Daily update from ARGO is already saved in ' + 'daily_update.html')


def draw_scs(df):
    def file2float(_df):
        _float_name = _df['file'].split('/')[1]
        _float_name = str(_float_name)
        return _float_name

    df = df.dropna()

    df_scs = df[(df['latitude'] >= 4) & (df['latitude'] <= 26) &
                (df['longitude'] <= 125) & (df['longitude'] >= 104)]
    float_name = df_scs.apply(file2float, axis=1)
    df_scs.insert(2, 'float', float_name)
    df_scs = df_scs.drop_duplicates('float', keep='last')

    scs_map = folium.Map(location=[df_scs['latitude'].mean(), df_scs['longitude'].mean()], zoom_start=3,
                         control_scale=True)
    marker_cluster = plugins.MarkerCluster().add_to(scs_map)

    for name, row in df_scs.iterrows():
        folium.Marker(location=[row["latitude"], row["longitude"]]).add_to(marker_cluster)
    add_title('South China Sea Total ARGO Location', scs_map)
    scs_map.save('scs_vis.html')
    print('South China Sea Total ARGO Location is already saved in ' + 'scs_vis.html')
