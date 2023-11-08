from ytmusicapi import YTMusic
import json
ytmusic = YTMusic("oauth.json")

stolen_tracks_lists = []
playlist_name = ""

# Map Structure {"track_name": ["stolenId", "tvId"]}
map_fearless = {}
map_red = {}
map_speakNow = {}
map_1989 = {}

#### Get Album Info

# 1989 TV Info
# 1989 TV Album ID = MPREb_5XXbjpMgJar
tv_1989 = ytmusic.get_album("MPREb_ROOaFgqZpLS")
# print_1989_tv = json.dumps(tv_1989, indent = 4)  
# print(print_1989_tv)

# 1989 Stolen Info
# 1989 Stolen Album ID = MPREb_riIJjrsqo2I
stolen_1989 = ytmusic.get_album("MPREb_riIJjrsqo2I")
# print_1989_stolen = json.dumps(stolen_1989, indent = 4)  
# print(print_1989_stolen)

#### End Get Album Info

## Playlist info
playlist_list = ytmusic.get_library_playlists()


#### Functions
def map_maker(albumMap, stolen, tv):
    # mapName = ("map_" + albumName)
    stolenTracks = ytmusic.get_album(stolen)
    tvTracks = ytmusic.get_album(tv)
    for trackNum in range(len(stolenTracks["tracks"])):
        trackName = stolenTracks["tracks"][trackNum]["title"]
        if not "(Voice Memo)" in trackName and trackName in tvTracks["tracks"][trackNum]["title"]:
            stolenId = stolenTracks["tracks"][trackNum]["videoId"]
            albumMap[stolenId] = tvTracks["tracks"][trackNum]["videoId"]

def replace_track(stolenTrackId, tvTrackId, stolenSetVideoId, playlistId):
    trackInfo = ytmusic.get_song(stolenTrackId)
    trackName = trackInfo["videoDetails"]["title"]

    print("Replacing " + trackName + ":\nOld ID: " + stolenTrackId + "\nNew Id: " + tvTrackId)
    add_to_playlist(playlistId, tvTrackId, stolenSetVideoId)
    removeFromPlaylist(stolenTrackId, stolenSetVideoId, playlistId)

def add_to_playlist(playlist, tvTrackId, stolenSetVideoId):
    tvIdList = []
    tvIdList.append(tvTrackId)
    addTrackInfo = ytmusic.add_playlist_items(playlistId=playlist, videoIds=tvIdList)
    tvSetVideoId = addTrackInfo["playlistEditResults"][0]["setVideoId"]
    ytmusic.edit_playlist(playlistId=playlist, moveItem=(tvSetVideoId, stolenSetVideoId))    

def removeFromPlaylist(stolenTrackId, stolenSetVideoId, playlistId):
    stolenIdList = []
    stolenIdList.append({})
    stolenIdList[0]["videoId"] = stolenTrackId
    stolenIdList[0]["setVideoId"] = stolenSetVideoId
    ytmusic.remove_playlist_items(playlistId=playlistId, videos=stolenIdList)

def search_playlist(trackMap):
    # Get each playlist and list tracks on that list while checking for a match in the stolenTrackList
    for playlist in playlist_list:
        playlistId = playlist["playlistId"]
        if playlistId == "LM":
            continue
        current_playlist = ytmusic.get_playlist(playlist["playlistId"])

        for track in current_playlist["tracks"]:
            if track["videoId"] in trackMap.keys():
                if "setVideoId" in track:
                    print(playlist["title"])
                    setVideoId = track["setVideoId"]
                    print(setVideoId)
  
                    stolenId = track["videoId"]
                    replace_track(stolenId, trackMap[stolenId], setVideoId, playlistId)

def main():
    map_maker(map_1989, "MPREb_riIJjrsqo2I", "MPREb_ROOaFgqZpLS")
    search_playlist(map_1989)

#### End Functions

main()

