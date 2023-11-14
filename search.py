from ytmusicapi import YTMusic
import json
ytmusic = YTMusic("oauth.json")

# search_results = ytmusic.search("Taylor Swift 1989")
albumNames = ["fearless", "speakNow", "red", "1989"]
fullAlbumDict = {album: {"tvAlbums": [], "stolenAlbums": []} for album in albumNames}


# Fearless
# TV: OLAK5uy_mGRDKgRDJtrpyw25zrYD7Rl56ACL1Oiy8
# Regular: OLAK5uy_muzVJZB508O6Pn7hAnKLX-0FhxVFC9Z9M
# Platinum Edition: OLAK5uy_lZdZBuYMGZcc5AJZmJeGN-390ORcsEtJU

# Speak Now

# Red

# 1989

search_results = ytmusic.get_album_browse_id("OLAK5uy_mGRDKgRDJtrpyw25zrYD7Rl56ACL1Oiy8")

fearless_stolen_albums = []


def getTrackNames(search_results):
    album = ytmusic.get_album(search_results)
    albumsDict = {}
    for trackNum in range(len(album["tracks"])):
        trackTitle = (album["tracks"][trackNum]["title"])
        tvVideoId = (album["tracks"][trackNum]["videoId"])
    
        if "[From The Vault]" not in trackTitle: 
            albumsDict[trackTitle] = {}
            albumsDict[trackTitle]["stolenVideoIds"] = []
            albumsDict[trackTitle]["tvVideoId"] = tvVideoId
    return albumsDict

# albumDict = {item: {} for item in getTrackNames(search_results)}
# print(json.dumps(getTrackNames(search_results), indent=4))

albumDict = getTrackNames(search_results)
for trackName in albumDict.keys():
    stolenTrackName = trackName.replace(" (Taylor’s Version)", "").strip()
    
    for album in fearless_stolen_albums:
        album = ytmusic.get_album(album)
        for trackNum in range(len(album["tracks"])):
            if stolenTrackName.lower() == album["tracks"][trackNum]["title"].lower():
                albumDict[trackName]["stolenVideoIds"].append(album["tracks"][trackNum]["videoId"])

print(json.dumps(albumDict, indent=4))
                

# print(json.dumps(fearless["tracks"], indent=4))
# Taylor Swift channel ID = UCqECaJ8Gagnn7YCbPEzWH6g
# get_playlists = ytmusic.get_library_playlists()
# album_info = ytmusic.get_artist("UCqECaJ8Gagnn7YCbPEzWH6g")
# album_list = ytmusic.get_artist_albums("UCqECaJ8Gagnn7YCbPEzWH6g", params="ggMIegYIARoCAQI%3D")