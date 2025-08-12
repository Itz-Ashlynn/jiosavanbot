import asyncio
import json
from typing import Dict, Literal, Optional, Any, Union, List

import aiohttp
import aiofiles

class JioSaavnFallback:
    """
    Fallback API class for better playlist and artist support.
    """
    
    BASE_URL = "https://jiosavanwave.vercel.app"
    
    async def _request_data(self, url: str, params: Dict[str, Any] = None) -> Union[Dict[str, Any], List[Any]]:
        """Make request to fallback API"""
        import logging
        logger = logging.getLogger(__name__)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        
        logger.info(f"🔄 Fallback API Request: {url}")
        logger.info(f"📋 Parameters: {params}")
        
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url=url, params=params) as response:
                    logger.info(f"📡 Response Status: {response.status}")
                    response.raise_for_status()
                    
                    response_data = await response.json()
                    logger.info(f"✅ Fallback API Success: {response_data.get('success', False)}")
                    
                    if response_data.get('success') and response_data.get('data'):
                        logger.info(f"📊 Data keys: {list(response_data['data'].keys())}")
                        
                        # Log specific info based on data type
                        data = response_data['data']
                        if 'songs' in data:
                            logger.info(f"🎵 Songs found: {len(data.get('songs', []))}")
                        if 'topSongs' in data:
                            logger.info(f"🎵 Top songs found: {len(data.get('topSongs', []))}")
                        if 'name' in data:
                            logger.info(f"📝 Name: {data.get('name')}")
                    else:
                        logger.warning(f"⚠️ Fallback API returned unsuccessful response")
                    
                    return response_data
                    
        except Exception as e:
            logger.error(f"❌ Fallback API request failed: {e}")
            logger.error(f"🔗 Failed URL: {url}")
            logger.error(f"📋 Failed params: {params}")
            return None
    
    async def get_playlist(self, playlist_id: str, playlist_url: str = None) -> Optional[Dict[str, Any]]:
        """Get playlist from fallback API"""
        url = f"{self.BASE_URL}/api/playlists"
        
        # Try with URL first if provided, as it seems more reliable
        if playlist_url:
            params = {'link': playlist_url, 'page': 0, 'limit': 50}
            response = await self._request_data(url, params)
            if response and response.get('success'):
                return response
        
        # If playlist_id looks like a numeric ID, use it directly
        if playlist_id and playlist_id.isdigit():
            params = {'id': playlist_id, 'page': 0, 'limit': 50}
            return await self._request_data(url, params)
        
        # If not numeric and no URL, try to extract numeric ID from the alphanumeric one
        # This might need to be improved based on JioSaavn's ID format
        params = {'id': playlist_id, 'page': 0, 'limit': 50}
        return await self._request_data(url, params)
    
    async def get_album(self, album_id: str, album_url: str = None) -> Optional[Dict[str, Any]]:
        """Get album from fallback API"""
        url = f"{self.BASE_URL}/api/albums"
        
        # Try with URL first if provided, as it seems more reliable
        if album_url:
            params = {'link': album_url, 'page': 0, 'limit': 50}
            response = await self._request_data(url, params)
            if response and response.get('success'):
                return response
        
        # If album_id looks like a numeric ID, use it directly
        if album_id and album_id.isdigit():
            params = {'id': album_id, 'page': 0, 'limit': 50}
            return await self._request_data(url, params)
        
        # If not numeric and no URL, try to extract numeric ID from the alphanumeric one
        # This might need to be improved based on JioSaavn's ID format
        params = {'id': album_id, 'page': 0, 'limit': 50}
        return await self._request_data(url, params)
    
    async def get_artist_songs(self, artist_id: str, page: int = 1, song_count: int = 20, album_count: int = 10, artist_url: str = None) -> Optional[Dict[str, Any]]:
        """Get artist songs from fallback API"""
        url = f"{self.BASE_URL}/api/artists"
        
        # Try with URL first if provided, as it seems more reliable
        if artist_url:
            params = {'link': artist_url, 'page': page, 'songCount': song_count, 'albumCount': album_count, 'sortBy': 'popularity', 'sortOrder': 'desc'}
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            response = await self._request_data(url, params)
            if response and response.get('success'):
                return response
        
        # If artist_id looks like a numeric ID, use it directly
        if artist_id and artist_id.isdigit():
            params = {'id': artist_id, 'page': page, 'songCount': song_count, 'albumCount': album_count, 'sortBy': 'popularity', 'sortOrder': 'desc'}
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            return await self._request_data(url, params)
        
        # Try with the original ID anyway
        params = {'id': artist_id, 'page': page, 'songCount': song_count, 'albumCount': album_count, 'sortBy': 'popularity', 'sortOrder': 'desc'}
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request_data(url, params)
    
    async def get_song(self, song_id: str, song_url: str = None) -> Optional[Dict[str, Any]]:
        """Get song from fallback API"""
        url = f"{self.BASE_URL}/api/songs"
        
        # Try with URL first if provided, as it seems more reliable
        if song_url:
            params = {'link': song_url}
            response = await self._request_data(url, params)
            if response and response.get('success'):
                return response
        
        # Try with song ID (note: API expects 'ids' parameter)
        params = {'ids': song_id}
        return await self._request_data(url, params)


