import pandas as pd
import requests
import os
import time
from pathlib import Path
import argparse


def get_dataframe(xml_file_path):
    """Reads the content of a XML file and returns it as a dataframe
    Parameters:
    ------------
    xml_file_path: str
        path to the XML file to be read
    Returns:
    ------------
    df_subset: DataFrame
        dataframe containing the data from the XML file
    """

    df = pd.read_xml(xml_file_path)

    unique_people = df["Last"].unique()

    #select only a subset where the filing type is "P"
    df_subset = df[df['FilingType'] == 'P']

    #drop columns: Prefix, Suffix
    df_subset = df_subset.drop(columns=['Prefix', 'Suffix', "StateDst"])


    #reset index
    df_subset = df_subset.reset_index(drop=True)

    #convert year column to datetime
    df_subset['Year'] = pd.to_datetime(df_subset['Year'], format='%Y')

    #add a new_column called "corresponding url" that contains the url of the pdf file
    df_subset["corresponding_url"] = df_subset.apply(lambda row: f"https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/{row['Year'].year}/{row['DocID']}.pdf", axis=1)

    return df_subset
    #TODO: maybe only subset for people we want to specify with unique_people


def arg_parser():
    parser = argparse.ArgumentParser(description='Download PDFs from XML file')
    parser.add_argument('--year', type=int, default=2022, help='which year we want to download the pdfs from')
    parser.add_argument('--result_folder', type=str, default='data/processed', help='path to the folder where the pdfs should be saved')
    args = parser.parse_args()
    return args

def download_pdf(folder, year, result_folder, df):
    """Downloads the pdf files from the corresponding url and saves them in a folder
    Parameters:
    ------------
    folder: str
        path to the folder where the pdf files should be saved
    year: str
        year of the pdf files
    result_folder: str
        path to the folder where the pdf files should be saved
    df: DataFrame
        dataframe containing the data from the XML file
    Returns:
    ------------
    None, saves the pdf files in a folder

    """
    
    print(f'Downloading PDFs from {year}...')
    print(f'Number of PDFs to download: {len(df)}')
    for index, row in df.iterrows():
        correspondig_url = row["corresponding_url"]
        name = row["Last"]
        filing_data = row["FilingDate"]
        
        #change the order of the data, first the year then the month then the day
        filing_data = filing_data.split("/")
        filing_data = filing_data[2] + "-" + filing_data[0] + "-" + filing_data[1]

        url = correspondig_url
        response = requests.get(url)

        if response.status_code == 200:
            #create a folder to store the pdf files
            os.makedirs(Path(folder/ result_folder/ year),exist_ok=True)
            #save the pdf files
            with open(Path(folder/ result_folder/ year /f"{name}_{filing_data}.pdf"), 'wb') as file:
                file.write(response.content)
                print(f"file {name}_{filing_data}.pdf saved")


    #exit the conneciton:
        response.close()

if __name__ == '__main__':

    folder = Path(__file__).parent.parent.parent
    args = arg_parser()
    year = str(args.year)
    result_folder = args.result_folder
    raw_folder = folder / 'data/raw'
    xml_file_path = raw_folder /f'{year}FD.xml'


    #path is .../data/raw/2022FD.xml for year 2022
    df = get_dataframe(xml_file_path)

    #download the pdf files and store them in the result folder, default is data/processed
    download_pdf(folder, year, result_folder, df)









