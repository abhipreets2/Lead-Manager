import React from "react";

import { UserContext } from "../context/UserContext";

const Register = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmationPassword, setConfirmationPassword] = useState("");
    const [errorMessage, setErrorMessage] = useState("");
    const [, setToken] = useContext(UserContext);

    const submitRegistration = async () => {
        const requestOptions = {
            method : "POST",
            headers : {"Content-Type" : "application/json"},
            body : JSON.stringify({email : email, hashed_password : password}),
        };

        const response = await fetch("/api/users", requestOptions);
        const data = response.json();
        if(!response.ok){
            setErrorMessage(data.detail);
        }
        else{
            setToken(data.access_token);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if(password == confirmationPassword && password.length > 5) {
            submitRegistration();
        }
        else{
            setErrorMessage("Ensure the passwords match and greater than 5 characters");
        };

    };

};