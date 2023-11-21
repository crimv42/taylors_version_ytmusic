from ytmusicapi import YTMusic
import json
import re
ytmusic = YTMusic("oauth.json")

# Fearless
# TV: OLAK5uy_mGRDKgRDJtrpyw25zrYD7Rl56ACL1Oiy8
# Regular: OLAK5uy_muzVJZB508O6Pn7hAnKLX-0FhxVFC9Z9M
# Platinum Edition: OLAK5uy_lZdZBuYMGZcc5AJZmJeGN-390ORcsEtJU

# Speak Now
# TV: OLAK5uy_ne0DpedKNeKeFyjQ86_6DJHyCGCjqHOv8
# Regular: OLAK5uy_mDY0SYhu9rF7RdxJNVsJHTxSeKhD6DxVQ
# Deluxe: OLAK5uy_ma7jNM1HuRvhHdcqHGtyYWuB_r-_hqN-c

# Red
# TV: OLAK5uy_l1Em5x2MlWyFc1w_7ayxQc6qVLVUbhaME
# Regular: OLAK5uy_ks84GLjEXPo9_C4dbTmyX99z5W0gwzFIk
# BMR_Red: OLAK5uy_mnq56DGqyvOiaqJtjHxlksOHOJhKRCseU

# 1989
# TV: OLAK5uy_ncKvykObOe16WxrmZEAlCbWBRZm2Utaqk
# Regular: OLAK5uy_n8mGmmk-aCPt9QQ9dOLQAHj0fDa7bBuLA
# Deluxe: OLAK5uy_mWbyIY5FoCOlKwTI9xXLoRXzv3VpoYv_g
# BMR: OLAK5uy_knugp3pcdtuz6Oil8vBHX9V5PkpVCnnK0

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
fullAlbumDict = {album: {"tvAlbums": tvAlbums[album], "stolenAlbums": stolenAlbums[album]} for album in albumNames}


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




print(json.dumps(getTrackNames(fullAlbumDict), indent=4))
# print(json.dumps(albumDict, indent=4))