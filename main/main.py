from ytmusicapi import YTMusic
import re
import subprocess
import os

# Check if oauth.json exists
oauth_json_exists = os.path.exists("oauth.json")

if not oauth_json_exists:
    # Run the auth.sh script
    auth_script_path = "./auth.sh"  # Replace with the actual path if not in the same directory
    subprocess.run(auth_script_path, shell=True)

    # Check if oauth.json was created after running the script
    oauth_json_exists_after_script = os.path.exists("oauth.json")

    if oauth_json_exists_after_script:
        ytmusic = YTMusic("oauth.json")
    else:
        print("Error: auth.sh script may not have executed successfully.")
else:
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
    "red": ["OLAK5uy_ks84GLjEXPo9_C4dbTmyX99z5W0gwzFIk", "OLAK5uy_mnq56DGqyvOiaqJtjHxlksOHOJhKRCseU", "OLAK5uy_kM-DjIbUEeP8hC3Wf1hKnW4GWQ104PhLE"],
    "nineteenEightyNine": ["OLAK5uy_n8mGmmk-aCPt9QQ9dOLQAHj0fDa7bBuLA", "OLAK5uy_mWbyIY5FoCOlKwTI9xXLoRXzv3VpoYv_g", "OLAK5uy_knugp3pcdtuz6Oil8vBHX9V5PkpVCnnK0"]
}
albumDict = {album: {"tvAlbums": tvAlbums[album], "stolenAlbums": stolenAlbums[album]} for album in albumNames}


### Songs with issues currently
# thelasttime
# everythinghaschanged
# badblood(featkendricklamar)


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
                        trackTitle = trackTitle.replace(" ", "").lower().replace("(taylorsversion)", "").replace("taylorsversion", "").replace("(originaldemorecording)", "").strip()

                        ## Songs we need to filter out
                        skipTracks = ["mine(popmix)", "ifthiswasamovie", "backtodecember(acousticversion)", "haunted(acousticversion)", "ronan"]
                        if trackTitle in skipTracks:
                            continue

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
    try:
        add_to_playlist(playlistId, tvTrackId, stolenSetVideoId)
    except:
        print("Could not add track. Probably already exists in playlist")
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

def flatten_dict(d):
    flattened_dict = {}
    for album, tracks in d.items():
        for track, data in tracks.items():
            flattened_dict[track] = data
    return flattened_dict

def search_playlist(stolenTracks, fullDict):
    # Get each playlist and list tracks on that list while checking for a match in the stolenTrackList
    for playlist in playlist_list:
        playlistId = playlist["playlistId"]
        if playlistId == "LM":
            continue
        elif any(substring in playlist["title"] for substring in ["LM", "Recap", "Mix", "Presenting"]):
            continue
        current_playlist = ytmusic.get_playlist(playlist["playlistId"])

        for track in current_playlist["tracks"]:
            if track["videoId"] in stolenTracks:
                trackVideoId = track["videoId"]
                for trackName in fullDict.keys():
                    if trackVideoId in fullDict[trackName]['stolenVideoIds']:
                        print(playlist["title"])
                        print(trackName)
                        tvVideoId = fullDict[trackName]['tvVideoId']
                        if "setVideoId" in track:
                            setVideoId = track["setVideoId"]
                        print("\n")
                        replace_track(trackVideoId, tvVideoId, setVideoId, playlistId)

def main():
    fullAlbumDict = getTrackNames(albumDict)
    songsDict = flatten_dict(fullAlbumDict)
    stolenTracks = []
    for album in fullAlbumDict.keys():
        for track in fullAlbumDict[album].keys():
            if fullAlbumDict[album][track]["stolenVideoIds"] != [] and fullAlbumDict[album][track]["tvVideoId"] is not None:
                stolenTracks.extend(fullAlbumDict[album][track]["stolenVideoIds"])
    search_playlist(stolenTracks, songsDict)            

#### End Functions

if __name__ == "__main__":
    main()

