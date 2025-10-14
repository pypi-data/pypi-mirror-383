from io import UnsupportedOperation

import requests
from pathlib import Path
from typing import Optional


class PlateFrameService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlateFrameService, cls).__new__(cls)
            cls._instance._repository = None
        return cls._instance
    
    def __init__(self):
        if self._repository is None:
            from ..repository.plate_frame_repository import PlateFrameRepository
            self._repository = PlateFrameRepository()

    @property
    def __repository(self):
        return self._repository
    
    def get_plate_frame(self, plate_frame_name: str):
        return self.__repository.get_plate_frame(plate_frame_name)
    
    def get_plate_frames(self):
        return self.__repository.get_plate_frames()

    def get_plate_frames_by_plate(self, plate_name: str):
        return self.__repository.get_plate_frames_by_plate(plate_name) 
    
    def download_fits_plate_frames(self, plate_names: tuple, output_dir: Optional[str] = None):

        if output_dir is None:
            output_dir = './fits_downloads'
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        downloaded_files = []
        
        for plate_name in plate_names:
            try:
                plate_frame = self.__repository.get_plate_frame(plate_name)
                
                if plate_frame.empty:
                    print(f"Warning: Plate frame '{plate_name}' not found in database")
                    continue
                
                # Get the FITS link from the DataFrame
                link_fits = plate_frame.iloc[0]['link_fts']
                
                if not link_fits:
                    print(f"Warning: No FITS link found for plate frame '{plate_name}'")
                    continue
                
                # Download the file
                print(f"Downloading FITS file for '{plate_name}' from {link_fits}")
                response = requests.get(link_fits, stream=True)
                response.raise_for_status()
                
                # Save the file
                file_name = f"{plate_name}.fits"
                file_path = output_path / file_name
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"Successfully downloaded: {file_path}")
                downloaded_files.append(str(file_path))
                
            except Exception as e:
                print(f"Error downloading FITS file for '{plate_name}': {str(e)}")
        
        return downloaded_files

    def download_fits_plate_frames_from_custom_query(self, query: str, output_dir: Optional[str] = None):

        if output_dir is None:
            output_dir = './fits_downloads'

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        downloaded_files = []

        plate_frames = self._repository.get_from_custom_query(query)

        if plate_frames.empty:
            raise UnsupportedOperation(f"Warning: No plate frames found for query '{query}'")

        for index, row in plate_frames.iterrows():
            plate_frame_name = row["name"]
            link_fit = row["link_fts"]
            try:
                # Download the file
                print(f"Downloading FITS file for '{plate_frame_name}' from {link_fit}")
                response = requests.get(link_fit, stream=True)
                response.raise_for_status()

                # Save the file
                file_name = f"{plate_frame_name}.fits"
                file_path = output_path / file_name

                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"Successfully downloaded: {file_path}")
                downloaded_files.append(str(file_path))

            except Exception as e:
                print(f"Error downloading FITS file for '{plate_frame_name}': {str(e)}")

        return downloaded_files