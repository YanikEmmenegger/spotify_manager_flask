import axios from "axios";
import {useCookies} from "react-cookie";
import {useEffect} from "react";


const RecentlyListened = () => {

    const [cookies] = useCookies();

    const getRecentlyListened = async () => {
        //make a axios request to http://localhost/api/user/latest
        try {
            const response = await axios.get('http://localhost/api/user/latest/', {
                headers: {
                    Authorization: cookies.refresh_token,
                    SpotifyUUID: cookies.spotify_uuid
                }
            });
            console.log(response.data)
        } catch (e) {
            console.log(e)
        }
    }

    useEffect(() => {
        getRecentlyListened()
    }, [])

    return (
        <></>
    );
}

export default RecentlyListened;