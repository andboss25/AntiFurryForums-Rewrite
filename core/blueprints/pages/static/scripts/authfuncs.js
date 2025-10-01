async function login(){
    if (document.getElementById('policy').checked != true) {
        document.getElementById("error").style.color = 'red';
        document.getElementById("error").innerHTML = 'Please agree to the privacy policy'
        return;
    }
    let username = document.getElementById("username").value
    let password = document.getElementById("password").value

    let resp = await fetch("/api/user/login",{
            body: JSON.stringify({ username: username, password: password}),
            method: "POST",
            headers: {
            "Content-Type": "application/json",
        },
    })

    let parsed_resp = await resp.json()
    
    if ('error' in parsed_resp) {
        document.getElementById("error").style.color = 'red';
        document.getElementById("error").innerHTML = parsed_resp['error']
    } else if ('token' in parsed_resp) {
        document.getElementById("error").style.color = 'green';
        document.getElementById("error").innerHTML = 'Signed into account!'
        localStorage.setItem('token',parsed_resp['token'])
    }
    
}

async function signup(){
    if (document.getElementById('policy').checked != true) {
        document.getElementById("error").style.color = 'red';
        document.getElementById("error").innerHTML = 'Please agree to the privacy policy'
        return;
    }
    let username = document.getElementById("username").value
    let password = document.getElementById("password").value

    let resp = await fetch("/api/user/signup",{
            body: JSON.stringify({ username: username, password: password}),
            method: "POST",
            headers: {
            "Content-Type": "application/json",
        },
    })

    let parsed_resp = await resp.json()
    
    if ('error' in parsed_resp) {
        document.getElementById("error").style.color = 'red';
        document.getElementById("error").innerHTML = parsed_resp['error']
    } else if ('token' in parsed_resp) {
        document.getElementById("error").style.color = 'green';
        document.getElementById("error").innerHTML = 'Created account!'
        localStorage.setItem('token',parsed_resp['token'])
    }
    
}