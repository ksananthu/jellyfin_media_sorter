import os
import time
import shutil
import subprocess
import json
import logging
from imdb import Cinemagoer
import re


## change here

# log_file = (
#     "media_uploader.log"
# )


# # directory lists
# watch_dir_movies = "./upload/movies"
# watch_dir_series = "./upload/series"

# dest = "./dest"


log_file = (
    "/app/log/media_uploader.log"
)


# directory lists
watch_dir_movies = "/app/media/up_movies"
watch_dir_series = "/app/media/up_series"

dest = "/app/media/dst"



# logging setup
logging.basicConfig(
    filename=log_file,
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)



def delete_file(path):
    
    isDir = os.path.isdir(path)
    if isDir == True:
        try:
            shutil.rmtree(path)
            logger.info("Folder %s  is deleted" %path)
        except:
            logger.error("Folder %s  can't be deleted" %path)



def get_details(imdb_link):
    # Create IMDb instance
    ia = Cinemagoer()

    # Extract IMDb ID from the URL
    match = re.search(r"tt\d+", imdb_link)
    if not match:
        logger.error("Invalid IMDb link.")
        return "Invalid IMDb link."

    imdb_id = match.group(0)

    try:
        # Fetch movie/series details
        movie = ia.get_movie(imdb_id[2:])  # Skip 'tt' part
        title = movie.get('title', 'Unknown Title')
        year = movie.get('year', 'Unknown Year')
        logger.info(f"{title} {year} is in databse")
        return title, year
    
    except Exception as e:
        logger.error(f"Error in fetching : {e}")
        return "error"



def movie_mover(source_folder, destination_path, new_name):
    try:
        # Ensure the source folder exists
        if not os.path.exists(source_folder):
            logger.error(f"Source folder '{source_folder}' does not exist.")
            return

        # # Ensure the destination path exists (no need in our case)
        # if not os.path.exists(destination_path):
        #     os.makedirs(destination_path)
        
        

        # Construct the full destination path with the new folder name
        new_folder_path = os.path.join(destination_path, new_name)
        
        
        # check folder with same name already exists in the dst
        if os.path.exists(new_folder_path):
            logger.error(f"{new_name} already exists")
            return

        # Copy the folder to the new destination
        shutil.copytree(source_folder, new_folder_path)
        logger.info(f"Folder copied to '{new_folder_path}'")
        
        # deleting folder
        delete_file(source_folder)
        
    except Exception as e:
        logger.error(f"An error occurred in copying: {e}")




def watcher (directory_path):
    """
    Input  : Directory path
    Output : list with path, cat, url
   
   
    """ 
    watch_output = []

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file == 'start.txt':
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    if len(lines) == 2:
                        cat = lines[0].strip()
                        url = lines[1].strip()
                        json_data = [root, cat, url]
                        
                        if cat in ('ind', 'oth', 'eng'):
                            watch_output.append(json_data)
                            
    logger.info(f"Found : {watch_output}")
    return watch_output




def movie_sorter():
    
    """
    Place files inside the folder.
    each video file should have a name like SxxExx
    start.txt also placed in same directory
    
    start.txt
        - cat [eg: ind, eng, oth]
        - imdb url
    
    """
    
    movies_list = watcher(watch_dir_movies)
    
    for movie in movies_list:
        movie_src_path = movie[0]
        movie_cat = movie[1]
        movie_url = movie[2]
        
        mtitle, myear = get_details(movie_url)
        movie_dst_path = f"{dest}/{movie_cat}_movies"
        
        folder_name = f"{mtitle} ({myear})"
        
        movie_mover(movie_src_path, movie_dst_path, folder_name)
        

def series_sorter():
    """
    Place files inside the folder.
    each video file should have a name like SxxExx
    start.txt also placed in same directory.
    
    start.txt
        - cat [eg: ind, eng, oth]
        - imdb url
    
    """
    
    series_list = watcher(watch_dir_series)
    
    for series in series_list:
        series_src_path = series[0]
        series_cat = series[1]
        series_url = series[2]
        
        
        stitle, syear = get_details(series_url)
        folder_name = f"{stitle} ({syear})"
        
        series_dst_path = f"{dest}/{series_cat}_series/{folder_name}"

        if not os.path.exists(series_dst_path):
            os.makedirs(series_dst_path)
            logger.info(f"Folder created : {series_dst_path}")
        
        files = os.listdir(series_src_path)
        
        for file in files:
            full_file_path = os.path.join(series_src_path, file)
            
            if file == 'start.txt':
                
                # copying files to new dest 
                
                start_info_path = os.path.join(series_dst_path, file)
                if not os.path.exists(start_info_path):
                    shutil.copy(full_file_path, series_dst_path)
                    logger.info(f"File copied  : {file} -- Dest : {series_dst_path}")
            
            # every file other than start.txt
            else:
                # Regular expression to match "SxxExx" in filenames
                pattern = re.compile(r"S(\d{2})E\d{2}", re.IGNORECASE)
                
                # Search for the "SxxExx" pattern in the filename
                match = pattern.search(file)
                
                if match:
                    # Extract season number
                    season_number = match.group(1)
                    season_folder_name = f"Season {season_number}"
                    
                    season_folder_path = os.path.join(series_dst_path, season_folder_name)
                    
                    # create season folder if not exists
                    if not os.path.exists(season_folder_path):
                        os.makedirs(season_folder_path)
                        logger.info(f"Directory created : {season_folder_path}")
                    
                    dest_file_path_full = os.path.join(season_folder_path, file)
                    # copying files to new dest 
                    if not os.path.exists(dest_file_path_full):
                        shutil.copy(full_file_path, dest_file_path_full)
                        logger.info(f"file copied : {file} -- Dest : {dest_file_path_full}")
            
        # deleting uploaded folder
        delete_file(series_src_path)
        
        




if __name__ == "__main__":
    while True:
        movie_sorter()
        series_sorter()
        
        logger.info("---------- Sleeping for 1 min -----------")
        time.sleep(60)
    