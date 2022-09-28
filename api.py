from fastapi import FastAPI
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
from urllib.parse import unquote
import re
from httpx import Client, Timeout

app = FastAPI()
app.state.client = Client(timeout=Timeout(60))


@app.get("/stop/{stop_id}")
def get_stop(stop_id: int):
    """Fetches a stop's ID"""
    stop_id = str(stop_id)
    if not stop_id.startswith("450"):
        stop_id = "450" + stop_id
    url = "http://deps.at?%s" % stop_id
    response = app.state.client.get(
        url,
        follow_redirects=True
    )
    if response.status_code == 200:
        response = app.state.client.get(
            "http://publicwyca.rslepi.co.uk/departureboards/mEPIDepartureBoard.aspx?id={0}&cid=595".format(stop_id)
        )
    soup = BeautifulSoup(response.text, "html.parser")
    departures = soup.find_all("div", {"class": "deprow"})
    parsed_url = unquote(str(response.url))
    try:
        share = re.search(r"shareURL=(http://deps\.at/\?\d+)", parsed_url).group(1)
    except AttributeError:
        if response.history:
            share = str(response.history[-1].url)
        else:
            share = str(response.url)
    result = {
        "url": share
    }
    for departure in departures:
        # print(departure.prettify())
        bus_name = departure.find(id="serviceDiv").get_text(strip=True)
        values = {
            "stand": "stand",
            "destination": "destination",
            "due": "time"
        }
        result[bus_name] = {
            "name": bus_name,
            "stand": "Unknown",
            "destination": "Unknown",
            "time": "Unknown",
        }
        for key, value in values.items():
            _result = departure.find(id=key + "Div")
            if _result is not None:
                result[bus_name][value] = _result.get_text(strip=True)

    return JSONResponse(
        result,
        200,
        headers={
            "Cache-Control": "max-age=60, public",
        },
    )


# @app.get("/nearby-stops")
# async def nearby_stops(postcode: str):
#     """Fetches local stops to the provided postcode"""
#     url = "https://connect.wyca.vix-its.com/Text/PostcodeResults.aspx"
#     response = app.state.client.get(url, params={"search": postcode})
#     soup = BeautifulSoup(response.text, "html.parser")
#     nearby = {}
#     try:
#         for entry in soup.body.div.table.find_all("tr")[2:]:
#             # Example:
#             # <tr>
#             # <td class="body-cell">96</td><td class="body-cell">45013308</td><td class="body-cell">
#             # <a href="WebDisplay.aspx?stopRef=45013308&amp;stopName=Valley+Mount" id="GridViewPostcodeResults_HyperLink1_0" title="View departure board">Valley Mount</a>
#             # </td><td class="body-cell-contains-nested-table">
#             # <div>
#             # <table border="1" cellspacing="0" class="postcodeResultsInnerGridBodyTable" id="GridViewPostcodeResults_InnerGridView_0" rules="all">
#             # <tr>
#             # <td class="body-cell-nested-table-cell body-cell-nested-table-not-last-column">174, 175</td><td class="body-cell-nested-table-cell">Garforth</td>
#             # </tr>
#             # </table>
#             # </div>
#             # </td>
#             # </tr>
#             datas = entry.find_all("td")
#             try:
#                 distance_metres, stop_id, stop_name, _, services, destination = datas
#             except ValueError:
#                 continue
#             nearby[stop_id.get_text(strip=True)] = {
#                 "id": stop_id.get_text(strip=True),
#                 "distance": distance_metres.get_text(strip=True),
#                 "name": stop_name.get_text(strip=True),
#                 "busses": services.get_text(strip=True),
#                 "destination": destination.get_text(strip=True),
#             }
#     except AttributeError:
#         return {"error": "No stops found or postcode is too large"}
#     return nearby


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=4280)
