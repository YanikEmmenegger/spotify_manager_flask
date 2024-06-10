import {useCookies} from "react-cookie";
import {useEffect, useState} from "react";
import axios from "axios";

const Saver= () => {

    const [cookies] = useCookies();

    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(false)



    const startSaver = async () => {
        //make axios post request to /api/save
        //add headers with spotify_uuid and refresh_token
        //if response is 200, show success message
        //if response is 401, redirect to /login
        //if response is 500, show error message
        const headers = {
            'spotify_uuid': cookies.spotify_uuid,
            'refresh_token': cookies.refresh_token

        }

        try {
            const res = await axios.post('http://localhost/api/save/', {}, {headers: headers})
            console.log(res)
        } catch (e) {
            console.log(e)
            setError(true)

        }
        setLoading(false)
    }

    useEffect(() => {
        setLoading(true)
        startSaver()

    }, [])

    return (
        <div className='ENTER_COMPONENT_CLASS'>
            {loading ? 'Loading...' : error ? 'Error' : 'Saver'}
        </div>
    );
}

export default Saver;