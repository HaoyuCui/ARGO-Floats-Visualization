import argparse
from os.path import lexists
import pandas as pd
from utils import *


def main():
    parser = argparse.ArgumentParser(description="Demo of argparse")
    parser.add_argument('--url', default='https://data-argo.ifremer.fr/ar_index_global_prof.txt')
    parser.add_argument('--file_path', default='ar_index_global_prof.txt')
    parser.add_argument('--force', default=False)  # force to download
    parser.add_argument('--show_scs', default=True)
    parser.add_argument('--map_path', default='')
    args = parser.parse_args()
    url = args.url
    file_path = args.file_path
    force_download = args.force
    show_scs = args.show_scs
    map_path = args.map_path

    update_time = get_update_time_from_web(url)

    # print(update_time.strip())
    # print(get_update_time(file_path).strip())

    if not lexists(args.file_path) or \
            update_time.strip() != get_update_time(file_path).strip() or force_download:
        download(file_path, url)
        write_update_time(file_path, update_time)
        transfer2csv(file_path)
        df = pd.read_csv('data.csv')
        print('Data is updated.')
        df = pd.read_csv('data.csv')
        add_site(df)
    else:
        print('Data is up to date.')
        df = pd.read_csv('data.csv')

    print('[   ' + str(update_time) + '  ]')

    if not lexists('data.csv'):
        transfer2csv(file_path)

    update_df = get_update_data(df)
    # update_df.to_csv('df_update.csv')

    report(update_df)
    # add_float(df)
    if show_scs:
        draw_scs(df)
    draw_update(update_df)


if __name__ == '__main__':
    main()