class Jiosaavn:
    """
    A class to interact with the JioSaavn API for searching and downloading songs, albums, artists, and playlists.
    """

    BASE_URL = "https://www.jiosaavn.com"
    API_URL = f"{BASE_URL}/api.php"
    
    def __init__(self):
        self.fallback = JioSaavnFallback()

    async def _request_data(
        self,
        url: str,
        params: Dict[str, Any] = None
    ) -> Union[Dict[str, Any], List[Any]]:
        """
        Makes an asynchronous GET request to the specified URL with the given parameters.

        Args:
            url (str): The URL to send the GET request to.
            params (Dict[str, Any]): The query parameters for the GET request.

        Returns:
            Union[Dict[str, Any], List[Any]]: The JSON response from the request.

        Raises:
            RuntimeError: If there is an error during the request or if the response cannot be decoded as JSON.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.jiosaavn.com/',
            'Origin': 'https://www.jiosaavn.com'
        }
        
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url=url, params=params) as response:
                    response.raise_for_status()  # Raise an exception for HTTP errors
                    response_text = await response.text()
                    
                    # Check if response is HTML (not JSON) - this handles the web interface check
                    if response_text.strip().startswith('<!DOCTYPE') or response_text.strip().startswith('<html'):
                        # Return a simple status for web interface health checks
                        return {"status": "ok", "message": "Bot web interface is running"}
                    
                    # Try to parse JSON
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        # If JSON parsing fails, check if it's likely a blocked request
                        if 'blocked' in response_text.lower() or 'forbidden' in response_text.lower():
                            raise RuntimeError("Request blocked by JioSaavn. Try again later.")
                        else:
                            # Log the response for debugging but don't expose it to user
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.debug(f"Non-JSON response from {url}: {response_text[:200]}...")
                            raise RuntimeError("JioSaavn API returned invalid response format.")
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Request to {url} failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during request to {url}: {e}")

    async def search(
        self,
        query: str,
        search_type: Literal["songs", "albums", "artists", "playlists"],
        page_no: Optional[int] = 1,
        page_size: Optional[int] = 10
    ) -> Dict[str, Any]:
        """
        Search for songs, albums, artists, or playlists.

        Args:
            query (str): The search query string.
            search_type (Literal["songs", "albums", "artists", "playlists"]): The type of search to perform.
            page_no (Optional[int]): The page number for paginated results. Defaults to 1.
            page_size (Optional[int]): The number of results per page. Defaults to 10.

        Returns:
            Dict[str, Any]: The search results from the API.

        Raises:
            ValueError: If `page_no` or `page_size` are not positive integers, or if `search_type` is invalid.
        """
        if page_no is not None and page_no < 1:
            raise ValueError("`page_no` must be a positive integer.")
        if page_size is not None and page_size < 1:
            raise ValueError("`page_size` must be a positive integer.")

        search_type_call_map = {
            "songs": "search.getResults",
            "albums": "search.getAlbumResults",
            "artists": "search.getArtistResults",
            "playlists": "search.getPlaylistResults",
        }

        call = search_type_call_map.get(search_type)
        if not call:
            raise ValueError(f"Invalid search_type: {search_type}")

        params = {
            'p': page_no,
            'q': query,
            '__call': call,
            'api_version': 4,
            'n': page_size,
            '_format': 'json',
            '_marker': 0,
            'ctx': 'web6dot0'
        }

        return await self._request_data(self.API_URL, params=params)

    async def search_all_types(
        self,
        query: str
    ) -> Dict[str, Any]:
        """
        Retrieve search results across all types, returning a limited subset due to API constraints.

        Args:
            query (str): The search query string.

        Returns:
            Dict[str, Any]: The search results from the API.
        """
        params = {
            '_format': 'json',
            '_marker': 0,
            'query': query,
            '__call': 'autocomplete.get',
            'ctx': 'web6dot0'
        }
        return await self._request_data(self.API_URL, params=params)

    async def get_artist(
        self,
        artist_id: Optional[str] = None,
        artist_name: Optional[str] = None,
        page_no: Optional[int] = 1,
        page_size: Optional[int] = 20
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves the details of an artist based on the provided ID or name.
        Since the artist details API often returns empty data, this method
        searches for songs by the artist and constructs the response.

        Args:
            artist_id (Optional[str]): The unique identifier for the artist. Defaults to None.
            artist_name (Optional[str]): The name of the artist. Defaults to None.
            page_no (Optional[int]): The page number for paginated results. Defaults to 1.
            page_size (Optional[int]): The number of results per page. Defaults to 10.

        Returns:
            Optional[Dict[str, Any]]: The details from the API or None if no response.

        Raises:
            ValueError: If `page_no` or `page_size` are not positive integers.
        """
        if page_no < 1:
            raise ValueError("`page_no` must be a positive integer.")
        if page_size < 1:
            raise ValueError("`page_size` must be a positive integer.")

        # First try to get artist details using the official API
        if artist_id:
            params = {
                '__call': 'webapi.get',
                'token': artist_id,
                'type': "artist",
                'p': page_no,
                'n_song': page_size,
                'n_album': page_size,
                'includeMetaTags': 0,
                'ctx': 'web6dot0',
                'api_version': 4,
                '_format': 'json',
                '_marker': 0
            }

            response = await self._request_data(self.API_URL, params=params)
            
            # Check if we got meaningful artist data
            if response and response.get("topSongs") and len(response["topSongs"]) > 0:
                start_index = (page_no - 1) * page_size
                end_index = page_no * page_size
                response["topSongs"] += response.get("topAlbums", [])
                response['count'] = len(response["topSongs"])
                response['topSongs'] = response["topSongs"][start_index:end_index]
                return response

        # Use fallback API directly for better artist support since it's more reliable
        if artist_id:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🎤 Using fallback API directly for artist {artist_id}")
            
            # Try to get artist URL from the response if available
            artist_url = None
            if response and response.get("perma_url"):
                artist_url = response["perma_url"]
            
            fallback_response = await self.fallback.get_artist_songs(artist_id, page_no, page_size, 10, artist_url)
            
            if fallback_response and fallback_response.get('success') and fallback_response.get('data'):
                # Convert fallback format to expected format
                artist_info = fallback_response['data']
                songs = artist_info.get('topSongs', [])
                albums = artist_info.get('topAlbums', [])
                
                # Combine songs and albums for compatibility
                all_items = songs + albums
                
                # Extract image URL properly
                image_url = ''
                if artist_info.get('image') and isinstance(artist_info['image'], list) and len(artist_info['image']) > 0:
                    # Get the highest quality image
                    image_url = artist_info['image'][-1].get('url', '')
                elif artist_info.get('image') and isinstance(artist_info['image'], str):
                    image_url = artist_info['image']
                
                artist_response = {
                    "artistId": artist_id,
                    "name": artist_info.get('name', artist_name or 'Unknown'),
                    "image": image_url,
                    "type": "artist",
                    "topSongs": all_items,  # Include both songs and albums
                    "count": len(all_items),
                    "follower_count": str(artist_info.get('followerCount', 0)),
                    "fan_count": str(artist_info.get('fanCount', 0)),
                    "is_verified": artist_info.get('isVerified', False),
                    "dominant_language": artist_info.get('dominantLanguage', ''),
                    "dominant_type": artist_info.get('dominantType', ''),
                    "bio": artist_info.get('bio', ''),
                    "dob": artist_info.get('dob', ''),
                    "urls": {
                        "songs": artist_info.get('url', f"https://www.jiosaavn.com/artist/{artist_info.get('name', '').lower().replace(' ', '-')}-songs/")
                    }
                }
                logger.info(f"✅ Fallback API returned {len(songs)} songs and {len(albums)} albums for artist {artist_info.get('name')}")
                return artist_response
            else:
                logger.warning(f"⚠️ Fallback API failed for artist {artist_id}")
                if fallback_response:
                    logger.debug(f"Fallback response: {fallback_response}")
                else:
                    logger.debug("No response from fallback API")

        # If fallback fails or no artist_id, fall back to song search
        if artist_id and not artist_name:
            # We can't search for an artist by ID easily, so return None
            logger.debug(f"Artist ID {artist_id} provided but no artist name. Cannot fetch songs.")
            return None

        if not artist_name:
            return None

        # Search for songs by this artist using original method
        search_query = f'"{artist_name}"'
        songs_response = await self.search(query=search_query, search_type="songs", page_no=page_no, page_size=page_size)
        
        if not songs_response or not songs_response.get('results'):
            return None

        # Filter songs to ensure they actually contain this artist
        artist_songs = []
        for song in songs_response['results']:
            song_artists = song.get('subtitle', '').lower()
            if artist_name.lower() in song_artists:
                artist_songs.append(song)
        
        if not artist_songs:
            return None

        # Construct artist response format
        artist_response = {
            "artistId": artist_id,
            "name": artist_name,
            "image": artist_songs[0].get('image', '').replace('150x150', '500x500') if artist_songs else '',
            "type": "artist",
            "topSongs": artist_songs,
            "count": len(artist_songs),
            "follower_count": "0",
            "urls": {
                "songs": f"https://www.jiosaavn.com/artist/{artist_name.lower().replace(' ', '-')}-songs/"
            }
        }
        
        return artist_response

    async def get_playlist_or_album(
        self,
        album_id: Optional[str] = None,
        playlist_id: Optional[str] = None,
        page_no: Optional[int] = 1,
        page_size: Optional[int] = 20,
        original_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves the details of a playlist or album based on the provided ID.

        Args:
            album_id (Optional[str]): The unique identifier for the album. Defaults to None.
            playlist_id (Optional[str]): The unique identifier for the playlist. Defaults to None.
            page_no (Optional[int]): The page number for paginated results. Defaults to 1.
            page_size (Optional[int]): The number of results per page. Defaults to 10.

        Returns:
            Optional[Dict[str, Any]]: The details from the API or None if no response or empty list for albums.

        Raises:
            ValueError: If both `album_id` and `playlist_id` are None or if `page_no` or `page_size` are not positive integers.
        """
        if page_no < 1:
            raise ValueError("`page_no` must be a positive integer.")
        if page_size < 1:
            raise ValueError("`page_size` must be a positive integer.")
        if not album_id and not playlist_id:
            raise ValueError("Either `album_id` or `playlist_id` must be provided.")

        search_type = "album" if album_id else "playlist"
        token = album_id or playlist_id

        params = {
            '__call': 'webapi.get',
            'token': token,
            'type': search_type,
            'p': page_no,
            'n': page_size,
            'includeMetaTags': 0,
            'ctx': 'web6dot0',
            'api_version': 4,
            '_format': 'json',
            '_marker': 0
        }

        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"🌐 Official API Request: {search_type} with token {token}")
        logger.info(f"📋 Official API params: {params}")
        
        response = await self._request_data(self.API_URL, params=params)
        
        if response:
            logger.info(f"✅ Official API Response received with keys: {list(response.keys())}")
        else:
            logger.warning(f"❌ Official API returned None/empty response")
        
        # For playlists and artists, use fallback API directly since it's more reliable
        # The logs show official API returns empty list even when playlist exists
        should_use_fallback = (
            not response or 
            (not response.get("list") and not response.get("songs")) or
            (response.get("list") == "" or response.get("list") == []) or
            (search_type in ["playlist", "album"] and response.get("list_count") == "0")
        )
        
        if should_use_fallback:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🔄 Official API failed for {search_type} {token}, trying fallback API...")
            logger.info(f"📋 Original response: {response}")
            
            if search_type == "playlist":
                # Try to get numeric ID from the original response if available
                numeric_id = None
                if response and response.get('id'):
                    numeric_id = response['id']
                
                # Use numeric ID if available, otherwise use token and original_url
                if numeric_id and numeric_id.isdigit():
                    logger.info(f"🔢 Using numeric ID {numeric_id} for fallback API")
                    fallback_response = await self.fallback.get_playlist(numeric_id, original_url)
                else:
                    logger.info(f"🌐 Using token {token} and URL for fallback API")
                    fallback_response = await self.fallback.get_playlist(token, original_url)
                
                if fallback_response and fallback_response.get('success') and fallback_response.get('data'):
                    # Convert fallback format to expected format
                    data = fallback_response['data']
                    songs = data.get('songs', [])
                    
                    # Extract image URL properly
                    image_url = ''
                    if data.get('image') and isinstance(data['image'], list) and len(data['image']) > 0:
                        # Get the highest quality image
                        image_url = data['image'][-1].get('url', '')
                    
                    response = {
                        "id": numeric_id or token,
                        "title": data.get('name', 'Unknown Playlist'),
                        "image": image_url,
                        "list": songs,
                        "list_count": data.get('songCount', len(songs)),
                        "perma_url": data.get('url', f"https://www.jiosaavn.com/featured/{token}"),
                        "more_info": {
                            "follower_count": 0  # Not provided in this API
                        }
                    }
                    logger.info(f"✅ Fallback API SUCCESS: Converted playlist '{data.get('name')}' with {len(songs)} songs")
                    # Return immediately after successful fallback conversion
                    return response
            
            elif search_type == "album":
                # Try to get numeric ID from the original response if available
                numeric_id = None
                if response and response.get('id'):
                    numeric_id = response['id']
                
                # Use numeric ID if available, otherwise use token and original_url
                if numeric_id and numeric_id.isdigit():
                    logger.info(f"🔢 Using numeric ID {numeric_id} for fallback API")
                    fallback_response = await self.fallback.get_album(numeric_id, original_url)
                else:
                    logger.info(f"🌐 Using token {token} and URL for fallback API")
                    fallback_response = await self.fallback.get_album(token, original_url)
                
                if fallback_response and fallback_response.get('success') and fallback_response.get('data'):
                    # Convert fallback format to expected format
                    data = fallback_response['data']
                    songs = data.get('songs', [])
                    
                    # Extract image URL properly
                    image_url = ''
                    if data.get('image') and isinstance(data['image'], list) and len(data['image']) > 0:
                        # Get the highest quality image
                        image_url = data['image'][-1].get('url', '')
                    
                    response = {
                        "id": numeric_id or token,
                        "title": data.get('name', 'Unknown Album'),
                        "image": image_url,
                        "list": songs,
                        "list_count": data.get('songCount', len(songs)),
                        "perma_url": data.get('url', f"https://www.jiosaavn.com/album/{token}"),
                        "year": data.get('releaseDate', '').split('-')[0] if data.get('releaseDate') else '',
                        "more_info": {
                            "album_url": data.get('url', f"https://www.jiosaavn.com/album/{token}")
                        }
                    }
                    logger.info(f"✅ Fallback API SUCCESS: Converted album '{data.get('name')}' with {len(songs)} songs")
                    # Return immediately after successful fallback conversion
                    return response
        
        if not response:
            return None

        # Debug logging to understand response structure
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Final response for {search_type} (token={token}): keys={list(response.keys()) if response else 'None'}")
        
        # Log more details for debugging
        if response:
            if 'list' in response:
                logger.debug(f"Response has 'list' with {len(response['list'])} items")
            if 'songs' in response:
                logger.debug(f"Response has 'songs' with {len(response['songs'])} items")
            if 'title' in response:
                logger.debug(f"Response title: {response['title']}")
            if 'error' in response:
                logger.debug(f"Response has error: {response['error']}")
        else:
            logger.debug("Response is None or empty")

        # Handle different response structures for playlists vs albums
        if search_type == "playlist":
            # Check if playlist has songs
            if not response.get("list") and not response.get("songs"):
                logger.debug("No songs found in playlist response")
                return None
            
            # Some playlists use 'songs' instead of 'list'
            if response.get("songs") and not response.get("list"):
                response["list"] = response["songs"]
                response["list_count"] = len(response["songs"])
            
            return response

        # For albums
        if not response.get("list") and not response.get("songs"):
            logger.debug("No songs found in album response")
            return None

        # Some albums use 'songs' instead of 'list'  
        if response.get("songs") and not response.get("list"):
            response["list"] = response["songs"]

        # Apply pagination
        start_index = (page_no - 1) * page_size
        end_index = page_no * page_size
        response['list'] = response["list"][start_index:end_index]
        
        # Set additional metadata
        more_info = response.get("more_info", {})
        album_url = more_info.get("album_url") or response.get("perma_url")

        if album_url:
            response["perma_url"] = album_url
            
        return response

    async def get_song(
        self,
        song_id: str
    ) -> Dict[str, Any]:
        """
        Retrieves the details of a song based on the song ID.

        Args:
            song_id (str): The unique identifier for the song.

        Returns:
            Dict[str, Any]: The song details from the API.
        """
        params = {
            '__call': 'webapi.get',
            'token': song_id,
            'type': 'song',
            'includeMetaTags': 0,
            'ctx': 'web6dot0',
            'api_version': 4,
            '_format': 'json',
            '_marker': 0
        }
        
        # Try official API first
        response = await self._request_data(self.API_URL, params=params)
        
        # If official API fails or returns empty, try fallback API
        if not response or not response.get("songs"):
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🔄 Official song API failed for {song_id}, trying fallback API...")
            
            fallback_response = await self.fallback.get_song(song_id)
            if fallback_response and fallback_response.get('success') and fallback_response.get('data'):
                # Convert fallback format to expected format
                data = fallback_response['data']
                
                # Convert to expected format - the data should be an array of songs
                if isinstance(data, list):
                    response = {"songs": data}
                else:
                    response = {"songs": [data]}
                    
                logger.info(f"✅ Fallback song API success for {song_id}")
        
        return response

    async def get_song_lyrics(
        self,
        lyrics_id: str
    ) -> Dict[str, Any]:
        """
        Retrieves the lyrics of a song based on the lyrics ID.

        Args:
            lyrics_id (str): The ID of the lyrics to retrieve.

        Returns:
            Dict[str, Any]: The lyrics details from the API.

        Raises:
            ValueError: If the lyrics ID is invalid or the lyrics could not be retrieved.
        """
        params = {
            '__call': 'lyrics.getLyrics',
            'lyrics_id': lyrics_id,
            'type': 'song',
            'includeMetaTags': 0,
            'ctx': 'web6dot0',
            'api_version': 4,
            '_format': 'json',
            '_marker': 0
        }
        try:
            response = await self._request_data(self.API_URL, params=params)
            if not response:
                raise ValueError("No response received from the API.")
            return response
        except Exception as e:
            raise ValueError(f"Failed to retrieve lyrics for ID {lyrics_id}: {e}")

    async def get_download_url(
        self,
        song_id: str,
        bitrate: Literal[160, 320]
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves the download URL for a song based on the song ID and bitrate.

        Args:
            song_id (str): The unique identifier for the song.
            bitrate (Literal[160, 320]): The desired bitrate for the download.

        Returns:
            Optional[Dict[str, Any]]: The download data containing the URL or None if not found.
        """
        song_response = await self.get_song(song_id=song_id)
        if song_response:
            encrypted_media_url = song_response.get("songs", [])[0].get("more_info", {}).get("encrypted_media_url")
            params = {
                "__call": 'song.generateAuthToken',
                "url": encrypted_media_url,
                "bitrate": bitrate,
                "api_version": 4,
                "_format": "json",
                "ctx": "wap6dot0",
                "_marker": 0
            }
            return await self._request_data(url=self.API_URL, params=params)
        return None

    async def download_song(
        self,
        song_id: str,
        bitrate: Literal[160, 320],
        download_location: str
    ) -> None:
        """
        Downloads a song based on the song ID and bitrate.

        Args:
            song_id (str): The unique identifier for the song.
            bitrate (Literal[160, 320]): The desired bitrate for the download.
            download_location (str): The file path where the song will be saved.

        Raises:
            ValueError: If the song download URL cannot be retrieved.
        """
        download_data = await self.get_download_url(song_id=song_id, bitrate=bitrate)
        if not download_data or not download_data.get("auth_url"):
            raise ValueError("Unable to retrieve the download URL for the song.")

        url = download_data["auth_url"]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.jiosaavn.com/',
            'Origin': 'https://www.jiosaavn.com',
            'Sec-Fetch-Dest': 'audio',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"'
        }

        # Retry logic for downloads
        max_retries = 3
        for attempt in range(max_retries):
            try:
                timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes timeout
                async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                    async with session.get(url) as response:
                        response.raise_for_status()
                        async with aiofiles.open(download_location, "wb") as file:
                            while True:
                                chunk = await response.content.read(4 * 1024 * 1024)  # 4 MB chunk size
                                if not chunk:
                                    break
                                await file.write(chunk)
                break  # Success, exit retry loop
            except aiohttp.ClientError as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise ValueError(f"Failed to download song after {max_retries} attempts: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        return download_location
