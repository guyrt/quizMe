import React, {useCallback, useEffect} from "react";
import { createRoot } from 'react-dom/client';

import {
    createMemoryRouter,
    RouterProvider
    , useNavigate
} from "react-router-dom";

import SignIn from "./optionsManagement/signin";
import { sharedState } from "./stateTrackers/sharedState";
import { LoggedInUserSettings } from "./optionsManagement/loggedInUserSettings";
import { SignUp } from "./optionsManagement/signup";


const optionsRouter = createMemoryRouter([
    {
        path: '/',
        element: <RedirectRouter />
    },
    {
        path: '/signin',
        element: <SignIn doNav={true} handleSignUp={() => {}} handleSignedIn={() => {}} />
    },
    {
        path: '/signup',
        element: <SignUp doNav={true} handleSignedUp={() => {}}/>
    },
    {
        path: '/user',
        element: <LoggedInUserSettings />
    }
]);

/// Redirect router. Loads first. Main job is to contain "loading" content and sort out
/// logged in or logged out landing.
function RedirectRouter() {

    const navigate = useNavigate();

    const resolveRoute = useCallback(async() => {
        const token = await sharedState.getApiToken();
        if (token === undefined) {
            // no token - load sign in.
            console.log("Signin page");
            navigate("/signin");
            
        } else {
            // token - load user view.
            console.log("User stats");
            navigate("/user");
        }
    }, []);

    useEffect(() => {
        console.log('Redirect init.');
        resolveRoute();
    }, [resolveRoute]);

    return (
        <div>Hang tight...</div>
    );
}

document.addEventListener('DOMContentLoaded', () => {
    // Render your React component instead
    const a = document.getElementById('app');
    if (a != null) {
        const root = createRoot(a);
        root.render(
            <React.StrictMode>
                <RouterProvider router={optionsRouter} />
            </React.StrictMode>
        );
    }
});
