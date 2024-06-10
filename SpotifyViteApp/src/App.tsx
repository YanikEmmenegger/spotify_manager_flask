import {BrowserRouter as Router, Routes, Route} from 'react-router-dom'
import Home from './pages/Home'
import  {useEffect, useState} from "react";
import {useCookies} from "react-cookie";

function App() {

    //get cookies from browser refresh_token and spotify_uuid
    //if cookies are present, redirect to home page
    //if cookies are not present, redirect to login page
    const [cookies] = useCookies();

    const [loading, setLoading] = useState(true)


    useEffect(() => {
        setLoading(true)
        console.log(cookies)

        if (cookies.spotify_uuid === undefined || cookies.spotify_uuid === "" || cookies.refresh_token === undefined || cookies.refresh_token === "") {

            //if page is not /login redirect to /login
            window.location.href = 'http://localhost/api/auth'

        }
        setLoading(false)

    }, [cookies])

    if (loading) {
        return (
            <div>
                Loading...
            </div>
        )
    }

    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home/>}/>
            </Routes>
        </Router>
    )
}

export default App