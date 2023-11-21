from ytmusicapi import YTMusic
import json
import re
ytmusic = YTMusic("oauth.json")

stolen_tracks_lists = []
playlist_name = ""


## Playlist info
playlist_list = ytmusic.get_library_playlists()

albumNames = ["fearless", "speakNow", "red", "nineteenEightyNine"]
tvAlbums = {
    "fearless": ["OLAK5uy_mGRDKgRDJtrpyw25zrYD7Rl56ACL1Oiy8"],
    "speakNow": ["OLAK5uy_ne0DpedKNeKeFyjQ86_6DJHyCGCjqHOv8"],
    "red": ["OLAK5uy_l1Em5x2MlWyFc1w_7ayxQc6qVLVUbhaME"],
    "nineteenEightyNine": ["OLAK5uy_ncKvykObOe16WxrmZEAlCbWBRZm2Utaqk", "OLAK5uy_lvlz2hg23jGszL0Jaa9Wy9TE_XNnfMijM"]
}
stolenAlbums = {
    "fearless": ["OLAK5uy_muzVJZB508O6Pn7hAnKLX-0FhxVFC9Z9M", "OLAK5uy_lZdZBuYMGZcc5AJZmJeGN-390ORcsEtJU", "OLAK5uy_k9QEkm7Med3kLvYpQVSJXb_kSKyBOi8BE"],
    "speakNow": ["OLAK5uy_mDY0SYhu9rF7RdxJNVsJHTxSeKhD6DxVQ", "OLAK5uy_ma7jNM1HuRvhHdcqHGtyYWuB_r-_hqN-c"],
    "red": ["OLAK5uy_ks84GLjEXPo9_C4dbTmyX99z5W0gwzFIk", "OLAK5uy_mnq56DGqyvOiaqJtjHxlksOHOJhKRCseU"],
    "nineteenEightyNine": ["OLAK5uy_n8mGmmk-aCPt9QQ9dOLQAHj0fDa7bBuLA", "OLAK5uy_mWbyIY5FoCOlKwTI9xXLoRXzv3VpoYv_g", "OLAK5uy_knugp3pcdtuz6Oil8vBHX9V5PkpVCnnK0"]
}
albumDict = {album: {"tvAlbums": tvAlbums[album], "stolenAlbums": stolenAlbums[album]} for album in albumNames}

#### Functions
def getTrackNames(albumDict):
    albumsDict = {}

    for albumName in albumDict:
        albumsDict[albumName] = {}

        # Combined processing for both TV and stolen albums
        for albumType in ["tvAlbums", "stolenAlbums"]:
            for albumId in albumDict[albumName][albumType]:
                search_results = ytmusic.get_album_browse_id(albumId)
                albumData = ytmusic.get_album(search_results)

                for track in albumData["tracks"]:
                    trackTitle = track["title"]

                    # Skip tracks with "Voice Memo" or "Commentary"
                    if "Voice Memo" in trackTitle or "Commentary" in trackTitle:
                        continue

                    if "From The Vault" not in trackTitle:
                        # Clean and standardize the track title
                        trackTitle = " ".join(re.findall(r"[a-zA-Z0-9\(\)\&]+", trackTitle))
                        trackTitle = trackTitle.replace(" (Taylor s Version)", "").strip()

                        # Initialize dictionary for the track if it does not exist
                        if trackTitle not in albumsDict[albumName]:
                            albumsDict[albumName][trackTitle] = {"stolenVideoIds": [], "tvVideoId": None}

                        # Assign video ID based on album type
                        videoIdKey = "tvVideoId" if albumType == "tvAlbums" else "stolenVideoIds"
                        videoIdList = albumsDict[albumName][trackTitle][videoIdKey]
                        if isinstance(videoIdList, list):
                            videoIdList.append(track["videoId"])
                        else:
                            albumsDict[albumName][trackTitle][videoIdKey] = track["videoId"]

    return albumsDict

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
            if track["videoId"] in trackMap:
                if "setVideoId" in track:
                    print(playlist["title"])
                    setVideoId = track["setVideoId"]
                    print(setVideoId)
  
                    stolenId = track["videoId"]
                    # replace_track(stolenId, trackMap[stolenId], setVideoId, playlistId)

def main():
    fullAlbumDict = getTrackNames(albumDict)
    for album in fullAlbumDict.keys():
        for track in fullAlbumDict[album].keys():
            stolenVideoIds = fullAlbumDict[album][track]["stolenVideoIds"]
            tvId = fullAlbumDict[album][track]["tvVideoId"]
            if stolenVideoIds != [] and tvId != "":
                search_playlist(stolenVideoIds)
                # print(track)
                # print(stolenVideoIds)
                # print(tvId)


#### End Functions

main()

