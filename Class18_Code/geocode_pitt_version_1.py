import pandas as pd
import numpy as np
import logging
from geopy.geocoders import Nominatim


def is_same_add(add1, add2):
    if add1.find("#") > 1:
        add1 = add1[:add1.find("#")].rstrip()
    if add2.find("#") > 1:
        add2 = add2[:add2.find("#")].rstrip()
    if add1 == add2:
        return True
    else:
        return False


logging.basicConfig(filename="pitt_log.txt", filemode="w")
active_voters = pd.read_csv("pitt_active_voter_99800.csv")
latlon = np.zeros(shape=(len(active_voters), 2), dtype=np.float64)

for i in active_voters.index:
    if i < 99800:
        continue
    # use different provider
    geolocator = Nominatim(user_agent="Class_17")

    res_add = active_voters["res_street_address"].iloc[i]
    city = active_voters["res_city_desc"].iloc[i]
    state = active_voters["state_cd"].iloc[i]

    # if the address is empty 
    if len(res_add) * len(city) * len(state) == 0:
        logging.warning("record %6d, broken address. %s, %s, %s" % (i, res_add, city, state))
        latlon[i, 0] = -9999
        latlon[i, 1] = -9999
    else:
        # one address may have multiple voters,
        # for duplicated address, copy previous lat, lon
        if i > 0 and is_same_add(active_voters["res_street_address"].iloc[i],
                                 active_voters["res_street_address"].iloc[i - 1]):
            print("%s is the same as the previous address" % res_add)
            latlon[i, 0] = active_voters["LAT"].iloc[i - 1]
            latlon[i, 1] = active_voters["LON"].iloc[i - 1]
        else:
            # if the mail address include "#", geoencoder will fail
            # 1120  COWELL FARM RD   #115
            if res_add.find("#") > 1:
                res_add = res_add[:res_add.find("#")].rstrip()

            # 24008 E NC HWY 33 HWY => 24008 NC-33
            if " NC HWY" in res_add:
                add_list = res_add.split(" ")
                res_add = add_list[0] + " " + "NC-" + add_list[4]

            # 26011 E US HWY 264 HWY => 26011 US-264
            if " US HWY" in res_add:
                add_list = res_add.split(" ")
                res_add = add_list[0] + " " + "US-" + add_list[4]

            # 1631  BELVOIR HWY HWY => 1631  BELVOIR HWY 
            if "HWY HWY" in res_add:
                res_add.replace("HWY HWY", "HWY")

            address = "%s, %s, %s" % (res_add, city, state)
            try:
                location = geolocator.geocode(address)
                if location is None:
                    # city could be incorrect, try `main_address, zip_code`
                    mail_zipcode = active_voters["mail_zipcode"].iloc[i]
                    address = "%s, %s, %d" % (res_add, state, mail_zipcode)
                    try:
                        location2 = geolocator.geocode(address)
                        if location2 is None:
                            logging.warning("record %6d, failed to geocode the address: %s" % (i, address))
                            latlon[i, 0] = -9999
                            latlon[i, 1] = -9999
                        else:
                            latlon[i, 0] = location2.latitude
                            latlon[i, 1] = location2.longitude
                    except:
                        print("%06d, exception, %s" % (i, address))
                        latlon[i, 0] = -9999
                        latlon[i, 1] = -9999
                        logging.warning("%06d, exception, %s" % (i, address))
                else:
                    latlon[i, 0] = location.latitude
                    latlon[i, 1] = location.longitude
                print("%06d lat=%12.6f lon=%12.6f, %s" % (i, latlon[i, 0], latlon[i, 1], address))
            except:
                print("%06d, exception, %s" % (i, address))
                latlon[i, 0] = -9999
                latlon[i, 1] = -9999
                logging.warning("%06d, exception, %s" % (i, address))

    active_voters.loc[i, "LAT"] = latlon[i, 0]
    active_voters.loc[i, "LON"] = latlon[i, 1]
    active_voters.loc[i, "Geocode_Flag"] = True
    if i % 100 == 0:
        active_voters.to_csv("pitt_active_voter_%05d.csv" % i)

active_voters.to_csv("pitt_active_voter_final.csv")
