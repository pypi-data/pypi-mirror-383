"""
Inofficial wrapper for the API of the www.netztransparenz.de platform.

To access the API it is required to set up a free account and client in the
Netztransparenz extranet. (see: https://www.netztransparenz.de/en/Web-API)
"""

import requests
import logging
import datetime as dt
import io

import pandas as pd

log = logging.getLogger("NetztransparenzClient")
_api_date_format = "%Y-%m-%dT%H:%M:%S"
_csv_date_format = "%Y-%m-%d %H:%M %Z"
_csv_date_format_no_zone = "%Y-%m-%d %H:%M"
_ACCESS_TOKEN_URL = "https://identity.netztransparenz.de/users/connect/token"
_API_BASE_URL = "https://ds.netztransparenz.de/api/v1"

class NetztransparenzClient:

    def __init__(self, client_id, client_pass):

        response = requests.post(_ACCESS_TOKEN_URL,
                    data = {
                            'grant_type': 'client_credentials',
                            'client_id': client_id,
                            'client_secret': client_pass
            })

        if response.ok:
            self.token = response.json()['access_token']
        else:
            message = f'Error retrieving token\n{response.status_code}:{response.reason}'
            log.error(message)
            raise Exception(f"Login failed. {message}")

    def check_health(self):
        """
        Return the text response of the API health endpoint.
        Any Response but "OK" indicates a problem.
        """

        url = f"{_API_BASE_URL}/health"
        response = requests.get(url, headers = {'Authorization': 'Bearer {}'.format(self.token)})
        return response.text

    def _basic_read_nt(self, resource_url, earliest_data, dt_begin: dt.datetime | None = None, dt_end: dt.datetime | None = None, 
        transform_dates=False):
        """
        Internal method to read data in one of the common formats of th nt portal.
        Target format is: Dates separated in "Datum", "von", "Zeitzone von", "bis", "Zeitzone bis".
        Return a pandas Dataframe with data of the endpoint specified with resource_url.
        If either dt_begin or dt_end is None, all available data will be queried.

            resource_url -- url of the endpoint without the base url and without leading or trailing "/"
            earliest_data -- first datapoint in the source collection
            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        url = f"{_API_BASE_URL}/{resource_url}"
        if((dt_begin != None) and (dt_end != None)):
            start_of_data = dt_begin.strftime(_api_date_format)
            start_of_data = start_of_data if start_of_data > earliest_data else earliest_data
            end_of_data = dt_end.strftime(_api_date_format)
            url = f"{_API_BASE_URL}/{resource_url}/{start_of_data}/{end_of_data}"

        response = requests.get(url, headers = {'Authorization': 'Bearer {}'.format(self.token)})
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text),
            sep=";",
            header=0,
            decimal=",",
            thousands=".",
            na_values=["N.A."]
            )

        if(transform_dates):    
            df["von"] = pd.to_datetime(df["Datum"] + " " + df["von"] + " " + df["Zeitzone von"], format=_csv_date_format, utc=True)
            df["bis"] = pd.to_datetime(df["Datum"] + " " + df["bis"] + " " + df["Zeitzone bis"], format=_csv_date_format, utc=True)
            #The end of timeframes may be 00:00 of the next day witch is not correctly represented in timestamps
            df["bis"] = df["bis"].where(df["bis"].dt.time != dt.time(0,0), df["bis"] + dt.timedelta(days=1))
            df = df.drop(["Datum", "Zeitzone von", "Zeitzone bis"], axis=1).set_index("von")
        
        return df
    
    def _basic_read_nrvsaldo(self, resource_url, earliest_data, dt_begin: dt.datetime | None = None, dt_end: dt.datetime | None = None, transform_dates=False):
        """
        Internal method to read data in the format of most /nrvsaldo dataseries.
        Target format is: Dates separated in "datum", "von", "bis", "zeitzone".
        Return a pandas Dataframe with data of the endpoint specified with resource_url.
        If either dt_begin or dt_end is None, all available data will be queried.

            resource_url -- url of the endpoint without the base url and without leading or trailing "/"
            earliest_data -- first datapoint in the source collection
            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        url = f"{_API_BASE_URL}/{resource_url}"
        if((dt_begin != None) and (dt_end != None)):
            start_of_data = dt_begin.strftime(_api_date_format)
            start_of_data = start_of_data if start_of_data > earliest_data else earliest_data
            end_of_data = dt_end.strftime(_api_date_format)
            url = f"{_API_BASE_URL}/{resource_url}/{start_of_data}/{end_of_data}"

        response = requests.get(url, headers = {'Authorization': 'Bearer {}'.format(self.token)})
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text),
            sep=";",
            header=0,
            decimal=",",
            na_values=["N.A."]
            )
        
        if(transform_dates):
            df["von"] = pd.to_datetime(df["datum"] + " " + df["von"] + " " + df["zeitzone"], format="%d.%m.%Y %H:%M %Z").dt.tz_convert(None)
            df["bis"] = pd.to_datetime(df["datum"] + " " + df["bis"] + " " + df["zeitzone"], format="%d.%m.%Y %H:%M %Z").dt.tz_convert(None)
            #The end of timeframes may be 00:00 of the next day witch is not correctly represented in timestamps
            df["bis"] = df["bis"].where(df["bis"].dt.time != dt.time(0,0), df["bis"] + dt.timedelta(days=1))
            df = df.drop(["datum", "zeitzone"], axis=1).set_index("von")
        return df

    def _basic_read_vermarktung(self, resource_url, earliest_data, dt_begin: dt.datetime | None = None, dt_end: dt.datetime | None = None, transform_dates = False):
        """
        Internal method to read data in the format of most /vermarktung dataseries.
        Target format is: Dates separated in "datum", "von", "bis", "zeitzone".
        Return a pandas Dataframe with data of the endpoint specified with resource_url.
        If either dt_begin or dt_end is None, all available data will be queried.

            resource_url -- url of the endpoint without the base url and without leading or trailing "/"
            earliest_data -- first datapoint in the source collection
            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        url = f"{_API_BASE_URL}/{resource_url}"
        if((dt_begin != None) and (dt_end != None)):
            start_of_data = dt_begin.strftime(_api_date_format)
            start_of_data = start_of_data if start_of_data > earliest_data else earliest_data
            end_of_data = dt_end.strftime(_api_date_format)
            url = f"{_API_BASE_URL}/{resource_url}/{start_of_data}/{end_of_data}"

        response = requests.get(url, headers = {'Authorization': 'Bearer {}'.format(self.token)})
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text),
            sep=";",
            header=0,
            decimal=",",
            na_values=["N.A."]
            )

        if(transform_dates):    
            df["von"] = pd.to_datetime(df["Datum"] + " " + df["von"] + " " + df["Zeitzone von"], format=_csv_date_format, utc=True)
            df["bis"] = pd.to_datetime(df["Datum"] + " " + df["bis"] + " " + df["Zeitzone bis"], format=_csv_date_format, utc=True)
            #The end of timeframes may be 00:00 of the next day witch is not correctly represented in timestamps
            df["bis"] = df["bis"].where(df["bis"].dt.time != dt.time(0,0), df["bis"] + dt.timedelta(days=1))
            df = df.drop(["Datum", "Zeitzone von", "Zeitzone bis"], axis=1).set_index("von")

        return df

    def _basic_read_systemdienstleistungen(self, resource_url, earliest_data, dt_begin: dt.datetime | None = None, dt_end: dt.datetime | None = None, transform_dates=False):
        """
        Internal method to read data in the format of most 'systemdienstleistungen' dataseries.
        Target format is: Dates separated in "BEGINN_DATUM", "BEGINN_UHRZEIT", "ENDE_DATUM",
        "ENDE_UHRZEIT", "ZEITZONE_VON", "ZEITZONE_BIS".
        Return a pandas Dataframe with data of the endpoint specified with resource_url.
        If either dt_begin or dt_end is None, all available data will be queried.

            resource_url -- url of the endpoint without the base url and without leading or trailing "/"
            earliest_data -- first datapoint in the source collection
            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "BEGINN" and "ENDE" that contain fully qualified timestamps. (default: False)
        """
        url = f"{_API_BASE_URL}/data/{resource_url}"
        if((dt_begin != None) and (dt_end != None)):
            start_of_data = dt_begin.strftime(_api_date_format)
            start_of_data = start_of_data if start_of_data > earliest_data else earliest_data
            end_of_data = dt_end.strftime(_api_date_format)
            url = f"{_API_BASE_URL}/data/{resource_url}/{start_of_data}/{end_of_data}"

        response = requests.get(url, headers = {'Authorization': 'Bearer {}'.format(self.token)})
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text),
            sep=";",
            header=0,
            decimal=",",
            na_values=["N.A."],
            )

        if(transform_dates):    
            df["BEGINN"] = pd.to_datetime(
                df["BEGINN_DATUM"] + " " + df["BEGINN_UHRZEIT"] + " " + df["ZEITZONE_VON"],
                format="%d.%m.%Y %H:%M %Z",
                utc=True,
            ).dt.tz_localize(None)
            df["ENDE"] = pd.to_datetime(
                df["ENDE_DATUM"] + " " + df["ENDE_UHRZEIT"] + " " + df["ZEITZONE_BIS"],
                format="%d.%m.%Y %H:%M %Z",
                utc=True,
            ).dt.tz_localize(None)
            df = df.drop(
                [
                    "BEGINN_DATUM",
                    "BEGINN_UHRZEIT",
                    "ENDE_DATUM",
                    "ENDE_UHRZEIT",
                    "ZEITZONE_VON",
                    "ZEITZONE_BIS",
                ],
                axis=1,
            )

        return df

    def hochrechnung_solar(self, dt_begin: dt.datetime | None = None, dt_end: dt.datetime | None = None, transform_dates=False):
        """
        Return a pandas Dataframe with data of the endpoint /hochrechnung/Solar.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        return self._basic_read_nt("data/hochrechnung/Solar", "2011-03-31T22:00:00", dt_begin, dt_end, transform_dates)

    def hochrechnung_wind(self, dt_begin: dt.datetime | None = None, dt_end: dt.datetime | None = None, transform_dates=False):
        """
        Return a pandas Dataframe with data of the endpoint /hochrechnung/Wind.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        return self._basic_read_nt("data/hochrechnung/Wind", "2011-03-31T22:00:00", dt_begin, dt_end, transform_dates)

    def online_hochrechnung_windonshore(self, dt_begin: dt.datetime | None = None, dt_end: dt.datetime | None = None, transform_dates=False):
        """
        Return a pandas Dataframe with data of the endpoint /OnlineHochrechnung/Windonshore.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        return self._basic_read_nt("data/OnlineHochrechnung/Windonshore", "2011-12-31T23:00:00", dt_begin, dt_end, transform_dates)

    def online_hochrechnung_windoffshore(self, dt_begin: dt.datetime | None = None, dt_end: dt.datetime | None = None, transform_dates=False):
        """
        Return a pandas Dataframe with data of the endpoint /OnlineHochrechnung/Windoffshore.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        return self._basic_read_nt("data/OnlineHochrechnung/Windoffshore", "2011-12-31T23:00:00", dt_begin, dt_end, transform_dates)

    def online_hochrechnung_solar(self, dt_begin: dt.datetime | None = None, dt_end: dt.datetime | None = None, transform_dates=False):
        """
        Return a pandas Dataframe with data of the endpoint /OnlineHochrechnung/Solar.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        return self._basic_read_nt("data/OnlineHochrechnung/Solar", "2011-12-31T23:00:00", dt_begin, dt_end, transform_dates)

    def vermarktung_differenz_einspeiseprognose(self, dt_begin: dt.datetime | None = None, dt_end: dt.datetime | None = None, transform_dates=False):
        """
        Return a pandas Dataframe with data of the endpoint /vermarktung/DifferenzEinspeiseprognose.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        return self._basic_read_vermarktung("data/vermarktung/DifferenzEinspeiseprognose", "2011-04-01T00:00:00", dt_begin, dt_end, transform_dates)

    def vermarktung_inanspruchnahme_ausgleichsenergie(self, dt_begin: dt.datetime | None = None, dt_end: dt.datetime | None = None, transform_dates=False):
        """
        Return a pandas Dataframe with data of the endpoint /vermarktung/InanspruchnahmeAusgleichsenergie.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        return self._basic_read_vermarktung("data/vermarktung/InanspruchnahmeAusgleichsenergie", "2011-04-01T00:00:00", dt_begin, dt_end, transform_dates)

    def vermarktung_untertaegige_strommengen(self, dt_begin: dt.datetime | None = None, dt_end: dt.datetime | None = None, transform_dates=False):
        """
        Return a pandas Dataframe with data of the endpoint /vermarktung/DifferenzEinspeiseprognose.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        return self._basic_read_vermarktung("data/vermarktung/DifferenzEinspeiseprognose", "2011-04-01T00:00:00", dt_begin, dt_end, transform_dates)
    
    def redispatch(self, dt_begin: dt.datetime | None = None, dt_end: dt.datetime | None = None, transform_dates=False):
        """
        Return a pandas Dataframe with data of the endpoint /redispatch.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2021-10-01T00:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "BEGINN" and "ENDE" that contain fully qualified timestamps. (default: False)
        """
        return self._basic_read_systemdienstleistungen("redispatch", "2021-10-01T00:00:00", dt_begin, dt_end, transform_dates)
    
    def prognose_solar(self, dt_begin: dt.datetime | None = None, dt_end: dt.datetime | None = None, transform_dates=False):
        """
        Return a pandas Dataframe with data of the endpoint /prognose/Solar.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC (no values after: 2022-12-15T00:00:00)
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        url = f"{_API_BASE_URL}/data/prognose/Solar/"
        if((dt_begin != None) and (dt_end != None)):
            #Prognose Solar contains historical data, adapt dates to the relevant timeframe
            start_of_data = dt_begin.strftime(_api_date_format)
            start_of_data = start_of_data if start_of_data > "2011-03-31T22:00:00" else "2011-03-31T22:00:00"
            end_of_data = dt_end.strftime(_api_date_format)
            end_of_data = end_of_data if end_of_data < "2022-12-15T00:00:00" else "2022-12-15T00:00:00"
            url = f"{_API_BASE_URL}/data/prognose/Solar/{start_of_data}/{end_of_data}"

        response = requests.get(url, headers = {'Authorization': 'Bearer {}'.format(self.token)})
        df = pd.read_csv(io.StringIO(response.text),
            sep=";",
            header=0,
            decimal=",",
            thousands=".",
            na_values=["N.A."]
            )
        
        if(transform_dates):    
            df["von"] = pd.to_datetime(df["Datum"] + " " + df["von"] + " " + df["Zeitzone von"], format=_csv_date_format, utc=True)
            df["bis"] = pd.to_datetime(df["Datum"] + " " + df["bis"] + " " + df["Zeitzone bis"], format=_csv_date_format, utc=True)
            df = df.drop(["Datum", "Zeitzone von", "Zeitzone bis"], axis=1).set_index("von")

        return df

    def prognose_wind(self, dt_begin: dt.datetime | None = None, dt_end: dt.datetime | None = None, transform_dates=False):
        """
        Return a pandas Dataframe with data of the endpoint /prognose/Wind.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC (no values after: 2022-12-15T00:00:00)
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        url = f"{_API_BASE_URL}/data/prognose/Wind"
        if((dt_begin != None) and (dt_end != None)):
            #Prognose Wind contains historical data, adapt dates to the relevant timeframe
            start_of_data = dt_begin.strftime(_api_date_format)
            start_of_data = start_of_data if start_of_data > "2011-03-31T22:00:00" else "2011-03-31T22:00:00"
            end_of_data = dt_end.strftime(_api_date_format)
            end_of_data = end_of_data if end_of_data < "2022-12-15T00:00:00" else "2022-12-15T00:00:00"
            url = f"{_API_BASE_URL}/data/prognose/Wind/{start_of_data}/{end_of_data}"

        response = requests.get(url, headers = {'Authorization': 'Bearer {}'.format(self.token)})
        df = pd.read_csv(io.StringIO(response.text),
            sep=";",
            header=0,
            decimal=",",
            thousands=".",
            na_values=["N.A."]
            )
        
        if(transform_dates):    
            df["von"] = pd.to_datetime(df["Datum"] + " " + df["von"] + " " + df["Zeitzone von"], format=_csv_date_format, utc=True)
            df["bis"] = pd.to_datetime(df["Datum"] + " " + df["bis"] + " " + df["Zeitzone bis"], format=_csv_date_format, utc=True)
            df = df.drop(["Datum", "Zeitzone von", "Zeitzone bis"], axis=1).set_index("von")

        return df