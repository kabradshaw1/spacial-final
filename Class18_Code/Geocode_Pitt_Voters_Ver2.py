import pandas as pd
from pathlib import Path
from geopy import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from multiprocessing import Process
import shutil


# Step 2: Standardize the street address
# function for standardize street address
def standardize_street_address(address: str):
    # step (1.1) remove sub-unit after #, 1120  COWELL FARM RD   #115
    if "#" in address:
        address = address[:address.find("#")]
    # step (1.2) remove sub-unit after APTS
    elif "APTS" in address:
        address = address[:address.find("APTS")]

    # step (2) replace multi-space with single-space, and remove tailing spaces
    address = " ".join(address.split())

    # step (3)  24008 E NC HWY 33 HWY => 24008  NC-33
    if " HWY HWY" in address:
        address = address.replace(" HWY HWY", " HWY")
    return address


# define a function for writing the output in a separate process
def write_pickle(df: pd.DataFrame, file_name: Path):
    if file_name.exists():
        tmp_path = file_name.parent/"tmp.pickle"
        # make a copy of the current pickle file before overwriting it
        shutil.copy(file_name, tmp_path)
    df.to_pickle(file_name)
    #df.to_csv(file_name)


def main():
    output_folder = Path("../Output")
    pickle_file_path = output_folder / "pitt_voter_geocoding.pickle"

    # For further correcting the stree address
    replace_dict = {
        "HARBOR POINTE LN": "RIVER BLUFF ROAD",
        "OAK TOWNE DR": "OAKTOWNE DR",
        "VOA SITE C RD": "V O A SITE C RD",
        "L T HARDEE RD": "LT HARDEE RD",
        "FOX DEN WAY": "FOX DEN LOOP",
        "FISHPOND RD": "FISH POND RD",
        "COVENGTON WAY": "COVINGTON",
        "OLD FIRE TOWER RD": "OLD FIRETOWER RD",
        "SUNNY SIDE RD": "SUNNYSIDE RD",
        "JOHNSONS MILL DR": "JOHNSON'S MILL DR",
        "HOLLY GLENN DR": "HOLLY GLEN DR",
        "PLANTERS WAY DR": "PLANTERS WAY",
        "DUNHAGAN RD": "DUNHAGEN RD",
        "ANDERSON RD": "ANDERSON DR",
        "BOXELDER WAY": "LAWRENCE STREET",
        "COURT DR": "CT",
        "HWY HWY": "HWY",
        "CHIPAWAY": "CHIPWAY",
        "CHARLIE BRANCH DR": "CHARLIE BRANCH",
        "WINDBROOKE DR": "WINDBROOK DR",
        "BRIDLE CIR": "BRIDLE CT",
        "BROOK HOLLOW": "BROOKHOLLOW",
        "HOLLY GLENN": "HOLLY GLEN",
        "FREELAND LN": "FREELAND AVE",
        "FIRE TOWER": "FIRETOWER",
        "CROSSROADS RD": "CROSSROADS",
        "RIVER HILL": "RIVER HILLS",
        "W NC 33": "NC 33",
        "HARELL": "HARRELL",
        "JC Galloway": "J C Galloway",
        "WINDBROOKE": "WINDBROOK",
        "WILLIAMSBURG DR": "WILLIAMSBURG RD",
        "CHESSWOOD LN": "CHESTWOOD LN",
        "BLACK JACK SIMPSON RD": "BLACKJACK-SIMPSON RD",
        "BLACK JACK GRIMESLAND RD": "BLACKJACK GRIMESLAND RD"
    }

    locator = Nominatim(user_agent="Pitt Case Study")
    geocode = RateLimiter(locator.geocode, min_delay_seconds=1.0)

    # if the pitt_voeter_geocoding.pickle file doesn't exist, then start from scratch
    if pickle_file_path.is_file() is False:
        # Step 1: Preprocess the data, read from the text file and covert it into CSV file, only keep active voters
        data_path = Path("../Pitt")
        txt_file = data_path / "pitt_voter.txt"

        # read the txt file
        df = pd.read_table(txt_file, encoding="ISO-8859-1")

        # subset the data according to active status and verification status
        active_status = df["voter_status_desc"]  # active or not
        verification_status = df["voter_status_reason_desc"]  # verified or not

        # `&` is the logic and operator for Pandas Series
        selection_flags = (active_status == "ACTIVE") & (verification_status == "VERIFIED")
        active_df = df[selection_flags]

        # Step 2: update the "res_street_address" column
        active_df.loc[:, "res_street_address"] = active_df["res_street_address"].apply(standardize_street_address)

        # Step 3: sort the data frame alphabetically according to res_street_address
        active_df = active_df.sort_values("res_street_address")
        # reset index after sorting
        active_df.reset_index(inplace=True)

        csv_file = output_folder / "pitt_active_voter_standardized.csv"
        active_df.to_csv(csv_file)

        # Step 4: Prepare geocoding, create a "LAT" and a "LON" column, and a "GEOCODE" column
        active_df.insert(active_df.shape[1], "LAT", -9999.0)
        active_df.insert(active_df.shape[1], "LON", -9999.0)
        active_df.insert(active_df.shape[1], "GEOCODE", False)

        # Step 5: Geocoding
        for i in active_df.index:
            # if the i-th address is the same as the (i-1)-th address, then we don't need to geocode it
            if i > 0 and active_df.loc[i, "res_street_address"] == active_df.loc[i - 1, "res_street_address"]:
                active_df.loc[i, "LAT"] = active_df.loc[i - 1, "LAT"]
                active_df.loc[i, "LON"] = active_df.loc[i - 1, "LON"]
                active_df.loc[i, "GEOCODE"] = active_df.loc[i - 1, "GEOCODE"]
                continue

            street_address = active_df.loc[i, "res_street_address"]
            zip_code = int(active_df.loc[i, "zip_code"])
            county_name = "Pitt"
            state_name = "NC"
            # We don't use "city" since the "res_city" may not be accurate in the original data

            # Handle special cases of street address
            # (1) ended with "HALL" or "SUITES", reset it to "E 5th St, Greenville, NC 27858"
            if street_address[-4:] == "HALL" or street_address[-6:] == "SUITES":
                street_address = "E 5th St"

            # further correct street address
            for key, value in replace_dict.items():
                bad_add = key
                good_add = value
                if bad_add in street_address:
                    street_address.replace(bad_add, good_add)
                    break

            # geocode query dict
            query = {"street": street_address,
                     "county": county_name,
                     "state": state_name,
                     "postalcode": zip_code}
            location = geocode(query=query)

            # set a flag indicating this row has been geocoded
            active_df.loc[i, "GEOCODE"] = True
            if location is not None:
                active_df.loc[i, "LAT"] = location.latitude
                active_df.loc[i, "LON"] = location.longitude
                print("Index %d, Address %s has been successfully geocoded" %(i, active_df.loc[i, "res_street_address"]))

            # The following line write the pickle file in a serial mode
            # active_df.to_pickle(pickle_file_path)

            # The following two lines write the pickle file in a parallel mode
            io_process = Process(target=write_pickle, args=(active_df, pickle_file_path,))
            io_process.start()

    # if the pickle file already exists, continue geocoding
    else:
        print("Continue geocoding based on the pickle file: %s" % str(pickle_file_path))
        active_df = pd.read_pickle(pickle_file_path)
        #active_df = pd.read_csv(pickle_file_path)
        # Step 5: Geocoding
        for i in active_df.index:
            # skip rows which have been geocoded
            if active_df.loc[i, "GEOCODE"]:
                continue

            # if the i-th address is the same as the (i-1)-th address, then we don't need to geocode it
            if i > 0 and active_df.loc[i, "res_street_address"] == active_df.loc[i - 1, "res_street_address"]:
                active_df.loc[i, "LAT"] = active_df.loc[i - 1, "LAT"]
                active_df.loc[i, "LON"] = active_df.loc[i - 1, "LON"]
                active_df.loc[i, "GEOCODE"] = active_df.loc[i - 1, "GEOCODE"]
                continue

            street_address = active_df.loc[i, "res_street_address"]
            zip_code = int(active_df.loc[i, "zip_code"])
            county_name = "Pitt"
            state_name = "NC"
            # We don't use "city" since the "res_city" may not be accurate in the original data

            # Handle special cases of street address
            # (1) ended with "HALL" or "SUITES", reset it to "E 5th St, Greenville, NC 27858"
            if street_address[-4:] == "HALL" or street_address[-6:] == "SUITES":
                street_address = "E 5th St"
            elif "VINEYARD DR" in street_address:
                street_address = "652, Forlines Road"

            # further correct street address
            for key, value in replace_dict.items():
                bad_add = key
                good_add = value
                if bad_add in street_address:
                    street_address = street_address.replace(bad_add, good_add)
                    break

            # geocode query dict
            query = {"street": street_address,
                     "county": county_name,
                     "state": state_name,
                     "postalcode": zip_code}
            location = geocode(query=query)

            # set a flag indicating this row has been geocoded
            active_df.loc[i, "GEOCODE"] = True
            if location is not None:
                active_df.loc[i, "LAT"] = location.latitude
                active_df.loc[i, "LON"] = location.longitude
                active_df.loc[i, "GEOCODE"] = True
                print("Index %d, Address %s has been successfully geocoded" %(i, active_df.loc[i, "res_street_address"]))

            # The following line write the pickle file in a serial mode
            # active_df.to_pickle(pickle_file_path)

            # The following two lines write the pickle file in a parallel mode
            io_process = Process(target=write_pickle, args=(active_df, pickle_file_path,))
            io_process.start()


if __name__ == "__main__":
    main()
