from fastapi import FastAPI
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
from httpx import Client, Timeout

app = FastAPI()
app.state.client = Client(timeout=Timeout(60))


@app.get("/stop/{stop_id}")
def get_stop(stop_id: int):
    """Fetches a stop's ID"""
    url = "http://www.rslpublic.co.uk/mobiledepboard/WYPTEDefaultMenu.aspx"
    response = app.state.client.get(
        url,
        params={
            "id": stop_id,
            "cid": 595,
            "RTI": True,
        },
    )
    soup = BeautifulSoup(response.text, "html.parser")
    departures = soup.find_all("div", {"class": "deprow-inner"})
    result = {
        "url": str(response.url)
    }
    for departure in departures:
        children = list(filter(lambda x: x.get_text() != "\n", departure.div.children))
        bus_name = children[0].get_text(strip=True)
        result[bus_name] = {
            "name": bus_name,
            "stand": "Unknown",
            "destination": "Unknown",
            "time": "Unknown",
        }
        for child in children[1:]:
            # print(child)
            _id = child.attrs.get("id", "unknown")
            # print(_id)
            if _id.endswith("Destination"):
                result[bus_name]["destination"] = child.get_text(strip=True)
            elif _id.endswith("Stand"):
                result[bus_name]["stand"] = child.get_text(strip=True)
            elif _id.endswith("Time"):
                result[bus_name]["time"] = child.get_text(strip=True)

    return JSONResponse(
        result,
        200,
        headers={
            "Cache-Control": "max-age=300, public",
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
